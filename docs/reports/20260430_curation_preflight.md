# Curation Preflight Report — First Ingest

**Report date:** 2026-05-01  
**Source export:** `exports/raw/20260430_220917.json`  
**Runtime DB:** `/workspace/db/standards.db`  
**Review CSV:** `outputs/review_20260430_220917.csv`  
**Auditor:** Max (Claude Code agent)

> **Updated 2026-05-01:** The Curation Workbench model has been formalized. Two new
> nullable columns have been added to `shared_parameters`: `curation_note` (Text) and
> `standard_data_type` (String). All existing ingest records have `NULL` for both fields.
> Bulk deprecation is now performed via `scripts/ingest/bulk_curate.py`, which requires a
> non-blank `--curation-note` on every `--apply` run. See `PROJECT_MEMORY.md` for the
> two-tier validation model.

---

## A. Executive Summary

| Metric | Value |
|---|---|
| Total records | 806 |
| Status: `raw` | 806 |
| Status: `proposed` | 0 |
| Status: `approved` | 0 |
| Status: `deprecated` | 0 |

**Recommended next action:** Resolve the source-authoring anomalies described in Section D before promoting any records. A small tracer-bullet set of 15 candidates is identified in Section G for a first `proposed` pass once anomalies are cleared, but no records should be promoted until Shawn/Sage has reviewed and decided on each item in Section H.

**Correction to prior audit:** The earlier report identified 8 zero-padded GUIDs. Broader analysis finds **23 hand-authored GUIDs** across three distinct patterns. See Section D.

---

## B. Review Buckets

These buckets are approximations. Many records could belong to more than one; the intent is to guide human review sequencing, not to create a final taxonomy.

| Bucket | Est. Count | Notes |
|---|---|---|
| Architectural / door / window / glazing | ~200 | Frame, panel, glass, sash, hardware parameters. Large, likely firm-maintained core. |
| Identity / manufacturer metadata | ~45 | Copyright, manufacturer contact, product data, IFC classification. Mix of firm and vendor-template origin. |
| MEP (mechanical, electrical, plumbing) | ~79 | Identified by group (`Mechanical`, `Electrical`, etc.) or MEP data_types. Mostly unknown data_types — review before promotion. |
| Structural / reinforcement | ~92 | `Structural` group plus 12 single-letter `Reinforcement Length` records. Likely inherited. |
| Green building / energy analysis | ~35 | LEED, Energy Star, R-Value, thermal properties. Mix of firm and inherited. |
| IFC Parameters | 18 | Masterformat, Uniclass, Uniformat, BIMobject. External classification schemes. |
| Family type parameters | 5 | `Family type: Casework/Doors/Generic Models/Specialty Equipment`. Unusual data_type pattern. |
| Hand-authored GUID records | 23 | All three GUID patterns listed in Section D. Flag before promotion. |
| Placeholder / test / vendor artifacts | ~40 | "Identity Data" name (32), Novotny temp parameters (4), ParameterTest, Test Data, B2–B5. |
| Unclassified | remainder | Parameters not clearly in another bucket; standard types and groups. |

---

## C. Duplicate and Conflict Analysis

### Summary

| Issue | Count |
|---|---|
| Names appearing more than once | 82 |
| Names with multiple data_types | 13 |
| Names with multiple groups | 19 |
| Same name, same dtype, same group (true duplicates) | 59 names / 130+ records |
| Same GUID appearing more than once | 0 |

No duplicate GUIDs. All 806 GUIDs are unique.

### Notable conflict cases

**`Phase` × 2 — wrong data_type (source-authoring error)**  
Both records are `data_type = "Number of Poles"`, `group = "Electrical"`.
A parameter named `Phase` should almost certainly have `data_type = "Text"` or `"Integer"`.
The `Number of Poles` data_type on a parameter named `Phase` is a strong signal of source-file authoring error.

| GUID | Name | data_type | group |
|---|---|---|---|
| `697795fb-88ee-4cc9-93e4-e363ae8be74b` | Phase | Number of Poles | Electrical |
| `87ea06de-740f-40d8-9c8a-fdffd71e5e4c` | Phase | Number of Poles | Electrical |

