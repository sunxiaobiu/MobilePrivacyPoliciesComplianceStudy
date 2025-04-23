import os
import pandas as pd

# Get the path to the base folder
base_folder_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison'

# List to store all target_info
all_target_info = []

# Iterate through all subfolders
for subdir_name in os.listdir(base_folder_path):
    subdir_path = os.path.join(base_folder_path, subdir_name)
    if os.path.isdir(subdir_path):
        # Build the target file path
        target_file_path = os.path.join(subdir_path, f'{subdir_name}_target_info_summary.csv')
        if os.path.exists(target_file_path):
            # Load the target info CSV file
            targets_df = pd.read_csv(target_file_path)
            # Extract the 'target_info' column and add it to the list
            all_target_info.extend(targets_df['target_info'])
        else:
            print(f"File '{target_file_path}' not found, skipping this subfolder.")
    else:
        print(f"'{subdir_name}' is not a valid subfolder, skipping.")

# Convert all target_info to a DataFrame
all_target_info_df = pd.DataFrame(all_target_info, columns=['target_info'])

# Remove duplicates from all target_info globally
all_unique_target_info = all_target_info_df['target_info'].drop_duplicates()

# Save the result to a CSV file
output_file_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison\all_unique_target_info.csv'
all_unique_target_info.to_csv(output_file_path, index=False, header=['all_unique_target_info'])

print(f"All unique target_info has been saved to '{output_file_path}'.")
