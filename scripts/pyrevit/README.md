# pyRevit Extraction Scripts

Scripts in this directory run **inside Revit** via pyRevit on a Windows machine.
They cannot run inside the dev container.

## Prerequisites

- Revit 2026
- pyRevit 4.8+
- Access to a Revit model containing shared parameters

## Usage

1. Open your Revit model.
2. Open the pyRevit shell, or add `extract_shared_params.py` to a pyRevit
   tab/button.
3. Run `extract_shared_params.py` from pyRevit.
4. The script writes a timestamped JSON file to the repository's
   `exports/raw/` directory.

## Output contract

- One JSON array per run.
- Each element contains exactly these raw Revit fields: `guid`, `name`,
  `data_type`, `group`, `description`.
- `source_file` is not produced by pyRevit. It is populated later by
  container-side ingest from the raw JSON filename.
- File is never overwritten — always a new timestamped filename.
- Files under `exports/raw/` are immutable evidence. Do not hand-edit, rename,
  delete, overwrite, or otherwise mutate them.

## Next step

After extraction, run the container-side ingest pipeline against the raw JSON
export. Do not run ingest from Windows paths.