**`SHGC` × 2 — conflicting data_types**  
One record has `data_type = "Number"` (physically correct for a dimensionless ratio);
the other has `data_type = "Text"`. They also have different GUIDs.

| GUID | Name | data_type | group |
|---|---|---|---|
| `08000000-0000-0000-0000-000000000003` | SHGC | Number | Energy Analysis |
| `09f1de2d-268b-46df-8d9d-7546a90225df` | SHGC | Text | Other |

Note: the first GUID is hand-authored (see Section D).

**`Copyright` × 4 — same dtype/group, different GUIDs**  
All four are `Text / Identity Data`. One has a hand-authored GUID (`...0001`).

| GUID | Notes |
|---|---|
| `00000000-0000-0000-0000-000000000001` | Hand-authored |
| `5d32399b-ac20-4fdd-b6bb-e92cfd0b3742` | Normal |
| `7af6066b-00ef-449d-bc12-a70583c5bd01` | Normal |
| `b4941df0-6c30-48b4-b2ba-d098a864bf49` | Normal |

**`"Identity Data"` name × 32 — mass placeholder**  
Thirty-two records all have the literal name `"Identity Data"`, `data_type = "Text"`,
`group = "Other"`. `"Identity Data"` is a Revit built-in parameter group name. Using it as
a parameter name is almost certainly a shared-parameter-file template error or a vendor
pattern where this placeholder was never replaced. These 32 records are near-certainly not
promotable as-is. See Section D.

**`Green Building-LEED` × 2 — different GUIDs, different groups**

| GUID | group |
|---|---|
| `00000000-0000-0000-0000-000000000010` | Text (anomalous) |
| `e12cad99-dcc9-4303-9c2f-7f63f211388c` | Green Building Properties |

**`R Value` vs `R-Value`** — near-duplicate names, same `data_type = "Number"`,
same `group = "Energy Analysis"`. Different GUIDs. These represent the same physical
concept under two slightly different names. Decide which is canonical before promotion.

**`Glazing Thickness` × 2** — same dtype (`Length`) but different groups
(`Dimensions` vs `Constraints`). Same concept, different assignment. One is likely
from a door family, one from a window family.

**`Building Codes` × 2** — same dtype (`URL`), both have `group = "Text"` (anomalous),
but different GUIDs. Both hand-authored (see Section D). True duplicate under an
anomalous group.

### True-duplicate names (same dtype + group, multiple GUIDs) — sample

59 distinct names appear with identical dtype/group but different GUIDs. Selected examples:

| Name | dtype | group | Count |
|---|---|---|---|
| `Identity Data` | Text | Other | **32** |
| `Copyright` | Text | Identity Data | 4 |
| `Panel Width` | Length | Dimensions | 4 |
| `Finish` | Material | Materials and Finishes | 4 |
| `Frame Finish` | Material | Materials and Finishes | 3 |
| `Interior Finish` | Material | Materials and Finishes | 3 |
| `Panel Height` | Length | Dimensions | 3 |
| `Product Material` | Material | Materials and Finishes | 3 |
| `Clearance Offset Back/Bottom/Front/Left/Right/Top` | Length | Constraints | 2 each |
| `Actual Height` / `Actual Width` | Length | Dimensions | 2 each |
| `Frequency` | Frequency | Electrical | 2 |
| `Number of Poles` | Number of Poles | Electrical | 2 |

These likely exist because the shared parameter file accumulated parameters from multiple
family authors over time, each adding their own copy rather than referencing a shared definition.

---

## D. Source-Anomaly Analysis

### D1. Hand-authored GUIDs — 23 records

The earlier audit report identified 8 records. Broader analysis finds **23** records with
GUIDs that are clearly hand-authored (sequential or patterned) rather than randomly
generated by Revit. Three distinct patterns exist, suggesting at least three authoring events.

**Pattern A — sequential `00000000-0000-0000-0000-0000000000xx` (20 records, gaps noted)**

