"""
Bundle multiple yaml files in a single one.
Replace all $ref that refer to a local file path with the json path.
Must be careful to declare a key for each element, or the substitution will fail.
"""

import json
import os
from pathlib import Path
from typing import Any

import yaml

CURRENT_FOLDER = Path(__file__).parent
BUNDLE_FILENAME = "bundle.yaml"
BUNDLE_FILE = CURRENT_FOLDER / BUNDLE_FILENAME


def ref_replacer(dict_var: dict[str, Any]):
    """Foreach key equal to `$ref` replace the value, stripping all before the `#`."""
    for k, v in dict_var.items():
        if k == "$ref":
            if "#" not in v:
                continue

            _index = v.index("#")
            dict_var[k] = v[_index:]
            yield v

        elif isinstance(v, dict):
            for id_val in ref_replacer(v):
                yield id_val


def get_all_yaml_files(
    path: Path = CURRENT_FOLDER,
    blacklist_bundle_file: str = BUNDLE_FILENAME,
) -> list[Path]:
    """Given a path, find all yaml files (apart from the blacklist one)."""
    oas_definitions = set()
    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith(".yaml") or file.startswith("."):
                continue

            if file == blacklist_bundle_file:
                continue

            if "." in root:
                continue

            module_path = os.path.join(root, file)
            oas_definitions.add(Path(module_path))

    return sorted(oas_definitions)


def export_definition(data: dict[str, Any], output_file: Path = BUNDLE_FILE) -> None:
    """Export the bundled definition."""
    with open(output_file, "w") as f:
        f.write(json.dumps(data, indent=4))


def main() -> None:
    oas_partial_files = get_all_yaml_files()

    oas_definitions = dict()
    for _file in oas_partial_files:
        oas_definitions.update(yaml.load(Path(_file).read_text(), Loader=yaml.Loader))

    for _ in ref_replacer(oas_definitions):
        # don't do anything, just replace all occurrence
        continue

    export_definition(oas_definitions)


if __name__ == "__main__":
    main()
