import shutil
import os

import json
import sys
from pathlib import Path


def GeneratePysaConfig(source_dirs, output_path="Files/.pyre_configuration"):
    if isinstance(source_dirs, str):
        source_dirs = [source_dirs]
    config = {
        "site_package_search_strategy": "pep561",
        "source_directories": source_dirs,
        "taint_models_path": ["pysa_models"]
    }
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

def CopyPysaDirectoryContents(src_dir, dst_dir):
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)

    for item in src_path.iterdir():
        src_item = item
        dst_item = dst_path / item.name

        if item.is_dir():
            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
        else:
            shutil.copy2(src_item, dst_item)


if __name__ == "__main__":
    lib_source_path = sys.argv[1]
    lib_check_path = sys.argv[2]

    GeneratePysaConfig(lib_check_path)

    CopyPysaDirectoryContents("Files", lib_source_path)
    