| GUID | Name | data_type | group |
|---|---|---|---|
| `...000000000001` | Copyright | Text | Identity Data |
| `...000000000002` | *(absent — gap in sequence)* | | |
| `...000000000003` | Manufacturer Address | Text | Other |
| `...000000000004` | Manufacturer Phone | Text | Other |
| `...000000000005` | Manufacturer Fax | Text | Other |
| `...000000000006` | Manufacturer Email | Text | Other |
| `...000000000007` | Manufacturer Website | URL | Other |
| `...000000000008` | Specification | URL | **Text** ⚠ |
| `...000000000009` | Product Data | URL | **Text** ⚠ |
| `...000000000010` | Green Building-LEED | URL | **Text** ⚠ |
| `...000000000011` | Construction Details | URL | **Text** ⚠ |
| `...000000000012` | Test Data | URL | **Text** ⚠ |
| `...000000000013` | Sales Information | URL | **Text** ⚠ |
| `...000000000014` | Installation-Fabrication | URL | **Text** ⚠ |
| `...000000000015` | Drawn By | Text | Identity Data |
| `...000000000016` | Warranty Duration (Years) | Integer | Phasing |
| `...000000000017` | Maintenance Schedule (Months) | Integer | Phasing |
| `...000000000018` | Installation Phase | Text | Phasing |
| `...000000000019` | Expected Lifespan (Years) | Integer | Phasing |
| `...000000000020` | Building Codes | URL | **Text** ⚠ |

⚠ = `group = "Text"` (anomalous; `"Text"` is a data_type value, not a Revit group name).

Gaps in sequence: `...0002` is absent. `...0015`–`...001f` exist but `...0015`–`...0019`
appear (none absent between them); `...001a`–`...001f` absent; `...0020` present.

**Pattern B — `07000000-0000-0000-0000-000000000006` (1 record)**

| GUID | Name | data_type | group |
|---|---|---|---|
| `07000000-0000-0000-0000-000000000006` | Trim Material | Material | Materials and Finishes |

**Pattern C — `08000000-0000-0000-0000-00000000000x` (3 records)**

| GUID | Name | data_type | group |
|---|---|---|---|
| `08000000-0000-0000-0000-000000000001` | Sound Transmission Class (STC) | Integer | Analytical Model |
| `08000000-0000-0000-0000-000000000002` | U-Factor | Number | Energy Analysis |
| `08000000-0000-0000-0000-000000000003` | SHGC | Number | Energy Analysis |

Sound Transmission Class, U-Factor, and SHGC are physically meaningful parameters with
reasonable data_types. The authoring pattern (`08…`) is different from Pattern A (`00…`),
suggesting a different author or a different shared parameter template file.

**Key risk:** Hand-authored GUIDs are not globally unique by construction. If another
firm or a vendor library used the same sequential pattern, these GUIDs would collide in a
combined Revit model. Confirm GUIDs are stable in the source `.txt` file before promoting.

### D2. `group = "Text"` anomaly — 16 records

`"Text"` is a Revit data_type value, not a parameter group name. Fourteen of these records
are URL-type document-link parameters (Specification, Product Data, etc.) that were likely
authored with the group field left as a default or filled incorrectly. Two are `Text`-type
parameters that happen to have `group = "Text"` for the same reason.

All 16 records should have their `group` corrected in the source `.txt` file before promotion.
The correct group is likely `"Other"`, `"Identity Data"`, or `"Green Building Properties"`
depending on the parameter.

### D3. Reinforcement Length — 12 single-letter records

