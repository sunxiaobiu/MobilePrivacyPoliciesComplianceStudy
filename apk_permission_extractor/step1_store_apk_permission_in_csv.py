import os
import csv

def extract_txt_to_csv(folder_path, output_csv_path):
    """
    Traverse subfolders and extract content from each .txt file starting from the fourth line.
    Each line is split and saved to a CSV file, with the content stored as a list for later comparison.
    'FilePath' stores the APK file's year and month.
    """
    data = []  # Store all data from .txt files

    # Check if the output directory exists, if not, create it
    output_folder = os.path.dirname(output_csv_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Skip processing if the CSV file already exists
    if os.path.exists(output_csv_path):
        print(f"File {output_csv_path} already exists, skipping.")
        return

    # Traverse the folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                txt_file_path = os.path.join(root, file)
                # Get the name of the parent folder
                folder_name = os.path.basename(root)
                with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
                    lines = txt_file.readlines()
                    if len(lines) >= 4:  # Ensure the file has at least 4 lines
                        # Read from the fourth line and split each line
                        extracted_lines = [
                            line.strip().split() for line in lines[3:]
                        ]
                        data.append({
                            "FolderName": folder_name,  # Use folder name
                            "Content": extracted_lines  # Store as a list
                        })

    # Write to a CSV file
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Write header
        writer.writerow(["FolderName", "Content"])
        # Write content, storing 'Content' as a string for CSV compatibility
        for entry in data:
            writer.writerow([entry["FolderName"], repr(entry["Content"])])

    print(f"Data successfully written to {output_csv_path}")

# Set folder path and output CSV path
base_folder_path = r"C:\Users\Softf\Desktop\APKMirror"  # Path to APKMirror directory
output_base_path = r"C:\Users\Softf\Desktop\new hp computer\PP Project\APKPermissionsandComparison"  # Output directory path

# Traverse each subfolder under the APKMirror directory
for subfolder in os.listdir(base_folder_path):
    subfolder_path = os.path.join(base_folder_path, subfolder)
    if os.path.isdir(subfolder_path):
        # Construct path to the target txt files
        txt_folder_path = os.path.join(subfolder_path, "APK LINKS", "apkmirror2", "apk", "apk_permissions")
        if os.path.exists(txt_folder_path):
            # Construct output CSV file path
            output_csv_path = os.path.join(output_base_path, subfolder, f"{subfolder}_permissions.csv")
            # Call the function to process the subfolder
            extract_txt_to_csv(txt_folder_path, output_csv_path)
        else:
            print(f"Path {txt_folder_path} does not exist, skipping this subfolder.")
