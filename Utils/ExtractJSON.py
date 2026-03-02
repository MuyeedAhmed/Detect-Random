import pandas as pd
import json
import glob
import os


def main():
    file_list = glob.glob('../Results/*.txt')
    all_data = []

    for file_path in file_list:
        outfile_name = os.path.basename(file_path)[:-4]+".xlsx"
        outfile_name = os.path.join('../Results', outfile_name)
        if os.path.exists(outfile_name):
            print(f"File {outfile_name} already exists. Skipping {file_path}.")
            continue
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                for entry in data:
                    all_data.append({
                        'Path': entry.get('path'),
                        'File': os.path.basename(entry.get('path')),
                        'Function': entry.get('define'),
                        'Line': entry.get('line'),
                        'Stop Line': entry.get('stop_line'),
                        'Leak Name': entry.get('name')
                    })
        except json.JSONDecodeError:
            print(f"Skipping {file_path}: Invalid JSON format.")

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_excel(outfile_name, index=False)
    

if __name__ == "__main__":
    main()