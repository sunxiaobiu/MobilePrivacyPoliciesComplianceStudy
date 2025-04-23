import yaml
import os

# Main directory path (contains multiple application subfolders)
base_directory = r'C:\Users\Softf\Desktop\Privacy_Policy_PoliGraph'

# Output directory path
output_base_directory = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison'

# Traverse all application subfolders in the main directory
for app_folder in os.listdir(base_directory):
    app_folder_path = os.path.join(base_directory, app_folder)

    # Check if it's a folder
    if os.path.isdir(app_folder_path):
        # Traverse all date-named subfolders under each application folder
        for date_folder in os.listdir(app_folder_path):
            date_folder_path = os.path.join(app_folder_path, date_folder)
            input_file_path = os.path.join(date_folder_path, 'graph-original.yml')

            # Check if the YAML file exists
            if os.path.exists(input_file_path):
                # Create output application folder path
                output_app_folder = os.path.join(output_base_directory, app_folder)
                os.makedirs(output_app_folder, exist_ok=True)

                # Output file path, file name: date folder name + '_targets.txt'
                output_file_name = f'{date_folder}_targets.txt'
                output_file_path = os.path.join(output_app_folder, output_file_name)

                # Read and process the YAML file
                with open(input_file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)

                # Extract all "target" values
                targets = [link["target"] for link in data.get('links', []) if "target" in link]

                # Save the extracted "target" values to a TXT file
                with open(output_file_path, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(targets))

                print(f'Processed and saved file: {output_file_path}')
            else:
                print(f'File does not exist: {input_file_path}')
