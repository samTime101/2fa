import os
import json

folder_path = './'  # You can change this to any path you want

if os.path.isdir(folder_path):
    items = os.listdir(folder_path)
    full_paths = [os.path.join(folder_path, item) for item in items]

    # Sort by last modified time (newest first)
    sorted_items = sorted(full_paths, key=os.path.getmtime, reverse=True)
    sorted_names = [os.path.basename(item) for item in sorted_items]

    print(json.dumps({'folder': sorted_names}, indent=2))

elif os.path.isfile(folder_path):
    with open(folder_path, 'r') as f:
        file_content = f.read()
        print(file_content)

