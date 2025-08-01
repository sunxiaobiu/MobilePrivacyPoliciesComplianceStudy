import openai
import pandas as pd
import os
import time
import csv

# Set your OpenAI API key
openai.api_key = "" # your api_key

# Function to get a matched data type using ChatCompletion
def match_permission_to_data_type(permission_description, data_types):
    data_types_description = "\n".join([f"{data_type} ({category}) - {desc}" for data_type, category, desc in data_types])
    messages = [
        {
            "role": "system", 
            "content": "You are a helpful assistant that maps Android permissions to privacy-related data types."
        },

        {
            "role": "user", 
            "content": (
                    f"You are an assistant that matches Android permission to data types."
                    f"The permission description is: {permission_description}"
                    f"Here are the available data types and their descriptions:\n{data_types_description}\n"
                    f"Respond with the best match as a single data type name, without any extra explanation or category name."
                    f"If you think there is no matching data type, then strictly respond 'No Match'."
                )
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0
    )

    # Extract and return the matching data type
    match = response['choices'][0]['message']['content'].strip()
    
    # Confirm whether the matched content is in the data type list
    valid_data_types = {dt[0] for dt in data_types}  # Extract the name of the data type
    if match == "No match found":
        return "No match found"
    elif match not in valid_data_types:
        return "Not valid"
    else:
        return match

# Matching logic
def match_permissions_to_data(permissions_df, data_types_df, output_file_path):
    data_types = list(zip(data_types_df['data_type_name'], data_types_df['category_name'], data_types_df['description']))
    
    # Check whether the output file exists
    file_exists = os.path.exists(output_file_path)

    # Open the CSV file
    with open(output_file_path, 'a', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # If the file does not exist, write to the table header
        if not file_exists:
            writer.writerow(['permission_name', 'permission_description', 'matched_data_type'])
        
        # Start processing the lines that have never been processed
        for i, perm_row in permissions_df.iterrows():
            perm_name = perm_row['all_unique_permissions']
            perm_desc = perm_row['Description'] if not pd.isna(perm_row.get('Description')) else perm_name
            matched_data_type = match_permission_to_data_type(perm_desc, data_types)
            writer.writerow([perm_name, perm_desc, matched_data_type])
            if (i + 1) % 300 == 0:
                print(f"Line {i + 1} has been processed. Take a 1-minute break...")
                time.sleep(60)

    print(f"The matching is completed. The results have been saved to '{output_file_path}' in real time.")

# Main function
def main():
    data_types_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\PPpoligraphDataAndComparison\data_types.csv'
    data_types_df = pd.read_csv(data_types_path, encoding='ISO-8859-1')
    
    all_unique_permissions_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\APKPermissionsandComparison\permission_with_description.csv'
    permissions_df = pd.read_csv(all_unique_permissions_path)

    output_file_path = r'C:\Users\Softf\Desktop\new hp computer\PP Project\APKPermissionsandComparison\matched_permissions_to_data_type.csv'
    match_permissions_to_data(permissions_df, data_types_df, output_file_path)

if __name__ == "__main__":
    main()
