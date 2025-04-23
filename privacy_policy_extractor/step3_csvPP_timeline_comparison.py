import os
import pandas as pd

# Input directory path: the main directory containing all application subfolders
input_directory = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison'

# Iterate through all application subfolders in the input directory
for app_folder in os.listdir(input_directory):
    app_folder_path = os.path.join(input_directory, app_folder)

    # Check if it is a folder
    if os.path.isdir(app_folder_path):
        # Input CSV file path
        input_csv_path = os.path.join(app_folder_path, f'{app_folder}_targets.csv')

        # Output CSV file path
        output_csv_path = os.path.join(app_folder_path, f'{app_folder}_targets_timeline_comparison.csv')

        # Check if the input CSV file exists
        if not os.path.exists(input_csv_path):
            print(f'Input file does not exist, skipping: {input_csv_path}')
            continue

        # Read the CSV file, specifying the 'Content' column as a string type
        df = pd.read_csv(input_csv_path, dtype={'Content': str})

        # Sort the data to ensure processing by date order
        df.sort_values(by='FolderName', inplace=True)

        # Store the final results
        timeline_data = []

        # Compare each pair of adjacent versions
        for i in range(len(df) - 1):
            # Current version and next version
            current_version = df.iloc[i]
            next_version = df.iloc[i + 1]

            # Version range (e.g., "201708 -> 201709")
            version_range = f"{current_version['FolderName']} -> {next_version['FolderName']}"

            # Get the content of the current and next versions, handle missing values
            current_content = current_version['Content']
            next_content = next_version['Content']

            # If the content of the current version is empty, set added and removed as 'Content is empty'
            if pd.isna(current_content) or pd.isna(next_content):
                added = 'emptyContent'
                removed = 'emptyContent'
            else:
                current_content = set(current_content.split(', '))
                next_content = set(next_content.split(', '))

                # Calculate added and removed content
                added = list(next_content - current_content)
                removed = list(current_content - next_content)

                # If added or removed content is empty, set it as 'No changes'
                if not added:
                    added = None
                else:
                    added = ', '.join(added)

                if not removed:
                    removed = None
                else:
                    removed = ', '.join(removed)

            # Append the data to the timeline_data list
            timeline_data.append({
                'Version': version_range,
                'Added': added,
                'Removed': removed
            })

        # Convert the results into a DataFrame
        timeline_df = pd.DataFrame(timeline_data)

        # Save the results as a new CSV file
        timeline_df.to_csv(output_csv_path, index=False)

        print(f'Timeline comparison has been saved to CSV file: {output_csv_path}')