All 12 records have `data_type = "Reinforcement Length"` and single-letter names:
`A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `J`, `K`, `O`, `R`.

These letters are standard structural engineering notation for rebar cross-section dimensions
(from ACI/AISC reinforcement bar bending schedules). They are almost certainly inherited from
a structural engineering firm's shared parameter file rather than authored by this firm.
All 12 are candidates for `deprecated` or explicit keeper decision before the library is considered clean.

### D4. "Identity Data" × 32 — mass placeholder name

Thirty-two records are named literally `"Identity Data"` with `data_type = "Text"`,
`group = "Other"`. This is a Revit category name, not a meaningful parameter name.
These are either:
- Template slots from a shared parameter file that were never filled in, or
- A vendor's placeholder parameter used across 32 different family templates.

These 32 records are not promotable as-is. Sage must decide: deprecate all, rename in
source and re-ingest, or investigate whether they serve a real purpose in any family.

### D5. Placeholder / test / vendor artifacts

| Name | data_type | group | Issue |
|---|---|---|---|
| `Novotny temp parameter Integer` | Integer | Constraints | Developer/vendor test param (×2 different GUIDs) |
| `Novotny temp parameter Length` | Length | Constraints | Same — "Novotny" is a vendor/author name |
| `Novotny temp parameter Angle` | Angle | Constraints | Same |
| `ParameterTest` | Text | Text | Explicit test artifact |
| `Test Data` | URL | Text | Name implies test/temporary |
| `B2`, `B3`, `B4`, `B5` | Yes/No | Other | Cryptic single-code names — unclear purpose |
| `TAG 1`, `TAG 2`, `TAG 3` | Text | Text | May be intentional tagging parameters |
| `W` | Number | Structural | Single-letter structural notation |

The four `Novotny` parameters and `ParameterTest` are strong `deprecated` candidates.
`Test Data`, `TAG 1/2/3`, and `B2–B5` require human judgment on intent.

---

## E. Unknown data_type Review

19 distinct `data_type` values are absent from `KNOWN_DATA_TYPES`. All records are accepted during ingest; each triggers a `WARNING`-level log entry with count and sample names.

| data_type | Count | Sample names (up to 5) | Recommendation |
|---|---|---|---|
| `Reinforcement Length` | 12 | K, B, O, D, A, G, J, C, F, R, E, H | Add to `KNOWN_DATA_TYPES` if records are retained; deprecate cluster if inherited |
| `Temperature` | 9 | Cooling Leaving Wet Bulb Temperature, Heating Entering Dry Bulb Temperature, … | Add to `KNOWN_DATA_TYPES` — valid Revit MEP type |
| `Air Flow` | 7 | Minimum Air Flow, Actual Supply Air Flow, Maximum Air Flow, … | Add to `KNOWN_DATA_TYPES` — valid Revit MEP type |
| `Force` | 4 | Capacity (Lbs), Unit Weight, Refrigerant Charge, Shipping Weight | Add to `KNOWN_DATA_TYPES`; note `Refrigerant Charge` conflict (also has a `Text` version) |
| `Pipe Size` | 4 | Waste Connection NPT, Condensate Drain Connection Diameter, … | Add to `KNOWN_DATA_TYPES` — valid Revit MEP type |
| `Pressure` | 4 | Total Static Pressure, Coil Air Pressure Drop, … | Add to `KNOWN_DATA_TYPES` — valid Revit MEP type |
| `Number of Poles` | 4 | Phase (×2 — anomalous), Number of Poles (×2) | Add to `KNOWN_DATA_TYPES`; resolve `Phase` authoring error first |
| `Cooling Load` | 3 | Sensible Cooling Capacity, Latent Cooling Capacity, Total Cooling Capacity | Add to `KNOWN_DATA_TYPES` — valid Revit MEP type |
| `Current` | 2 | Maximum Overcurrent Protection, Minimum Circuit Amps | Add to `KNOWN_DATA_TYPES` — valid Revit type |
| `Electrical Potential` | 2 | Voltage (×2) | Add to `KNOWN_DATA_TYPES` — valid Revit type; note duplicate name `Voltage` |
| `Family type: Generic Models` | 2 | Grid Type, Glazing | Defer — naming convention unresolved; `Glazing` has 3 competing records |
| `Frequency` | 2 | Frequency (×2) | Add to `KNOWN_DATA_TYPES` — valid Revit type; note duplicate name |
| `Heating Load` | 2 | Total Heating Capacity, Nominal Heating Capacity | Add to `KNOWN_DATA_TYPES` — valid Revit MEP type |
| `Apparent Power` | 1 | Apparent Power | Add to `KNOWN_DATA_TYPES` — valid Revit electrical type |
| `Family type: Casework` | 1 | Framed Screen Type | Defer — naming convention unresolved |
| `Family type: Doors` | 1 | Threshold Type | Defer — naming convention unresolved |
| `Family type: Specialty Equipment` | 1 | Clearance Type | Defer — naming convention unresolved |
| `Flow` | 1 | Drain Flow | Add to `KNOWN_DATA_TYPES` — valid Revit MEP type |
| `Velocity` | 1 | Face Velocity (FPM) | Add to `KNOWN_DATA_TYPES` — valid Revit MEP type |

**Summary:**
- **Add to `KNOWN_DATA_TYPES` now (Sage decision needed):** Temperature, Air Flow, Force, Pipe Size, Pressure, Cooling Load, Current, Electrical Potential, Frequency, Heating Load, Apparent Power, Flow, Velocity — all confirmed Revit built-in types that appear in the data and are unlikely to be errors.
- **Add after anomaly resolution:** Number of Poles (after `Phase` data_type error is fixed), Reinforcement Length (after cluster decision).
- **Defer:** The four `Family type: <X>` variants until the canonical naming question is settled.

---

## F. Proposed Human Review Sequence

The following order is recommended to avoid promoting records that depend on earlier decisions.

**Step 1 — Resolve obvious source-authoring anomalies (Windows / source `.txt` file)**
- Fix `group = "Text"` on the 14 URL parameters in Pattern A (correct to appropriate group).
- Fix `data_type = "Number of Poles"` on the two `Phase` parameters (should be `Text` or `Integer`).
- Decide fate of `ParameterTest` and four `Novotny temp parameter` records (deprecate in DB or fix at source).
- Decide fate of 32 `"Identity Data"`-named records.

**Step 2 — Resolve GUID stability questions**
- Confirm hand-authored GUID patterns A, B, C are intentional and stable.
- Confirm `...0002` was intentionally omitted from sequence.
- Confirm `07000000-...` and `08000000-...` pattern origins.

**Step 3 — Resolve duplicate and near-duplicate names**
- Pick canonical GUID for `Copyright` (×4), `Panel Width` (×4), `Finish` (×4), and other true duplicates.
- Decide between `R Value` and `R-Value` (near-duplicate).
- Decide between `Green Building-LEED` (hand-authored GUID, `group = "Text"`) and its counterpart.
- Decide fate of the `Reinforcement Length` single-letter cluster.

**Step 4 — Identify and approve a tracer-bullet set**
- Use the candidates in Section G for the first `proposed` pass.
- Promote only after Steps 1–3 are cleared for those specific records.

**Step 5 — Broad curation**
- Review MEP and structural clusters for firm-maintained vs. inherited distinction.
- Decide `Family type: <X>` canonical naming.
- Add confirmed Revit types to `KNOWN_DATA_TYPES` per Section E recommendations.

---

## G. Candidate Tracer-Bullet Set

These 15 records are suggested as a first `proposed` promotion candidate list. All have:
- Unique names (no duplicate-name peers)
- Known `data_type` values (no unknown-type warning)
- No hand-authored GUIDs
- No known anomalous `group` values
- Clear semantic meaning

**This is a recommendation only. No statuses have been changed.**

| GUID | Name | data_type | group | Reason |
|---|---|---|---|---|
| `572d1cb9-8bf1-46eb-ad89-01ef3c28dbf7` | Actual Depth | Length | Dimensions | Standard dimensional parameter; unambiguous |
| `181635d7-fedc-4038-9290-b5e5e52cb7b6` | Actual Length | Length | Dimensions | Standard dimensional parameter; unambiguous |
| `30ba9056-14e9-4bf4-b79a-3f6295170e03` | Load Classification | LoadClassification | Electrical - Loads | Unique type; sole record; clear purpose |
| `9ed8c7d7-454c-457e-b137-cf05336df7fd` | Fixture Wattage | Number | Electrical - Loads | Clear electrical parameter; no duplicate |
| `c97f4ee5-00d4-4b4e-b66f-8dfd9f850758` | Exterior | Yes/No | Graphics | Clear semantic meaning; no duplicate |
| `dcdea1f6-ce4b-4e53-809d-c27a9a5d2f74` | Exterior Apron | Yes/No | Graphics | Clear semantic meaning; no duplicate |
| `2a91b0fd-1d30-4460-a431-a7a28aa69007` | Energy Star Zone | Text | Green Building Properties | Clear standard reference; no duplicate |
| `0952cfbd-8103-4fe5-ad48-39f9cfc3752e` | Masterformat 2014 Description | Text | IFC Parameters | Standard IFC classification reference |
| `1c426e35-2741-4c38-af9c-0b3d29c6de80` | Uniclass 2015 Code | Text | IFC Parameters | Standard IFC classification reference |
| `aef92dbf-0729-41ca-95be-06821ff6e1d6` | Voltage Comments | Text | Electrical | Clear purpose; unique name |
| `6da17127-4650-4d0e-9c0c-31fd580a5bb1` | ADA Conformance | Text | Analytical Model | Clear accessibility reference; distinct from `ADA Compliant` |
| `fb4d2c28-866d-41d3-9e7e-f7bda388ee2a` | Available voltage range | Text | Electrical | Clear purpose; unique name |
| `56b90271-0bcc-4cfe-915f-4d17e571a679` | Date of publishing | Text | General | Standard metadata; unambiguous |
| `1f9cbaba-0477-489e-a406-ee3dcf7a59ec` | R Value | Number | Energy Analysis | Verify no promotion of `R-Value` at the same time |
| `119f72ce-4488-4605-8ca4-733b0851ffb8` ¹ | Operation temperature range_Cooling | Text | Identity Data | Unique; clear if MEP context is in scope |

¹ This candidate has a vendor-formatted name (`_` separator, mixed convention). Substitute
a different candidate if the name format is unacceptable.

**Alternative / reserve candidates if any above are rejected:**

| GUID | Name | data_type | group |
|---|---|---|---|
| `94704ab1-c93e-46be-beb7-9441c23e2e3c` | Approximated Horizontal Grid Spacing | Length | Construction |
| `ace7ebae-73ad-48d3-9d22-808f9375437d` | Approximated Vertical Grid Spacing | Length | Construction |
| `5b709c88-a636-4fcc-916a-03ab537dc76f` | Brand url | URL | General |
| `bab5f244-0fa6-4969-b31a-915506e8a30c` | Green Building LEED | URL | Green Building Properties |

---

## H. Items Requiring Shawn/Sage Decision

The following decisions are required before any status promotion proceeds.

1. **`group = "Text"` on 16 records (D2)** — What is the correct group for each? Correct in source `.txt` and re-ingest, or accept via direct DB curation?

2. **`Phase` × 2 with `data_type = "Number of Poles"` (C, D)** — Confirm this is a source-authoring error. What should the correct `data_type` be? Fix in source `.txt` and re-ingest, or curate directly?

3. **32 `"Identity Data"` named records (D4)** — Deprecate all? Investigate origin? These are not promotable as-is.

4. **`Novotny temp parameter` × 4 and `ParameterTest` (D5)** — Deprecate? These appear to be developer artifacts.

5. **Hand-authored GUID stability (D1)** — Confirm that Patterns A, B, and C GUIDs are stable and will not change in future shared parameter file revisions. Confirm the missing `...0002` is intentional.

6. **Reinforcement Length single-letter cluster (D3)** — Deprecate as inherited structural? Retain? This is the largest single unknown-data_type cluster.

7. **Duplicate name resolution (C)** — For the 59 true-duplicate name groups, which GUID is canonical? The `Copyright` (×4) and `Panel Width` (×4) cases need a decision. Duplicates cannot both be `approved`.

8. **`R Value` vs `R-Value` (C)** — Which is canonical? The other should be `deprecated`.

9. **`Family type: <X>` canonical naming (E)** — Is `FamilyType` or `Family type: <category>` the expected string? Does Revit emit these differently in different contexts?

10. **MEP and structural cluster scope (B)** — Which of the MEP/structural records are firm-maintained vs. inherited? This drives whether they become `approved` or `deprecated`.

11. **`KNOWN_DATA_TYPES` expansion (E)** — Approve the 13 Revit built-in types flagged in Section E for addition? Adding them will silence the warnings for those types once records are confirmed in scope.

12. **Tracer-bullet set confirmation (G)** — Review the 15 candidates and confirm or adjust the list before Max runs the promotion workflow.
