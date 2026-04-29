# ruff: noqa: UP010, UP020, UP030, UP032
"""Extract shared parameter definitions from the active Revit document.

This script is manually run from pyRevit inside Revit on Windows. It is
intentionally not unit-tested by pytest because Revit API code cannot run in
the dev container.

The script is self-contained by design: it does not import the container-only
Python package and it uses only Python/Revit API modules available in pyRevit.
It reads shared parameter definitions from the active document and writes one
timestamped immutable JSON export under exports/raw/.
"""

from __future__ import absolute_import

import io
import json
import os
from datetime import datetime

try:
    from Autodesk.Revit.DB import LabelUtils
except Exception:
    LabelUtils = None

try:
    from pyrevit import revit, script
except Exception:
    revit = None
    script = None


EXTRACTED_KEYS = ("guid", "name", "data_type", "group", "description")


def _repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _raw_export_dir():
    return os.path.join(_repo_root(), "exports", "raw")


def _definition_guid(definition):
    guid = getattr(definition, "GUID", None)
    if guid is None:
        return None
    return str(guid)


def _definition_name(definition):
    return getattr(definition, "Name", None)


def _definition_group(definition):
    owner_group = getattr(definition, "OwnerGroup", None)
    if owner_group is not None:
        group_name = getattr(owner_group, "Name", None)
        if group_name:
            return group_name

    try:
        group_id = definition.GetGroupTypeId()
        if LabelUtils is not None:
            return LabelUtils.GetLabelForGroup(group_id)
        return group_id.TypeId
    except Exception:
        pass

    try:
        if LabelUtils is not None:
            return LabelUtils.GetLabelFor(definition.ParameterGroup)
        return str(definition.ParameterGroup)
    except Exception:
        return None


def _definition_description(definition):
    description = getattr(definition, "Description", None)
    return description or None


def _normalize_data_type_label(label):
    if not label:
        return None

    compact = label.replace(" ", "").replace("-", "").replace("_", "")
    lowered = compact.lower()
    known = {
        "text": "Text",
        "string": "Text",
        "integer": "Integer",
        "int": "Integer",
        "number": "Number",
        "double": "Number",
        "length": "Length",
        "area": "Area",
        "volume": "Volume",
        "angle": "Angle",
        "url": "URL",
        "material": "Material",
        "yesno": "YesNo",
        "boolean": "YesNo",
        "multilinetext": "MultilineText",
        "currency": "Currency",
        "loadclassification": "LoadClassification",
        "image": "Image",
        "familytype": "FamilyType",
    }
    return known.get(lowered, label)


def _definition_data_type(definition):
    try:
        data_type_id = definition.GetDataType()
        if LabelUtils is not None:
            try:
                return _normalize_data_type_label(LabelUtils.GetLabelForSpec(data_type_id))
            except Exception:
                pass

        type_id = getattr(data_type_id, "TypeId", None)
        if type_id:
            return _normalize_data_type_label(type_id.rsplit(":", 1)[-1].rsplit(".", 1)[-1])
        return _normalize_data_type_label(str(data_type_id))
    except Exception:
        pass

    try:
        return _normalize_data_type_label(str(definition.ParameterType))
    except Exception:
        return None


def _shared_parameter_records(doc):
    binding_map = doc.ParameterBindings
    iterator = binding_map.ForwardIterator()
    iterator.Reset()

    records_by_guid = {}
    while iterator.MoveNext():
        definition = iterator.Key
        guid = _definition_guid(definition)
        if not guid:
            continue

        name = _definition_name(definition)
        data_type = _definition_data_type(definition)
        if not name or not data_type:
            continue

        records_by_guid[guid.lower()] = {
            "guid": guid.lower(),
            "name": name,
            "data_type": data_type,
            "group": _definition_group(definition),
            "description": _definition_description(definition),
        }

    return [records_by_guid[guid] for guid in sorted(records_by_guid)]


def _new_export_path(raw_dir):
    base = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = os.path.join(raw_dir, base + ".json")
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(raw_dir, "{0}_{1:02d}.json".format(base, counter))
        counter += 1
    return candidate


def _write_json(path, records):
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def main():
    if revit is None:
        raise RuntimeError("This script must be run from pyRevit inside Revit.")

    doc = revit.doc
    if doc is None:
        raise RuntimeError("No active Revit document found.")

    raw_dir = _raw_export_dir()
    if not os.path.isdir(raw_dir):
        os.makedirs(raw_dir)

    records = _shared_parameter_records(doc)
    output_path = _new_export_path(raw_dir)
    _write_json(output_path, records)

    message = "Exported {0} shared parameters to {1}".format(len(records), output_path)
    if script is not None:
        script.get_output().print_md(message)
    else:
        print(message)


if __name__ == "__main__":
    main()
