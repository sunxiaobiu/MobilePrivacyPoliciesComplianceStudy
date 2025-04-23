import os
import pandas as pd

# Input directory path: main directory containing all app subfolders
input_directory = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison'

# Iterate through all app subfolders in the input directory
for app_folder in os.listdir(input_directory):
    app_folder_path = os.path.join(input_directory, app_folder)

    # Check if it's a directory
    if os.path.isdir(app_folder_path):
        # Input CSV file path
        input_csv_path = os.path.join(app_folder_path, f'{app_folder}_targets.csv')

        # Check if the input CSV file exists
        if not os.path.exists(input_csv_path):
            print(f'Input file does not exist, skipping processing: {input_csv_path}')
            continue

        # Read the CSV file, specify 'Content' column as string type
        df = pd.read_csv(input_csv_path, dtype={'Content': str})

        # Filter out rows where the 'Content' column is empty
        df = df[df['Content'].notna()]

        # Set to store all content
        all_content = set()

        # Iterate through all rows, collect content and remove duplicates
        for _, row in df.iterrows():
            # Split content by comma and space, then store and deduplicate
            content_lines = set(row['Content'].split(', '))
            all_content.update(content_lines)

        # Convert the deduplicated content to a DataFrame
        target_info_df = pd.DataFrame(list(all_content), columns=['target_info'])

        # Output file path
        output_csv_path = os.path.join(app_folder_path, f'{app_folder}_target_info_summary.csv')

        # Save the result to a CSV file
        target_info_df.to_csv(output_csv_path, index=False)

        print(f'All target info has been deduplicated and saved to CSV file: {output_csv_path}')
