import pandas as pd
import json
import sys
import os

def filter_functions(json_file_path, excel_file_path, output_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    df = pd.read_excel(excel_file_path)
    target_functions = set(df['Function'].astype(str))

    skip_exact = {
        "input", "print", "float.__new__", "object.__init__", "str.__ne__", 
        "str.__eq__", "_warnings.warn", "all", "any", "max", "min", "sum", 
        "abs", "round", "sorted", "enumerate", "zip", "map", "filter", 
        "int.__add__", "int.__sub__", "int.__mul__", "int.__truediv__", 
        "int.__floordiv__", "int.__mod__", "int.__pow__", "time.time", 
        "bytes.decode", "bytes.encode", "int.__le__", "int.__lt__", 
        "int.__ge__", "int.__gt__", "str.__add__", "str.__mul__", 
        "str.__contains__", "str.__getitem__", "str.__len__", "str.__iter__", 
        "callable", "getattr", "setattr", "hasattr", "isinstance", "issubclass", 
        "len", "open", "range", "type", "vars", "dir", "id", "hash", "help", 
        "hex", "oct", "bin", "repr", "ascii", "format", "globals", "locals"
    }
    ignore_prefixes = (
        "Overrides{", "math.", "numpy.", "pandas.", "pip.", "os.", "sys.", "array.", 
        "list.", "dict.", "set.", "tuple.", "str.", "int.", "float.", 
        "bool.", "bytes.", "object.", "type.", "time.", "range.", 
        "callable", "getattr", "setattr", "hasattr", "isinstance", 
        "issubclass", "len", "open", "vars", "dir", "id", "hash", 
        "help", "hex", "oct", "bin", "repr", "ascii", "format", 
        "globals", "locals", "enumerate.", "zip.", "map", "filter",
        "itertools.", "pdb.", "slice.", "functools.", "collections.", 
        "subprocess.", "threading.", "asyncio.", "concurrent.", "multiprocessing.", 
        "socket.", "ssl.", "http.", "urllib.", "email.", "json.", "csv.", "xml.", 
        "logging.", "argparse.", "configparser.", "shutil.", "tempfile.", "glob.", "fnmatch.", "re.",
        "time.", "range.", "warnings.", "contextlib.", "dataclasses.", "enum.", "typing.", 
        "abc.", "copy.", "pickle.", "inspect.", "traceback.", "unittest.", "doctest.", "pydoc.", "asyncio."
    )
    
    ignore_substrings = ["._add_taint", "float.__", "int.__", "str.__", "bytes.__", "object.__", "type.__"]

    matching_functions = []

    for name, dependencies in data.items():
        if (name in skip_exact or 
            name in target_functions or 
            name.startswith(ignore_prefixes) or 
            any(sub in name for sub in ignore_substrings)):
            continue
        for dep in dependencies:
            if dep in target_functions:
                matching_functions.append([dep, name])
            
    result_df = pd.DataFrame(matching_functions, columns=['Function', 'TITO'])
    result_df.to_excel(output_file_path, index=False)
    

if __name__ == "__main__":
    results_path = "../Results/"
    project_path = sys.argv[1]

    json_path = os.path.join(project_path, "pyre-output/dependency-graph.json")
    project_name = os.path.basename(os.path.normpath(project_path))
    exelpath = os.path.join(results_path, "Filtered/" + project_name + ".xlsx")
    output_path = os.path.join(results_path, "Filtered/" + project_name + "_TITO.xlsx")
    filter_functions(
        json_file_path=json_path,
        excel_file_path=exelpath,
        output_file_path=output_path
    )