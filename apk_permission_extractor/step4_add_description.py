import pandas as pd

# File paths
input_folder = r'C:\Users\Softf\Desktop\new hp computer\PP Project\APKPermissionsandComparison'
all_unique_permissions_path = f'{input_folder}\\all_unique_permissions.csv'
android_permissions_path = f'{input_folder}\\androidPermissions.csv'
output_path = f'{input_folder}\\permission_with_description.csv'

# Read CSV files
all_unique_permissions_df = pd.read_csv(all_unique_permissions_path)
android_permissions_df = pd.read_csv(android_permissions_path)

# Create a dictionary to quickly match Permissions with their Descriptions
permission_dict = dict(zip(android_permissions_df['Permission'], android_permissions_df['Description']))

# Add a 'Description' column to the DataFrame
all_unique_permissions_df['Description'] = all_unique_permissions_df['all_unique_permissions'].map(permission_dict)

# Save the result to a new CSV file
all_unique_permissions_df.to_csv(output_path, index=False)

print("CSV file has been generated:", output_path)
