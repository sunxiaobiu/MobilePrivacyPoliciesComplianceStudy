import openai
import pandas as pd
import os
import time
import csv

# Set your OpenAI API key
openai.api_key = ""  # Add your API key here

# Function to match target information to the closest data type using ChatCompletion
def match_target_to_data_type(target_info, data_types):
    """
    Map the target information description to the closest data type using OpenAI's ChatCompletion.
    """
    # Build the ChatCompletion prompt, including the data type name, category, and description
    data_types_description = "\n".join([f"{data_type} ({category}) - {desc}" for data_type, category, desc in data_types])
    
    messages = [
        {"role": "system", "content": "You are an assistant that matches target information to data types. Please respond with the best match as a single data type name, without any extra explanation or category name."},
        {"role": "user", "content": f"The target info is: {target_info}.\n\nHere are the available data types and their descriptions:\n{data_types_description}\n\nWhich data type does this target most closely relate to?"}
    ]
    
    # Make the API call to OpenAI's GPT-3.5 model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Using GPT-3.5 model
        messages=messages
    )
    
    # Extract and return the matched data type
    return response['choices'][0]['message']['content'].strip()

# Function to match each target information to the closest data type and save results to CSV file in real-time
def match_targets_to_data(targets_df, data_types_df, output_file_path):
    """
    Match each target information to the closest data type and save results to a CSV file in real-time.
    """
    # Create a list of tuples containing data type names, categories, and descriptions
    data_types = list(zip(data_types_df['data_type_name'], data_types_df['category_name'], data_types_df['description']))

    # Check if the output file already exists, if so, get the current row count
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile)
            existing_rows = sum(1 for row in reader) - 1  # Subtract the header row
    else:
        existing_rows = 0

    # Start processing from the first unprocessed row
    row_counter = 0  # Initialize the row counter
    for i, target_row in targets_df.iloc[existing_rows:].iterrows():
        target_info = target_row['all_unique_target_info']
        # Get the matched data type
        matched_data_type = match_target_to_data_type(target_info, data_types)
        # Write the current row data to the output file
        with open(output_file_path, 'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if existing_rows == 0:
                writer.writerow(['target_info', 'matched_data_type'])  # Write header if it's the first row
            writer.writerow([target_info, matched_data_type])

        row_counter += 1
        # Pause for 1 minute after processing 300 rows
        if row_counter % 300 == 0:
            print(f"Processed {row_counter} rows, taking a 1-minute break...")
            time.sleep(60)  # Pause for 1 minute

    print(f"Matching completed. Results have been saved to '{output_file_path}'.")

# Main function to execute the target-to-data type matching process
def main():
    """
    Main function to execute the target-to-data type matching process.
    """
    # Load CSV files
    data_types_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison\data_types.csv'
    data_types_df = pd.read_csv(data_types_path, encoding='ISO-8859-1')  # CSV file containing data type names, categories, and descriptions
    
    # Load the all_unique_target_info.csv file
    all_unique_target_info_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison\all_unique_target_info.csv'
    targets_df = pd.read_csv(all_unique_target_info_path)
    
    # Construct the output file path
    output_file_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison\matched_target_info_to_data_type.csv'
    
    # Call the matching function
    match_targets_to_data(targets_df, data_types_df, output_file_path)

if __name__ == "__main__":
    main()
