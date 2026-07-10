# MILESTONE 001 COMPLETION

**Status:** Governance record, not implementation. This document records the completion and validation of Engineering Milestone 001 — the first code ever written in XERDNA's history. It does not modify PHASE_002_DESIGN.md, GRAPH/SCHEMA.md, or any other governance document. Per MASTER_CONTEXT.md Article XII, this is a Validation-stage record (stage 9), following Implementation (stage 8), for the scope approved in DOCS/PHASE_002_DESIGN.md v1.2.

**Traces to:** DOCS/PHASE_002_DESIGN.md (v1.2), DOCS/IMPLEMENTATION_POLICY.md, DOCS/PHASE_001_FREEZE.md.

---

## Scope

Milestone 001's goal, as approved: **create the absolute minimum local Universal Biological Memory Engine foundation** — local only, Python, SQLite, zero external services, zero networking, zero AI, zero ingestion, no frontend, no web application. Seven deliverables were authorized: project structure, database initialization, schema creation, configuration, validation framework, logging, and versioning.

**Explicitly not in scope, and not built:** Section 5 of the design (The Insertion Gate) — no application-layer insertion API, no immutability triggers, no `promoted_from`/`resolved_by` tier-restriction checks, no cross-table business rules (e.g., "confidence forbidden if `established_evidence`"). This boundary was stated in the Milestone 001 implementation plan before any code was written and held throughout — every enforcement mechanism this milestone contains is a single-row SQLite constraint (`NOT NULL`, `CHECK`, foreign key), nothing more.

## Implementation Summary

Six tasks were completed, each traced to a specific section of DOCS/PHASE_002_DESIGN.md:

