import os
import pandas as pd

# Define the base folder path
base_folder_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\APKPermissionsandComparison'

# List to store all permissions
all_permissions = []

# Iterate through all subdirectories
for subdir_name in os.listdir(base_folder_path):
    subdir_path = os.path.join(base_folder_path, subdir_name)
    if os.path.isdir(subdir_path):
        # Construct the target permission file path
        permission_file_path = os.path.join(subdir_path, f'{subdir_name}_all_permissions.csv')
        if os.path.exists(permission_file_path):
            # Load the permission CSV file
            permissions_df = pd.read_csv(permission_file_path)
            # Extract the 'Permission' column and add it to the list
            all_permissions.extend(permissions_df['Permission'])
        else:
            print(f"File '{permission_file_path}' not found, skipping this subfolder.")
    else:
        print(f"'{subdir_name}' is not a valid subdirectory, skipping.")

# Convert all collected permissions to a DataFrame
all_permissions_df = pd.DataFrame(all_permissions, columns=['permission'])

# Remove duplicate permissions globally
all_unique_permissions = all_permissions_df['permission'].drop_duplicates()

# Save the result to a CSV file
output_file_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\APKPermissionsandComparison\all_unique_permissions.csv'
all_unique_permissions.to_csv(output_file_path, index=False, header=['all_unique_permissions'])

print(f"All unique permissions have been saved to '{output_file_path}'.")
