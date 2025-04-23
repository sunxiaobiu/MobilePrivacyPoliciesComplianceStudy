import os
import re
import time
import shutil
import random
import builtins
import logging
import csv
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains



# ======== Configuration (User Can Modify) ========
SAVE_FOLDER = r"C:\Users\Softf\Desktop\copyAPKMirror"

# List of apps to process: (app_id, category, pages_to_crawl)
APPS_TO_PROCESS = [
    ("com.lemon.lvoverseas", "capcut", 4),
    ("com_ubercab_eats", "uber-eats-food-delivery", 3),
    #("me_lyft_android", "lyft", 12),
]

CHROME_DRIVER_PATH = "chromedriver"  # Adjust if not in PATH
# ================================================

# Proxy Pool
proxy_list = [
    # "http://43.202.154.212:80", this one is not useful but you can add if you have a proxy pool
    # Add more
]

def get_random_proxy():
    if proxy_list:
        return random.choice(proxy_list)
    return None

# Rewrite the print function to output it to both the log file and the console simultaneously
# def print(*args, **kwargs):
    # Output the message to the console
    # builtins.print(*args, **kwargs)  # 使用 builtins.print 而不是 __builtins__.print
    # Output the message to the log file
    # message = " ".join(map(str, args))
    # logging.info(message)

def configure_driver(proxy=None):
    # Configure log level
    service = Service()
    service.log_path = os.devnull  # Ignore log output
    return webdriver.Chrome(service=service)

def fetch_with_retries(url, headers, max_retries=3, delay=10):
    """
    Try to fetch the URL with retries in case of failure.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                print(f"Rate limit hit. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(delay)  # Wait before retrying
            else:
                response.raise_for_status()  # Raise HTTPError for bad status codes
                return response
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request error occurred: {e}")
            break
    return None

def process_link(url):
    """Process the link to find the APK download link."""
    ua = UserAgent()
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        "Referer": "https://play.google.com/store/apps/details?id=com.google.android.gms&hl=zh",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "session_id=1234567890abcdef;",
    }
    
    response = fetch_with_retries(url, headers)
    
    if not response:
        print(f"Failed to retrieve page: {url}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    rows = soup.find_all('div', class_='table-row')
    apk_link = None
    
    for row in rows:
        try:
            badge = row.find('span', class_='apkm-badge')
            if badge and badge.get_text(strip=True) == 'APK':
                apk_link = row.find('a', class_='accent_color')['href']
                break
        except Exception as e:
            print(f"Error processing row: {e}")
    
    time.sleep(5)  # Wait for 5 seconds
    return apk_link

def get_first_apks_by_month(app_id, category, pages):
    first_apks = {}  # {"YYYY-MM": {date: datetime, link: str}}
    ua = UserAgent()

    for page in range(pages, 0, -1):  # From high to low
        url = f"https://www.apkmirror.com/uploads/page/{page}/?appcategory={category}"
        headers = {
            "User-Agent": ua.random,
            "Referer": "https://play.google.com/store/apps/details?id=com.google.android.gms&hl=zh",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            # "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cookie": "session_id=1234567890abcdef;"
        }
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        table_cells = soup.find_all('div', class_='table-cell')

        # Traverse the entries in each page from back to front
        for cell in reversed(table_cells):
            # Extract the APK link elements
            h5_element = cell.find('h5', class_='appRowTitle')
            if h5_element:
                apk_link_element = h5_element.find('a', class_='fontBlack')
                if apk_link_element:
                    # Extract the APK title and date elements
                    apk_title = apk_link_element.get_text()
                    date_element = cell.find('span', class_='dateyear_utc')
                    if date_element:
                        # Get the date and link
                        date_text = date_element['data-utcdate']
                        apk_link = apk_link_element['href']

                        # Filter out the versions containing "alpha" and "beta"
                        if 'beta' in apk_title.lower() or 'alpha' in apk_title.lower():
                            continue

                        # Convert the date to a datetime object
                        date_obj = datetime.strptime(date_text, '%m/%d/%Y %H:%M UTC')

                        # Extract the month and year
                        month_year = date_obj.strftime('%Y-%m')

                        # If it has not been dealt with in that month, record it
                        if month_year not in first_apks:
                            first_apks[month_year] = {
                                "date": date_obj,
                                "link": f"https://www.apkmirror.com{apk_link}"
                            }

    return first_apks

def selenium_download(download_url, save_path):
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": save_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    })
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)

    try:
        driver.get(download_url)
        time.sleep(3)
        go_button = driver.find_element("xpath", "//a[contains(text(),'Download APK')]")
        go_button.click()
        time.sleep(5)
    except Exception as e:
        print(f"Download failed: {e}")
    finally:
        driver.quit()

def save_apk_links(app_id, apk_dict):
    folder = os.path.join(SAVE_FOLDER, app_id, "APK LINKS")  # Create folder with app_id
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"apk_links.csv")
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Link"])
        writer.writeheader()
        for month, apk in sorted(apk_dict.items()):
            writer.writerow({
                "Date": apk["date"].strftime("%Y-%m-%d %H:%M"),
                "Link": apk["link"]
            })
    print(f"Saved CSV to {filepath}")

def read_csv(input_file):
    """Read csv and return contents."""
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
    return rows

def write_csv(output_file, rows):
    """Write the data to a CSV file and overwrite the old file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def write_row_append(filename, row, write_header=False):
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header and not file_exists:
            writer.writerow(["App Name", "Link", "APK Link"])
        writer.writerow(row)