1. **Project structure** — `GRAPH/engine/` established as the code location (per TG1's resolution), with a `tests/` subpackage and a `.gitignore` excluding generated data.
2. **Configuration** — `config.py` defines `ENGINE_VERSION = "0.1.0"`, `SUPPORTED_SCHEMA_VERSION = "1.2"`, `MIN_PYTHON_VERSION = (3, 10)`, and path constants (Section 9).
3. **Logging** — `logging_setup.py`, local file + stdout only, no network-capable handler anywhere in the module.
4. **Schema creation** — `schema.sql`, all 9 tables from Section 4 (`nodes`, `node_xrefs`, `associations`, `confidence`, `hypotheses`, `predictions`, `checked_absent`, `entity_lineage`, `xerdna_namespace_registry`) as idempotent (`IF NOT EXISTS`) DDL, with every `NOT NULL`, tier/status/enum `CHECK`, and foreign-key constraint the design specifies at the single-row level, including the two same-row `CHECK`s expressible without cross-table logic (hypothesis `contradicting_evidence`/`none_found_as_of`; prediction `method_ontology_term`/`ontology_gap`).
5. **Database initialization** — `db.py`, exposing `connect()` (sets `PRAGMA foreign_keys = ON` on every connection, per Section 3, with no other code path opening a connection) and `init_db()` (idempotent, applies `schema.sql`, logs the result). A `check_python_version()` guard enforces the `>= 3.10` requirement at runtime rather than merely documenting it.
6. **Validation framework** — `tests/test_milestone_001.py`, using only the standard library's `unittest` (no new dependency introduced, including for testing).

One additional file, `GRAPH/__init__.py`, was added to make `GRAPH` itself an importable package — a prerequisite for `GRAPH.engine` imports to resolve reliably, not a scope expansion.

## Validation Summary

**18 of 18 tests pass, zero failures, zero errors, zero warnings** (confirmed twice: once under normal execution, once under `-W error::ResourceWarning` to force any resource-handling defect to fail loudly rather than pass silently).

Coverage by category:
- **Project structure** (2 tests): package importability, expected files present.
- **Configuration** (3 tests): `ENGINE_VERSION`, `SUPPORTED_SCHEMA_VERSION`, `MIN_PYTHON_VERSION` each match the design exactly.
- **Logging** (2 tests): writes to a local file only; no network-capable handler is ever attached.
- **Database initialization** (4 tests): file creation, all 9 tables present, `PRAGMA foreign_keys` reads back `1`, `init_db()` is safely re-callable.
- **Single-row constraint enforcement** (7 tests): a valid node insert succeeds; an invalid `evidence_tier` is rejected by SQLite itself; a missing required field is rejected; an invalid `status` value is rejected; `checked_absent` genuinely has no `evidence_tier` column (schema introspection, not just documentation); a valid `checked_absent` insert succeeds; a foreign-key violation is rejected.

One test-quality defect was found and fixed during validation, not left in: `test_writes_to_local_file_only` left a file handle open across a handler-reset, producing a `ResourceWarning`. Closing the handler before clearing it resolved this — a small but real instance of the same discipline this project has applied throughout (catch it now, don't ship it with a known, un-investigated warning).

## Files Created

```
GRAPH/__init__.py
GRAPH/engine/__init__.py
GRAPH/engine/.gitignore
GRAPH/engine/config.py
GRAPH/engine/logging_setup.py
GRAPH/engine/schema.sql
GRAPH/engine/db.py
GRAPH/engine/tests/__init__.py
GRAPH/engine/tests/test_milestone_001.py
```

No existing file was modified. `GRAPH/engine/data/` (holding the generated `.db` and `.log` files at runtime) is excluded from git via `GRAPH/engine/.gitignore` and was left empty at milestone close — nothing generated during validation was left behind.

## Python Environment Used

The design requires Python ≥ 3.10 (WVS4, Section 3). The system's default `python3` resolved to **3.9.6**, below this requirement. `/opt/homebrew/bin/python3.11` (**Python 3.11.15**) was located and used for all implementation and validation work instead. `db.py`'s `check_python_version()` enforces this requirement at runtime — the engine raises `RuntimeError` rather than running silently under an unsupported interpreter, so this constraint is mechanically guaranteed going forward, not just a note for whoever runs it next. **Action needed outside this document's scope:** whichever environment runs Milestone 002 and beyond needs `python3.11` (or newer) available, ideally on `PATH`, since the default `python3` on this machine does not satisfy the design's own minimum.

## Constitutional Compliance

- **VISION.md Article IX (Scientific Constitution Before Code):** held throughout — no code was written until DOCS/PHASE_002_DESIGN.md reached `READY FOR IMPLEMENTATION` via the full Architecture → Review → Decision → Remediation → engineering-readiness-review cycle (MASTER_CONTEXT.md Article XII).
- **MASTER_CONTEXT.md Article II Rule 1 (three-tier evidence model):** the `evidence_tier` `CHECK` constraint on `nodes` and `associations` is the first piece of code in XERDNA's history mechanically enforcing this rule — validated directly (an invalid tier is rejected by SQLite itself, not merely by convention).
- **MASTER_CONTEXT.md Article V Rule 2 (provenance is mandatory):** `primary_knowledge_source` and `source_record_id` are `NOT NULL` on both tiered tables; validated by test.
- **GRAPH/SCHEMA.md's Checked-Absent Records exemption (v1.2):** mechanically confirmed, not just asserted — `checked_absent` has no `evidence_tier` column, verified by schema introspection (`PRAGMA table_info`) in the test suite, the strongest form of proof available short of the gate logic itself.
- **VISION.md Article VII (Ethical Principles):** unaffected — this milestone contains no individual-level data and no capability of any kind beyond local schema/storage plumbing, consistent with the non-applicability finding already recorded in PHASE_002_DESIGN.md (CC1).

## Implementation Policy Compliance

Checked against DOCS/IMPLEMENTATION_POLICY.md's ten sections, to the extent each applies at this milestone's scope:

- **Section 1 (Implementation Principles):** built only from an already-approved, traced design; no scope silently expanded (Section 5 was named out of scope before coding began and stayed out).
- **Section 2 (Documentation Requirements):** every file's module docstring cites the specific PHASE_002_DESIGN.md section it implements.
- **Section 3 (Architectural Traceability):** the schema.sql header and per-table comments trace each table back to its Section 4 subsection; the design gap noted below was recorded rather than silently resolved.
- **Section 6 (Testing Requirements):** every constraint this milestone actually implements has a corresponding test; no untested enforcement claim exists at this milestone's scope.
- **Section 7 (Scientific Verification Requirements):** not separately exercised this milestone — no ontology or database metadata was introduced (no seed data was inserted as part of Milestone 001 itself; the one seed-shaped row used by a test is a synthetic fixture, not a scientific claim).
- **Sections 4, 5, 8, 9, 10** (Review independence, Validation records, Rollback, Versioning, Deprecation): Section 9 (Versioning) is directly addressed — `ENGINE_VERSION`/`SUPPORTED_SCHEMA_VERSION` exist and are tested. Sections 5, 8, and 10 are not yet load-bearing at this milestone's scope (nothing has shipped to roll back or deprecate yet); Section 4's independent-review caveat carries forward unchanged from PHASE_002_REVIEW.md's own stated limitation.

## Known Limitations

- **No enforcement beyond single-row SQLite constraints.** Cross-table rules — the immutability triggers, the `promoted_from`/`resolved_by` tier-restriction lookups, "no confidence row if `established_evidence`" — exist in the design but not yet in code. A direct SQL `INSERT` bypassing the (not-yet-built) application gate could currently create a record that violates one of these rules; only Milestone 002 closes this.
- **No seed data.** Section 7 of the design (the illustrative seed set exercising every rule end-to-end, including the newly-added `resolved_by` pathway) is not part of this milestone and does not yet exist in the database.
- **Default `python3` on this machine is below the design's minimum**, as noted above — an environmental fact to carry forward, not a code defect.
- **Local-only by design, not yet exercised at any real scale** — this milestone's own tests use small, synthetic fixtures; nothing here demonstrates behavior at the scale a real (even prototype-sized) dataset would exercise.

## Design Gap: `aggregator_knowledge_source`

GRAPH/SCHEMA.md's Provenance Model states every node *and edge* carries `aggregator_knowledge_source`. PHASE_002_DESIGN.md Section 4.3's `associations` field list, however, only names `primary_knowledge_source`, `source_record_id`, `retrieved_at`, `status`, and `schema_version` — `aggregator_knowledge_source` is absent from that row, even though it is present on `nodes` (Section 4.1).

This milestone implemented the approved design exactly as written: `schema.sql`'s `associations` table has no `aggregator_knowledge_source` column, with a comment recording the omission and pointing back to this note. This was flagged, not silently corrected, at implementation time (in the Milestone 001 implementation plan) and is repeated here for the permanent record. **This is a PHASE_002_DESIGN.md gap, not an implementation defect** — closing it requires a design-level correction (a small addition to Section 4.3, analogous to the WVS1-style fixes already applied in v1.1/v1.2), which should go through the same Review → Decision → Remediation discipline as every other design correction in this project, not be patched directly in code.

## Lessons Learned

- **A design that reads as complete can still hide an untested cross-table gap.** The Provenance Model's `aggregator_knowledge_source` omission in Section 4.3 survived two full Review/Decision/Remediation cycles (v1.1, v1.2) and a final engineering-readiness review before surfacing — only became visible when translating the design into literal DDL forced a field-by-field, table-by-table comparison against GRAPH/SCHEMA.md itself, not just against PHASE_002_DESIGN.md's own internal consistency. This suggests future design reviews should include an explicit cross-check against GRAPH/SCHEMA.md's own model sections, not only against the design document's internal coherence.
- **Environment assumptions need verification, not just specification.** The design correctly pinned a minimum Python version (WVS4), but the actual host environment didn't meet it — caught only by attempting the build, not by any earlier review stage (none of which run code). This is a category of gap document review cannot catch by construction; it reinforces why IMPLEMENTATION_POLICY.md Section 5 (Validation) exists as a distinct stage from Review.
- **Runtime constraint enforcement is a stronger proof than design text, and cheap to obtain early.** Confirming `checked_absent` has no `evidence_tier` column via `PRAGMA table_info` (not just by reading the schema.sql source) is a materially stronger validation than the equivalent design-stage claim — worth carrying forward as a validation pattern: wherever a design claims "X is absent/impossible," the corresponding test should demonstrate that absence structurally, not just assert the intended behavior.
- **Separating "schema creation" from "the insertion gate" as two milestones was the right call.** It kept Milestone 001 genuinely small and fully testable on its own terms (18 tests, all meaningful, none speculative about not-yet-built logic), and it makes Milestone 002's scope unambiguous before any of its code is written.

## Readiness for Milestone 002

Milestone 001 provides a validated foundation — a correctly-structured, constraint-enforcing local database and the configuration/logging/versioning scaffolding around it — for Milestone 002 to build **Section 5, The Insertion Gate**, on top of. Before Milestone 002 begins, per this project's own standing discipline, it should have its own implementation plan (smallest possible tasks, per-task validation) the same way Milestone 001 did; nothing in this document authorizes skipping that step. Two items should be carried into Milestone 002's own planning, not treated as already resolved:

1. The `aggregator_knowledge_source` design gap, above — ideally closed at the design level before or alongside Milestone 002's gate logic touches `associations` provenance handling.
2. The Python environment note, above — Milestone 002's own environment should be confirmed against `MIN_PYTHON_VERSION` before work begins, not rediscovered mid-implementation.

No further action is taken here. Stopping after this document, per instruction.
