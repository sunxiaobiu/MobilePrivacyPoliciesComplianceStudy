#!/usr/bin/env python3
import os
import subprocess
import csv

# Define the main directory containing HTML files and the output directory
base_directory = r"/mnt/c/Users/Softf/Desktop/Privacy Policies"
output_base_directory = r"/mnt/c/Users/Softf/Desktop/Privacy_Policy_PoliGraph"
low_quality_file = r"/mnt/c/Users/Softf/Desktop/low_quality_privacy_policy_analysis.csv"

# Read low-quality privacy policy records and build a dictionary for quick lookup
low_quality_policies = {}

with open(low_quality_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        folder_name = row['Folder']
        months = row['Low Quality Policies by Month']
        # Parse month information into a set for quick lookup
        months_set = set(month.split(':')[0] for month in months.split('; '))
        low_quality_policies[folder_name] = months_set

# Ensure the output base directory exists
os.makedirs(output_base_directory, exist_ok=True)

# Iterate through each subfolder
for folder_name in os.listdir(base_directory):
    folder_path = os.path.join(base_directory, folder_name)
    
    # Ensure it's a directory
    if os.path.isdir(folder_path):
        print(f"Processing folder: {folder_name}")

        # Check whether this folder is in the low-quality list
        low_quality_months = low_quality_policies.get(folder_name, set())

        # Iterate through all HTML files in the folder
        for html_file in os.listdir(folder_path):
            if html_file.endswith('.html'):
                html_file_path = os.path.join(folder_path, html_file)
                output_dir = os.path.join(output_base_directory, folder_name, os.path.splitext(html_file)[0])
                
                # Use the first six characters of the file name as the year-month info
                file_month = html_file[:6]

                # Skip low-quality files
                if file_month in low_quality_months:
                    print(f"{html_file} is marked as low quality for {file_month}. Skipping this file.")
                    continue

                # Skip if output directory already exists for this HTML file
                if os.path.exists(output_dir):
                    print(f"Output directory already exists for {html_file}. Skipping this file.")
                    continue

                # Ensure the output directory for each HTML file exists
                os.makedirs(output_dir, exist_ok=True)

                # List of commands to run
                commands = [
                    f'conda activate poligraph',
                    f'python -m poligrapher.scripts.html_crawler "{html_file_path}" "{output_dir}/"',
                    f'python -m poligrapher.scripts.init_document "{output_dir}/"',
                    f'python -m poligrapher.scripts.run_annotators "{output_dir}/"',
                    f'python -m poligrapher.scripts.build_graph "{output_dir}/"',
                    f'python -m poligrapher.scripts.build_graph --pretty "{output_dir}/"'
                ]

                for command in commands:
                    try:
                        # Use shell=True to allow conda environment activation
                        result = subprocess.run(command, shell=True, check=True)
                        print(f'Command "{command}" executed successfully.')
                    except subprocess.CalledProcessError as e:
                        print(f'Error occurred while executing "{command}": {e}')
                
                print(f"Finished processing file: {html_file} in folder: {folder_name}")
        print(f"Finished processing folder: {folder_name}")