def update_existing_rows(input_file, output_file, max_retries=3):
    """Update existing CSV file links with APK link if missing."""
    input_rows = read_csv(input_file)
    seen_links = set()
    if os.path.exists(output_file):
        existing_rows = read_csv(output_file)
    else:
        existing_rows = [input_rows[0] + ["APK Link"]]
        write_csv(output_file, existing_rows)

    for retry in range(max_retries):
        failed_rows = []

        for row in input_rows[1:]:
            link = row[1]
            if link in seen_links:
                continue

            apk_link = process_link(link)
            if apk_link:
                write_row_append(output_file, row + [apk_link])
            else:
                write_row_append(output_file, row + ['No suitable APK found'])
                failed_rows.append(row)

            seen_links.add(link)  # Record the processed links

        if not failed_rows:
            print("All links processed successfully!")
            break
        else:
            print(f"Retrying {len(failed_rows)} failed rows... ({retry + 1}/{max_retries})")
            input_rows = [input_rows[0]] + failed_rows

    if failed_rows:
        print(f"Some rows failed after {max_retries} retries.")

def move_latest_file(df, source_dir, dest_dir, row_index, apk_download_records):
    """Move the latest downloaded file to the target directory and update the download status"""
    time.sleep(200)  # Wait for the download to complete

    # Get all files in the download directory
    files = os.listdir(source_dir)
    if not files:
        print("Download directory is empty")
        df.loc[row_index, 'status'] = "Failed"
        return

    # Record the latest file's information
    latest_file = None
    latest_time = datetime.min

    # Iterate over all files to find the latest one
    for file in files:
        file_path = os.path.join(source_dir, file)
        if os.path.isfile(file_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time > latest_time:
                latest_time = file_mod_time
                latest_file = file_path

    if latest_file:
        # Check if the latest file is an APK file
        if latest_file.lower().endswith('.apk'):
            # Move the latest APK file
            shutil.move(latest_file, dest_dir)
            print(f"Moved APK file {os.path.basename(latest_file)} to {dest_dir}")
            df.loc[row_index, 'status'] = "Success"  # Update download status to success
        else:
            print(f"The latest file {os.path.basename(latest_file)} is not in APK format, skipping move")
            df.loc[row_index, 'status'] = "Failed"  # Update download status to failure
    else:
        print("No file found to move")
        df.loc[row_index, 'status'] = "Failed"  # Update download status to failure
    
    # Save the updated dataframe to CSV
    df.to_csv(apk_download_records, index=False)

def is_downloading(download_dir):
    """Check if the latest file in the download directory ends with '.crdownload'"""
    time.sleep(10)
    # Get all files in the download directory
    files = os.listdir(download_dir)
    if not files:
        return False
    
    # Get the latest file
    latest_file = max(
        (os.path.join(download_dir, f) for f in files),
        key=os.path.getmtime
    )
    print(latest_file)
    
    # Check if the latest file name ends with '.crdownload' or '.apk'
    if os.path.basename(latest_file).endswith('.crdownload') or os.path.basename(latest_file).endswith('.apk'):
        return True  # The latest file ends with '.crdownload' or '.apk', consider the download in progress or completed
    
    return False  # The latest file neither ends with '.crdownload' nor '.apk', consider the download not started or finished

def move_existing_files(default_download_directory, temp_dir):
    """
    Move .crdownload and .apk files to a temporary folder to prevent them from interfering with future downloads.
    """
    files = os.listdir(default_download_directory)
    for file in files:
        file_path = os.path.join(default_download_directory, file)
        if os.path.isfile(file_path) and (file.endswith('.crdownload') or file.endswith('.apk')):
            print(f"Found existing download file: {file}, moving it to the temporary folder.")
            shutil.move(file_path, os.path.join(temp_dir, file))

def prepare_for_new_download(default_download_directory, folder_path):
    """
    Clean up existing download files before starting a new download, move them to the temp_apks folder under folder_path.
    """
    # Create the temp_apks folder
    temp_apks_path = os.path.join(folder_path, 'temp_apks')
    os.makedirs(temp_apks_path, exist_ok=True)

    # Move existing .crdownload and .apk files to the temp_apks folder
    move_existing_files(default_download_directory, temp_apks_path)

def click_checkbox_with_retries(driver, download_dir, max_retries=3, wait_time=120):
    """
    Attempt to click the checkbox multiple times until successful or the maximum retries are reached.
    
    :param driver: Selenium WebDriver instance
    :param download_dir: Download directory
    :param max_retries: Maximum number of retries
    :param wait_time: Time to wait between retries (in seconds)
    """
    for attempt in range(max_retries):
        if is_downloading(download_dir):
            return True
        try:
            print(f"Attempt {attempt + 1} to click the checkbox...")
            
            # Wait for the checkbox to be clickable
            checkbox = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.cb-lb input[type="checkbox"], .cb-i input[type="checkbox"]'))
            )
            
            # Perform the click action
            actions = ActionChains(driver)
            actions.move_to_element(checkbox).click().perform()
            print("Clicked the checkbox.")

            if is_downloading(download_dir):
                return True
            
            # Check if the checkbox is selected
            if checkbox.is_selected():
                print("The checkbox is already selected.")
            else:
                print("The checkbox wasn't selected after clicking, trying again...")
        
        except Exception as e:
            print(f"Failed to click the checkbox: {e}")
        
        if is_downloading(download_dir):
            return True
        # Wait some time before retrying
        time.sleep(wait_time)
    
    print("All click attempts failed.")
    return False


