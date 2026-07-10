"""
Entity identity resolution -- decides whether an incoming record refers to
an entity already in the graph, before any write happens.

Traces to: GRAPH/SCHEMA.md's Entity Identity section: "when ingestion
encounters an entity already present under a different source ID, it
resolves to the existing canonical node and appends the xref -- it does
not create a duplicate. Unresolvable ambiguity (two sources disagreeing on
whether two records are the same entity) is itself recorded as a
research_hypothesis-tier relationship (xerdna:possibly_same_as) rather
than silently merged or silently dropped." Also Anti-Hallucination Rule 5
(no silent fuzzy merging -- below a defined certainty threshold, the
system records xerdna:possibly_same_as as a hypothesis, never a merge).

Matching is exact-string-equality on (namespace, external_id) pairs only
-- no normalization, no similarity scoring, no fuzzy logic of any kind
(explicit Milestone 005 scope boundary).

This module performs read-only lookups directly (SELECT queries, no
writes) and otherwise writes exclusively through GRAPH.engine.gate.
Callers ingesting a record that might already exist under a different
source identifier MUST use resolve_or_create_node() here, not
gate.insert_node() directly -- calling gate.insert_node() directly bypasses
identity resolution entirely and risks exactly the silent duplication this
module exists to prevent.
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import date

from GRAPH.engine import gate

POSSIBLY_SAME_AS_PREDICATE = "xerdna:possibly_same_as"


class AmbiguousIdentityError(Exception):
    """
    Raised when an incoming record's xrefs match two or more DIFFERENT
    existing canonical nodes -- GRAPH/SCHEMA.md's "unresolvable ambiguity"
    case. Nothing is written when this is raised: no new node, no
    appended xref, no automatic merge. Carries the conflicting xerdna_ids
    so a caller can choose to record the ambiguity explicitly via
    record_possibly_same_as() -- a separate, deliberate call, never
    triggered automatically by this exception alone.
    """

    def __init__(self, matched_xerdna_ids: frozenset[str], attempted_xrefs: list[tuple[str, str]]):
        self.matched_xerdna_ids = matched_xerdna_ids
        self.attempted_xrefs = attempted_xrefs
        super().__init__(
            f"ambiguous identity: incoming record's xrefs {attempted_xrefs} match "
            f"{len(matched_xerdna_ids)} distinct existing nodes {sorted(matched_xerdna_ids)} -- "
            f"refusing to guess which one it is (or isn't)"
        )


@dataclass
class IdentityResolution:
    outcome: str  # "created" | "resolved_existing"
    xerdna_id: str
    xrefs_appended: list[tuple[str, str]] = field(default_factory=list)


def find_matching_xerdna_ids(conn: sqlite3.Connection, xrefs: list[tuple[str, str]]) -> frozenset[str]:
    """
    Exact-match-only lookup: which existing xerdna_ids already carry any
    of the given (namespace, external_id) pairs. No fuzzy matching, no
    normalization -- literal string equality via SQL, nothing more.
    """
    matched: set[str] = set()
    for namespace, external_id in xrefs:
        rows = conn.execute(
            "SELECT DISTINCT xerdna_id FROM node_xrefs WHERE namespace = ? AND external_id = ?",
            (namespace, external_id),
        ).fetchall()
        matched.update(row[0] for row in rows)
    return frozenset(matched)


def resolve_or_create_node(conn: sqlite3.Connection, node_kwargs: dict) -> IdentityResolution:
    """
    The main entry point. node_kwargs is exactly what gate.insert_node()
    accepts (must include a non-empty "xrefs" list -- resolution has
    nothing to match against otherwise).

    - Zero existing nodes match any incoming xref -> mint a new node via
      gate.insert_node(), using the caller's proposed xerdna_id. Outcome
      "created".
    - Exactly one existing node matches (via any overlapping xref) -> do
      NOT create a new node, even if the caller's proposed xerdna_id
      differs. Append any of the incoming xrefs not already present on
      that node via gate.add_xref(). Outcome "resolved_existing".
    - Two or more DISTINCT existing nodes match different xrefs within the
      same incoming record -> raise AmbiguousIdentityError. Nothing is
      written.
    """
    xrefs = node_kwargs.get("xrefs") or []
    if not xrefs:
        raise ValueError("resolve_or_create_node requires node_kwargs['xrefs'] to be non-empty")

    matched = find_matching_xerdna_ids(conn, xrefs)

    if not matched:
        gate.insert_node(conn, **node_kwargs)
        return IdentityResolution(outcome="created", xerdna_id=node_kwargs["xerdna_id"], xrefs_appended=[])

    if len(matched) > 1:
        raise AmbiguousIdentityError(matched, xrefs)

    (existing_xerdna_id,) = matched
    existing_xrefs = {
        (row[0], row[1])
        for row in conn.execute(
            "SELECT namespace, external_id FROM node_xrefs WHERE xerdna_id = ?", (existing_xerdna_id,)
        ).fetchall()
    }
    appended = []
    for namespace, external_id in xrefs:
        if (namespace, external_id) not in existing_xrefs:
            gate.add_xref(conn, xerdna_id=existing_xerdna_id, namespace=namespace, external_id=external_id)
            appended.append((namespace, external_id))

    return IdentityResolution(outcome="resolved_existing", xerdna_id=existing_xerdna_id, xrefs_appended=appended)


def _ensure_possibly_same_as_registered(conn: sqlite3.Connection) -> None:
    """Self-registers xerdna:possibly_same_as (B4) before first use -- mirrors ingest.py's own pattern (Milestone 003)."""
    conn.execute(
        """
        INSERT OR IGNORE INTO xerdna_namespace_registry (prefix, kind, parent_type, introduced_in, rationale)
        VALUES ('possibly_same_as', 'predicate', NULL, 'GRAPH/SCHEMA.md',
                'Entity Identity section -- unresolvable ambiguity recorded as a hypothesis, never a silent merge')
        """
    )
    conn.commit()


def record_possibly_same_as(
    conn: sqlite3.Connection,
    *,
    xerdna_id_a: str,
    xerdna_id_b: str,
    reason: str,
    generated_by: str = "xerdna-identity-resolver",
) -> int:
    """
    Explicitly record unresolvable ambiguity as a research_hypothesis-tier
    xerdna:possibly_same_as association -- never called automatically by
    AmbiguousIdentityError; a caller decides, separately, whether to record
    it. GRAPH/SCHEMA.md Entity Identity section; Anti-Hallucination Rule 5.
    """
    _ensure_possibly_same_as_registered(conn)
    return gate.insert_hypothesis(
        conn,
        subject_id=xerdna_id_a,
        object_id=xerdna_id_b,
        predicate=POSSIBLY_SAME_AS_PREDICATE,
        primary_knowledge_source="infores:xerdna-identity-resolver",
        source_record_id=f"AMBIGUITY:{xerdna_id_a}:{xerdna_id_b}",
        retrieved_at=date.today().isoformat(),
        claim=f"{xerdna_id_a} and {xerdna_id_b} may be the same entity",
        supporting_evidence=reason,
        reasoning=(
            f"Identity resolution found overlapping xrefs suggesting {xerdna_id_a} and {xerdna_id_b} "
            f"could refer to the same real-world entity, but the match was not exact/exclusive enough "
            f"to resolve automatically -- recorded for human review, not merged (Anti-Hallucination Rule 5)."
        ),
        generated_by=generated_by,
        confidence_basis="xref overlap detected but insufficient to resolve without ambiguity",
        none_found_as_of=date.today().isoformat(),
    )
