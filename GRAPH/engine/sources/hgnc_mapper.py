"""
Maps a raw HGNC JSON record into GRAPH.engine.gate.insert_node() keyword
arguments, and validates it before it ever reaches the gate.

Traces to: DOCS/PHASE_002_DESIGN.md Section 4.1 (nodes), 4.2 (node_xrefs);
GRAPH/SCHEMA.md's Entity Identity section (the exact xref pattern used
below -- HGNC/NCBIGene/Ensembl -- is that section's own worked example).

No network access, no SQL, no gate.py calls. Pure data transformation and
validation -- this module reads a dict and returns a dict, nothing more.

--------------------------------------------------------------------------
FIELD MAPPING (every field, documented explicitly, per Milestone 004's
own requirement)
--------------------------------------------------------------------------

| HGNC JSON field         | XERDNA field                | Transformation                                          |
|--------------------------|------------------------------|----------------------------------------------------------|
| hgnc_id ("HGNC:1100")    | xerdna_id                   | "HGNC:1100" -> "xerdna:gene:hgnc-1100" (strip prefix,     |
|                          |                              | lowercase, namespaced)                                    |
| hgnc_id                  | source_record_id            | verbatim ("HGNC:1100")                                    |
| hgnc_id                  | xrefs entry                 | ("HGNC", "1100") -- numeric part only                     |
| entrez_id (if present)   | xrefs entry                 | ("NCBIGene", entrez_id)                                   |
| ensembl_gene_id (if present) | xrefs entry              | ("Ensembl", ensembl_gene_id)                              |
| uniprot_ids[0] (if present)  | xrefs entry              | ("UniProt", uniprot_ids[0]) -- first accession only        |
| (fixed)                  | category                    | "biolink:Gene"                                             |
| (fixed)                  | evidence_tier                | "established_evidence"                                     |
| (fixed)                  | primary_knowledge_source     | "infores:hgnc"                                             |
| fixture's fetched_at      | retrieved_at                 | verbatim, passed in by the caller (not by this module)     |
| (fixed)                  | schema_version                | config.SUPPORTED_SCHEMA_VERSION                            |
| status                   | (validation only)             | must equal "Approved" or the record is rejected            |
| symbol                   | (validation only)             | must be present or the record is rejected                  |

NOT MAPPED -- a known, reported gap, not a silent omission:
  symbol, name, locus_type, and every other descriptive/human-readable
  field HGNC provides have no destination. PHASE_002_DESIGN.md Section 4.1's
  `nodes` table has no label/name/symbol column at all -- this is a design
  gap (see this milestone's closing summary), not an implementation choice.
  This mapper does not invent a place to put them; it simply does not map
  them, the same discipline this project applied to the
  aggregator_knowledge_source gap.
--------------------------------------------------------------------------
"""

from GRAPH.engine import config


class SourceRecordInvalid(ValueError):
    """
    Raised when a raw HGNC record fails validation *before* it would even
    be attempted through the gate -- distinct from gate.GateValidationError,
    which is raised by XERDNA's own rules once a well-formed record reaches
    the Insertion Gate. A SourceRecordInvalid record never reaches the gate
    at all.
    """


def validate_hgnc_record(record: dict) -> None:
    """Raises SourceRecordInvalid if the record is incomplete or unusable. Returns None otherwise."""
    if not record.get("hgnc_id"):
        raise SourceRecordInvalid("record is missing hgnc_id -- cannot mint a canonical ID or source_record_id")
    if not record.get("symbol"):
        raise SourceRecordInvalid(f"record {record.get('hgnc_id')!r} is missing symbol")
    if record.get("status") != "Approved":
        raise SourceRecordInvalid(
            f"record {record.get('hgnc_id')!r} has status {record.get('status')!r}, not 'Approved' -- "
            f"not ingested as an established gene record"
        )


def map_hgnc_record_to_node_kwargs(record: dict, retrieved_at: str) -> dict:
    """
    Validate and map one raw HGNC record into GRAPH.engine.gate.insert_node()
    keyword arguments. Raises SourceRecordInvalid if the record fails
    validation -- callers should catch this separately from
    gate.GateValidationError (see GRAPH/engine/sources/hgnc_ingest.py).
    """
    validate_hgnc_record(record)

    hgnc_id = record["hgnc_id"]  # e.g. "HGNC:1100"
    numeric_id = hgnc_id.split(":", 1)[1]

    xrefs = [("HGNC", numeric_id)]
    if record.get("entrez_id"):
        xrefs.append(("NCBIGene", record["entrez_id"]))
    if record.get("ensembl_gene_id"):
        xrefs.append(("Ensembl", record["ensembl_gene_id"]))
    uniprot_ids = record.get("uniprot_ids") or []
    if uniprot_ids:
        xrefs.append(("UniProt", uniprot_ids[0]))

    return {
        "xerdna_id": f"xerdna:gene:hgnc-{numeric_id}",
        "category": "biolink:Gene",
        "evidence_tier": "established_evidence",
        "primary_knowledge_source": "infores:hgnc",
        "source_record_id": hgnc_id,
        "retrieved_at": retrieved_at,
        "schema_version": config.SUPPORTED_SCHEMA_VERSION,
        "xrefs": xrefs,
    }