def download_apk(df, row, driver, folder_path, apk_download_records):
    base_url = "https://www.apkmirror.com"  # Website URL
    time_str = row['Date']  # Date column
    partial_url = row['APK Link']  # Third column: partial URL

    # Check if there is a valid URL and it's a string
    if not isinstance(partial_url, str) or partial_url == "No suitable APK found":
        print(f"Invalid APK link: {partial_url}")
        return False
    full_url = base_url + partial_url

    # Parse the date
    try:
        date_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        folder_name = date_time.strftime('%Y%m')
    except ValueError:
        print(f"Incorrect date format: {time_str}")
        return False

    # Create a folder based on the time
    time_folder_path = os.path.join(folder_path, folder_name)
    os.makedirs(time_folder_path, exist_ok=True)

    try:
        # Use Selenium to access the webpage
        driver.get(full_url)

        # Wait for the page to load
        time.sleep(10)  # Adjust the wait time accordingly
        
        # Get the page content
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Find the download link
        download_link_tag = soup.find('a', {'class': 'downloadButton'})
        if download_link_tag:
            download_link = download_link_tag['href']
            print(f"Found download link: {download_link}")
        else:
            print(f"Could not find download link: {full_url}")
            time.sleep(30)
            return False

        # Full download link
        download_url = base_url + download_link
        print(f"Full download link: {download_url}")

        # Store the download link in the fourth column of the CSV
        df.loc[row.name, 'download'] = download_url
        # Update the CSV file
        df.to_csv(apk_download_records, index=False)
        print(f"Data saved to: {apk_download_records}")

        # Move the downloaded file to the target folder
        default_download_directory = os.path.expanduser('~/Downloads')

        # Clean up existing download files by moving them to the temp_apks folder
        prepare_for_new_download(default_download_directory, folder_path)

        # Use Selenium to download the file
        driver.get(download_url)

        try:
            # Check if a file is already downloading
            if is_downloading(default_download_directory):
                print("A file is already downloading.")
            else:
                # If no file is downloading, wait and click the button to complete verification
                if click_checkbox_with_retries(driver, default_download_directory):
                    print("Verification step completed.")
                else:
                    print("Checkbox verification failed, unable to continue download.")
                    return False
        
        except Exception as e:
            print("Error during verification:", e)
        
        time.sleep(120)
        # Move the downloaded file to the target folder
        move_latest_file(df, default_download_directory, time_folder_path, row.name, apk_download_records)

        print(f"Download completed and moved to: {time_folder_path}")
        return True

    except Exception as e:
        print(f"Error during download process: {e}")
        df.loc[row.name, 'status'] = "Failed"  # Update download status to failed
        return False

