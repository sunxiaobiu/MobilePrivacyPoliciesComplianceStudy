import os 
import csv

# Input directory path: the main directory containing all application subfolders
input_directory = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison'

# Iterate through all application subfolders in the input directory
for app_folder in os.listdir(input_directory):
    app_folder_path = os.path.join(input_directory, app_folder)

    # Check if it is a folder
    if os.path.isdir(app_folder_path):
        # Output CSV file path
        output_csv_path = os.path.join(app_folder_path, f'{app_folder}_targets.csv')

        # Check if the target CSV file already exists; if so, skip processing
        # if os.path.exists(output_csv_path):
        #     print(f'File already exists, skipping: {output_csv_path}')
        #     continue

        csv_data = []

        # Traverse all files under the application folder
        for root, dirs, files in os.walk(app_folder_path):
            for file in files:
                # Make sure it's a TXT file
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)

                    # Get the first six characters of the file name as an identifier (e.g., "202011")
                    folder_name = file[:6]

                    # Read the content of the TXT file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content_lines = f.readlines()

                    # Store content line by line into a set (to remove duplicates), and filter out 'UNSPECIFIED_DATA'
                    content_set = set(line.strip() for line in content_lines if line.strip() != 'UNSPECIFIED_DATA')

                    # Add the data to the csv_data list
                    csv_data.append({
                        'FolderName': folder_name,
                        'Content': list(content_set)  # Convert the set back to a list
                    })

        # If there is data to be written to the CSV
        if csv_data:
            # Save all content to the CSV file
            with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['FolderName', 'Content']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in csv_data:
                    # Join the list content with commas and save
                    writer.writerow({
                        'FolderName': row['FolderName'],
                        'Content': ', '.join(row['Content'])
                    })

            print(f'All data has been saved to CSV file: {output_csv_path}')
        else:
            print(f'No valid TXT files found in folder: {app_folder_path}')
