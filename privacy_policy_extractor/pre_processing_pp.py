from collections import defaultdict
import csv
import math
import os
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
from langdetect import detect

def removeUnneccessaryElements(soup):
    # Remove script, style, nav, footer, header, etc.
    for script in soup(["script", "style", "nav", "footer", "header", "img", "option", "select", "head", "button"]):
        script.extract()
    for div in soup.find_all("div", {'class':'footer'}):
        div.decompose()
    for div in soup.find_all("div", {'class': re.compile(r"sidebar")}):
        div.decompose()
    for div in soup.find_all("div", {'data-testid': re.compile(r"ax-navigation-menubar")}):
        div.decompose()
    for div in soup.find_all("div", {'class': re.compile(r"menu")}):
        div.decompose()
    for li in soup.find_all("li", {'class': re.compile(r"menu")}):
        li.decompose()
    for p in soup.find_all("p", {'class': re.compile(r"heading")}):
        p.decompose()
    for p in soup.find_all("p", {'class': re.compile(r"fw-bold")}):
        p.decompose()
    for ul in soup.find_all("ul", {'class': re.compile(r"menu")}):
        ul.decompose()
    for div in soup.find_all("div", {'class': re.compile(r"header")}):
        div.decompose()
    for div in soup.find_all("div", {'data-referrer': re.compile(r"page_footer")}):
        div.decompose()
    for div in soup.find_all("div", {'id':'footer'}):
        div.decompose()
    for div in soup.find_all("div", {'id': re.compile(r"sidebar")}):
        div.decompose()
    for div in soup.find_all("div", {'id': re.compile(r"menu")}):
        div.decompose()
    for li in soup.find_all("li", {'id': re.compile(r"menu")}):
        li.decompose()
    for ul in soup.find_all("ul", {'id': re.compile(r"menu")}):
        ul.decompose()
    for div in soup.find_all("div", {'id': re.compile(r"header")}):
        div.decompose()
    for div in soup.find_all("div", {'id': re.compile(r"breadcrumbs")}):
        div.decompose()
    for div in soup.find_all("div", {'id': re.compile(r"instagram")}):
        div.decompose()
    for div in soup.find_all("div", {'role': re.compile(r"navigation")}):
        div.decompose()
    for div in soup.find_all("div", {'role': re.compile(r"banner")}):
        div.decompose()
    for div in soup.find_all("div", {'role': re.compile(r"button")}):
        div.decompose()
    for div in soup.find_all("ul", {'role': re.compile(r"navigation")}):
        div.decompose()


# Load privacy policies
# Get the size of each file
# Mark PPs smaller than 2 KB or fewer than 200 words as low quality

visit_list = []
pp_language = {}

def pre_processing(pp_path):
    low_quality_pp = defaultdict(list)
    good_quality_count = 0
    languages = set()  # Used to store detected languages in the folder

    for file in tqdm(os.listdir(pp_path)):
        if file.endswith(".html"):
            if file not in visit_list:
                visit_list.append(file)
                # Open file
                with open(os.path.join(pp_path, file), 'r', encoding="utf-8") as f:
                    contents = f.read()
                    soup = BeautifulSoup(contents, "html.parser")
                    document = soup.get_text()

                    # Count words
                    tokens = re.split(r'; |, |\*|\n| ', document)
                    words = len([t for t in tokens if t.strip() != ''])

                    # Get file size
                    size = os.path.getsize(os.path.join(pp_path, file))
                    size = math.ceil(size / 1024)  # Convert to KB

                    # Identify low quality PPs
                    if size <= 2 or words <= 200:
                        # Group low quality files by month
                        month = file[:6]
                        low_quality_pp[month].append(file)
                    else:
                        good_quality_count += 1

                    # Detect language
                    try:
                        language = detect(document)
                        pp_language[file] = language
                        languages.add(language)
                    except:
                        pp_language[file] = "None"
                        languages.add("None")

    print(f"There are {sum(len(files) for files in low_quality_pp.values())} low quality privacy policies and {good_quality_count} good quality privacy policies in {os.path.basename(pp_path)}.")
    return low_quality_pp, good_quality_count, languages

def process_all_pp_folders(base_path, output_csv):
    # Initialize CSV with header
    header = ['Folder', 'Low Quality Count', 'Good Quality Count', 'Low Quality Policies by Month', 'Languages']
    if not os.path.exists(output_csv):
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            # Process each subfolder
            low_quality_pp, good_quality_count, languages = pre_processing(folder_path)

            # Format low quality summary by month
            month_files = {month: ', '.join(files) for month, files in low_quality_pp.items()}
            month_summary = [f"{month}: {len(files)} files" for month, files in low_quality_pp.items()]
            month_summary_str = '; '.join(month_summary)

            # Write results to CSV
            with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([folder, sum(len(files) for files in low_quality_pp.values()), good_quality_count, month_summary_str, ', '.join(languages)])

# Main entry
base_path = r"C:\Users\Softf\Desktop\Privacy Policies"
output_csv = os.path.join(base_path, 'low_quality_privacy_policy_analysis.csv')
process_all_pp_folders(base_path, output_csv)
