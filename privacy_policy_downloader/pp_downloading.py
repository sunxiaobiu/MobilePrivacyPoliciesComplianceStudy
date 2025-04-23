import os
import re
import requests
import time
import random
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Function to save webpage as HTML
def save_webpage_as_html(url):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.google.com/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    return response.url

# Function to try different archive dates to fetch the correct URL
def fetch_correct_url(base_url, year, month):
    days_to_try = [15, 10, 30]  # Try the 15th, 10th, and 30th
    for day in days_to_try:
        archive_date = f"{year}{month:02}{day:02}000000"
        url = base_url.replace('00000000000000', archive_date)
        print(url)
        final_url = save_webpage_as_html(url)
        
        if final_url:
            print(final_url)
            final_month = re.search(r'web/(\d{8})(\d{6})/', final_url).group(1)[4:6]
            if final_month == f"{month:02}":
                return final_url

    print(f"Could not find a valid redirect URL for {year}-{month:02}.")
    time.sleep(random.uniform(30, 40))
    return None

# Function to save the HTML file with retries if request fails
def save_html_with_retries(final_url, file_path, max_retries=5):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(final_url, headers=headers)
            response.raise_for_status()  # Check for request success
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Saved HTML for {os.path.basename(file_path)}")
            time.sleep(random.uniform(30, 40))
            return
        except requests.exceptions.RequestException as e:
            retries += 1
            print(f"Attempt {retries} failed: {e}")
            time.sleep(random.uniform(30, 40))

    print(f"Failed to save HTML after {max_retries} attempts.")

# Function to save the final HTML file using the final URL
def save_final_html(final_url, year_month, output_base_dir, app_id):
    if final_url:
        match = re.search(r'web/(\d{8})(\d{6})/', final_url)
        if not match:
            print("No valid timestamp found in the final URL")
            return

        date_part = match.group(1)
        time_part = match.group(2)

        filename = f'{date_part}_{time_part}.html'
        app_id_folder = app_id.replace('.', '_')  # Replace dots with underscores
        output_dir = os.path.join(output_base_dir, app_id_folder)  # Use appID for folder
        file_path = os.path.join(output_dir, filename)

        os.makedirs(output_dir, exist_ok=True)

        save_html_with_retries(final_url, file_path)

# Function to fetch and save HTML for each month within the date range
def fetch_and_save_html(start_date, end_date, base_url, save_dir, exclude_months, app_id):
    start_year = int(start_date[:4])
    start_month = int(start_date[4:])
    end_year = int(end_date[:4])
    end_month = int(end_date[4:])
    
    current_year = start_year
    current_month = start_month
    
    while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
        year_month = f"{current_year}{current_month:02}"
        output_dir = os.path.join(save_dir, year_month)

        # Check if the current month is in the skip list
        if current_year in exclude_months and current_month in exclude_months[current_year]:
            print(f"Skipping {current_year}-{current_month:02}")
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1
            continue
        
        # Check if the folder exists
        if os.path.exists(output_dir):
            print(f"Directory {output_dir} already exists, checking for HTML files.")

            # List all files in the directory
            existing_files = os.listdir(output_dir)
            
            # Filter out any .html files
            html_files = [f for f in existing_files if f.endswith('.html')]
            
            if html_files:
                print(f"HTML files already exist in {output_dir}, skipping this month.")
            else:
                print(f"No HTML files in {output_dir}, starting download.")
                final_url = fetch_correct_url(base_url, current_year, current_month)
                if final_url:
                    save_final_html(final_url, year_month, save_dir, app_id)
        else:
            print(f"Directory {output_dir} does not exist, creating directory and downloading data.")
            final_url = fetch_correct_url(base_url, current_year, current_month)
            if final_url:
                save_final_html(final_url, year_month, save_dir, app_id)
        
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1

# Main function to run the process for each app in the CSV file
def main():
    # Load the CSV file containing appID and privacyPolicyLink
    df = pd.read_csv('apps_info.csv', encoding='latin-1')  # Update with your CSV file path
    base_url = 'https://web.archive.org/web/00000000000000/https://www.indeed.com/legal'
    save_dir = 'C:\\Users\\Softf\\Desktop\\Privacy Policies'
    start_date = '201708'
    end_date = '202409'
    exclude_months = {}  # Add any months to skip if necessary

    for index, row in df.iterrows():
        app_id = row['appID']  # Get appID from the CSV
        privacy_policy_link = row['privacyPolicyLink']  # Get the privacy policy link
        formatted_link = f"https://web.archive.org/web/00000000000000/{privacy_policy_link.split('://')[1]}"
        
        print(f"Processing {app_id} with link {formatted_link}")
        fetch_and_save_html(start_date, end_date, formatted_link, save_dir, exclude_months, app_id)

# Run the main function
if __name__ == "__main__":
    main()