def main():
    for app_id, category, pages in APPS_TO_PROCESS:
        print(f"\n===== Processing {app_id} ({category}), {pages} page(s) =====")
        
        # Dynamically set the APK save folder for each app
        APK_SAVE_FOLDER = os.path.join(SAVE_FOLDER, app_id, "APK LINKS", "apkmirror2", "apk")  # Using app_id to create folder structure
        os.makedirs(APK_SAVE_FOLDER, exist_ok=True)

        # Path for the existing and output CSV
        apk_links = os.path.join(SAVE_FOLDER, app_id, "APK LINKS", "apk_links.csv")  # apk_links
        apk_download_links = os.path.join(SAVE_FOLDER, app_id, "APK LINKS", "apk_links_output.csv")  # apk_download_links

        # Fetch first APK links by month
        # apk_dict = get_first_apks_by_month(app_id, category, pages)
        # save_apk_links(app_id, apk_dict)

        # Get download links from apk links
        # update_existing_rows(apk_links, apk_download_links)

        # Logs
        # log_file_path = os.path.join(SAVE_FOLDER, app_id, "APK LINKS", "apk_download_log.txt")
        # logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

        apk_download_records = os.path.join(SAVE_FOLDER, app_id, "APK LINKS", "apk_links_with_downloads.csv")
        if os.path.exists(apk_download_records):
            df = pd.read_csv(apk_download_records)
            print(f"Read the existing download record file:{apk_download_records}")
        else:
            # If the file does not exist, read the initial CSV file
            df = pd.read_csv(apk_download_links)
            df['download'] = ""
            df['status'] = ""  # The newly added column is used to save the download status
            print(f"The existing download record file was not found. Load the initial data and create a new file:{apk_download_records}")

        max_retries = 3

        # Process the data in the CSV file line by line
        for retry in range(max_retries):
            print("Start downloading...")

            # Obtain a random agent
            proxy = get_random_proxy()
            if proxy:
                print(f"Use an agent: {proxy}")
            else:
                print("No agent was used.")

            # Configure the Selenium driver
            driver = configure_driver(proxy)

            # Record the rows that failed in the current attempt
            failed_rows = df[df['status'] != "Success"].index.tolist()

            for index in failed_rows:
                row = df.loc[index]
                success = download_apk(df, row, driver, APK_SAVE_FOLDER, apk_download_records)
                if not success:
                    continue

            driver.quit()

            # Record the rows that failed in the current attempt
            failed_rows = df[df['status'] != "Success"].index.tolist()

            # If there are no failed rows, end the loop
            if not failed_rows:
                print("All APK downloads have been completed")
                break
            else:
                print(f"本次下载失败的链接数量: {len(failed_rows)}")

            # Update the CSV file
            df.to_csv(apk_download_records, index=False)

            # Wait for a period of time before starting the next cycle
            time.sleep(30)

if __name__ == '__main__':
    main()





