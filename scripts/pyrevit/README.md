# pyRevit Extraction Scripts

Scripts in this directory run **inside Revit** via pyRevit on a Windows machine.
They cannot run inside the dev container.

## Prerequisites

- Revit 2026
- pyRevit 4.8+
- Access to a Revit model containing shared parameters

## Usage

1. Open your Revit model.
2. Open the pyRevit shell or add these scripts to a pyRevit tab/button.
3. Run `extract_shared_params.py`.
4. The script writes a timestamped JSON file to `../../exports/raw/`.

## Output contract

- One JSON array per run.
- Each element must have: `guid`, `name`, `data_type`.
- Optional fields: `group`, `description`.
- File is never overwritten — always a new timestamped filename.
- **Do not hand-edit files under `exports/raw/`.**

## Placeholder

`extract_shared_params.py` is not yet implemented. Revit API code will be
authored in a future session.
