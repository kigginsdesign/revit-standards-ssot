# Decision Packet — Deprecation Batch 1

| Field | Value |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-05-01 |
| **Author** | Max (Claude Code agent) on behalf of Sage |
| **Authorized by** | Sage |
| **Source export** | `exports/raw/20260430_220917.json` |
| **Records affected** | 37 (32 + 4 + 1) |
| **DB mutations** | None yet — awaiting Sage confirmation to apply |

---

## Purpose

Remove obvious non-parameter garbage from the active curation set before any
promotion work begins. These records are confirmed placeholder artifacts, developer
test parameters, or vendor-imported non-names that cannot become approved firm
standards without a source name change. They are not deleted; they are deprecated
with a recorded reason so the evidence is preserved.

This packet covers three independent batches that can be applied together or
separately.

---

## Batch A — "Identity Data" placeholder names (32 records)

### Rationale

Thirty-two records have the literal name `"Identity Data"`, `data_type = "Text"`,
`group = "Other"`. `"Identity Data"` is a Revit built-in parameter group name, not a
parameter name. These records appear to be placeholder slots from a shared parameter
file template or vendor-supplied family library where the name was never filled in.
They are not promotable as-is. No parameter named `"Identity Data"` should appear in
approved firm vocabulary.

### Dry-run verification

Command:
```
uv run python scripts/ingest/bulk_curate.py --name-exact "Identity Data"
```

Observed output:
```
Matched records: 32
... (20-record preview, all status=raw, all data_type=Text, all group=Other)
Dry-run mode. No changes made. Pass --apply to commit.
```

### Matching criteria

| Filter | Value |
|---|---|
| `--name-exact` | `Identity Data` |

All 32 matched records have identical `data_type = "Text"` and `group = "Other"`.
No false positives are expected; no other record in the database has this exact name.

### Proposed `curation_note`

```
Placeholder parameter name — "Identity Data" is a Revit group name, not a
valid parameter name. Batch 1 deprecation, 2026-05-01.
```

### Apply command (do not run without Sage authorization)

```
uv run python scripts/ingest/bulk_curate.py \
    --name-exact "Identity Data" \
    --curation-note "Placeholder parameter name — \"Identity Data\" is a Revit group name, not a valid parameter name. Batch 1 deprecation, 2026-05-01." \
    --apply
```

---

## Batch B — Novotny temp parameters (4 records)

### Rationale

Four records have names prefixed with `"Novotny temp parameter"`. `"Novotny"` is a
vendor/author surname appearing in a shared parameter file likely inherited from a
third party. The `"temp"` in the names is explicit — these are acknowledged test
parameters not intended for production. They appear in `group = "Constraints"`.

| GUID | Name | data_type | group |
|---|---|---|---|
| `2277e231-d93d-4b24-8965-e872d177ea2b` | Novotny temp parameter Integer | Integer | Constraints |
| `75dde55a-e5e5-4bbe-bf60-b6764d6868e9` | Novotny temp parameter Integer | Integer | Constraints |
| `8f404da0-0373-4226-861d-fbd5c3ce5225` | Novotny temp parameter Angle | Angle | Constraints |
| `bb51632f-ca09-491b-874c-90e5e02c0089` | Novotny temp parameter Length | Length | Constraints |

Note: two records share the name `"Novotny temp parameter Integer"` with different GUIDs.
Both are deprecated together.

### Dry-run verification

Command:
```
uv run python scripts/ingest/bulk_curate.py --name-contains "Novotny"
```

Observed output:
```
Matched records: 4
... (4-record preview, all status=raw)
Dry-run mode. No changes made. Pass --apply to commit.
```

### Matching criteria

| Filter | Value |
|---|---|
| `--name-contains` | `Novotny` |

The substring `"Novotny"` does not appear in any other parameter name in the database.
No false positives are expected.

### Proposed `curation_note`

```
Developer/vendor test parameter — "Novotny temp parameter" prefix indicates a
third-party or personal test artifact not intended for firm standards.
Batch 1 deprecation, 2026-05-01.
```

### Apply command (do not run without Sage authorization)

```
uv run python scripts/ingest/bulk_curate.py \
    --name-contains "Novotny" \
    --curation-note "Developer/vendor test parameter — \"Novotny temp parameter\" prefix indicates a third-party or personal test artifact not intended for firm standards. Batch 1 deprecation, 2026-05-01." \
    --apply
```

---

## Batch C — ParameterTest (1 record)

### Rationale

One record is named `"ParameterTest"`, `data_type = "Text"`, `group = "Text"`.
Both the name and the group (`"Text"` is a data_type value, not a Revit group name)
indicate a test artifact. The name is explicit about its purpose.

| GUID | Name | data_type | group |
|---|---|---|---|
| `2316b029-250d-4b1d-9ca1-7cb9bfd925d8` | ParameterTest | Text | Text |

### Dry-run verification

Command:
```
uv run python scripts/ingest/bulk_curate.py --name-exact "ParameterTest"
```

Observed output:
```
Matched records: 1
... (1-record preview, status=raw)
Dry-run mode. No changes made. Pass --apply to commit.
```

### Matching criteria

| Filter | Value |
|---|---|
| `--name-exact` | `ParameterTest` |

### Proposed `curation_note`

```
Explicit test artifact — parameter name "ParameterTest" indicates a non-production
test record. group="Text" also anomalous. Batch 1 deprecation, 2026-05-01.
```

### Apply command (do not run without Sage authorization)

```
uv run python scripts/ingest/bulk_curate.py \
    --name-exact "ParameterTest" \
    --curation-note "Explicit test artifact — parameter name \"ParameterTest\" indicates a non-production test record. group=\"Text\" also anomalous. Batch 1 deprecation, 2026-05-01." \
    --apply
```

---

## Combined totals

| Batch | Filter | Matched | Status after apply |
|---|---|---|---|
| A — Identity Data | `--name-exact "Identity Data"` | 32 | deprecated |
| B — Novotny temp | `--name-contains "Novotny"` | 4 | deprecated |
| C — ParameterTest | `--name-exact "ParameterTest"` | 1 | deprecated |
| **Total** | | **37** | |

Post-apply DB state (expected): 806 total, 769 raw, 37 deprecated, 0 proposed, 0 approved.

---

## Deferred — not in this batch

The following anomalies are **not** included in Batch 1 because they require additional
Sage decisions:

- **`group = "Text"` on 16 records** — Structural correction needed; some records may
  be salvageable with a group fix. Requires Sage decision on each record.
- **`Phase` × 2 with `data_type = "Number of Poles"`** — Source authoring error.
  Requires a decision on correct `data_type` before deprecating or retaining.
- **Reinforcement Length single-letter cluster (12 records: K, B, O, …)** — Pending
  decision on inherited structural content.
- **Hand-authored GUID records (23 records, patterns A/B/C)** — Pending GUID stability
  confirmation.
- **Duplicate-name clusters** — Require canonical GUID selection before deprecating
  the non-canonical copies.
- **`Test Data` (1 record), `TAG 1/2/3`, `B2–B5`** — Unclear intent; deferred pending
  Sage guidance.

---

## Open questions before apply

1. **Sage authorization** — Are the three batches above approved as stated?
2. **Curation note text** — Are the proposed `curation_note` strings acceptable, or
   should they be revised?
3. **Sequential vs combined apply** — Should the three batches be applied as one
   combined run or three separate `--apply` calls (one per batch)?
4. **Decision packet update** — After apply, this document should be updated to
   `Status: Applied` with the actual apply timestamp and final counts.
