import os
import csv
import ast

def collect_permissions(input_csv_path, output_csv_path):
    """
    Collects permissions from the specified CSV file, removes prefixes from the permissions,
    and writes the cleaned list to a new CSV file. If the output file already exists, processing is skipped.

    Args:
        input_csv_path (str): Path to the input CSV file containing permission data.
        output_csv_path (str): Path to save the cleaned and merged permission list.
    """
    # Skip processing if the output file already exists
    if os.path.exists(output_csv_path):
        print(f"File {output_csv_path} already exists, skipping.")
        return

    all_permissions = set()

    # Read input CSV and collect permissions
    with open(input_csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            # Parse the permission list from string to Python list
            content = ast.literal_eval(row[1])
            flattened_content = [item for sublist in content for item in sublist]  # Flatten nested list
            
            # Remove permission prefixes, keep only the last part
            cleaned_permissions = {permission.split('.')[-1] for permission in flattened_content}
            all_permissions.update(cleaned_permissions)  # Add to set to remove duplicates

    # Write all unique permissions to the output CSV
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(['Permission'])  # Write header
        for permission in sorted(all_permissions):  # Sort alphabetically
            writer.writerow([permission])

    print(f"Permission collection completed. Results saved to {output_csv_path}")

def process_permissions_in_subfolders(base_dir):
    """
    Traverse all subfolders under the given base directory, and process each '_permissions.csv' file.

    Args:
        base_dir (str): Path to the base directory containing subfolders.
    """
    # Traverse all subfolders in the base directory
    for subfolder_name in os.listdir(base_dir):
        subfolder_path = os.path.join(base_dir, subfolder_name)
        if os.path.isdir(subfolder_path):
            # Construct input and output file paths
            input_csv_path = os.path.join(subfolder_path, f"{subfolder_name}_permissions.csv")
            output_csv_path = os.path.join(subfolder_path, f"{subfolder_name}_all_permissions.csv")
            
            # Check if the input file exists
            if os.path.exists(input_csv_path):
                collect_permissions(input_csv_path, output_csv_path)
            else:
                print(f"File {input_csv_path} does not exist, skipping.")

if __name__ == "__main__":
    base_directory = r"C:\Users\Softf\Desktop\new hp computer\PP Project\APKPermissionsandComparison"
    process_permissions_in_subfolders(base_directory)
