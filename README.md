# The Seven-Year Itch: A Chronological Empirical Study of (In)Compliance between Privacy Policies and Android Applications from 2017 to 2024

This repository contains the official implementation for the paper:

**"The Seven-Year Itch: A Chronological Empirical Study of (In)Compliance between Privacy Policies and Android Applications from 2017 to 2024"**

## Project Overview

This Python-based project provides a complete framework for collecting Android APKs and their associated privacy policies, and mapping them to a set of user-defined **data types**. The purpose is to facilitate a longitudinal empirical analysis of **(in)compliance** between mobile applications and their privacy policies from 2017 to 2024.

Key highlights:
- APKs are collected from [APKMirror](https://www.apkmirror.com/)
- Privacy policies are archived from the [Wayback Machine](https://archive.org/web/)
- APKs are analyzed with **Androguard**
- Privacy policies are processed with **PoliGraph**
- Both permission and policy data are mapped to standardized **data types** using the **OpenAI API**

---

## Project Structure

```
.
├── apk_downloader/                        # Script to download APKs from APKMirror
│   └── apk_downloader.py
│
├── apk_permission_extractor/             # Extracts permissions using Androguard and map them to data types
│   ├── extract_apk_permissions.py
│   ├── step1_store_apk_permission_in_csv.py
│   ├── step2_collect_all_permissions_in_1_app.py
│   ├── step3_allPermissions_save_to_one_csv.py
│   ├── step4_add_description.py
│   └── step5_permission_dataType_compare_prompt.py
│
├── privacy_policy_downloader/            # Download privacy policies from Wayback Machine
│   └── pp_downloading.py
│
├── privacy_policy_extractor/             # Extract and process structured policy data using PoliGraph
│   ├── pre_processing_pp.py              # Preprocess policy texts and identify low quality privacy policies before feeding into PoliGraph
│   ├── run_poligraph.py
│   ├── step1_poligraph_preprocessing.py
│   ├── step2_txtPP_to_csvPP.py
│   ├── step3_csvPP_timeline_comparison.py
│   ├── step4_allPP_for_one_app.py
│   ├── step5_allPP_save_to_one_csv.py
│   └── step6_turn_pp_into_dataType_prompt.py

```

---

## Installation & Setup

### Requirements

- Python 3.8+
- Google Chrome
- ChromeDriver (matching your Chrome version)

### Python Dependencies

All necessary dependencies have been listed in the requirements.txt file.
To install them, simply run:

`pip install -r requirements.txt`

## How to Run

### Download APKs

`python apk_downloader/apk_downloader.py`

### Extract APK Permissions

Please download Androguard from <https://github.com/androguard/androguard>. You can also install it via pip:

 `pip install Androguard`. 
 
 Put this `extract_apk_permissions.py` python file into the Androguard file. Then run:

`python androguard-master/extract_apk_permissions.py`

### Map APK Permissions to Data Types (via OpenAI)

Run the following scripts in order from the `apk_permission_extractor/` folder:
```
python apk_permission_extractor/step1_store_apk_permission_in_csv.py
python apk_permission_extractor/step2_collect_all_permissions_in_1_app.py
python apk_permission_extractor/step3_allPermissions_save_to_one_csv.py
python apk_permission_extractor/step4_add_description.py
python apk_permission_extractor/step5_permission_dataType_compare_prompt.py
```

### Download Privacy Policies

`python privacy_policy_downloader/pp_downloading.py`

### Extract Policy Information

Before running PoliGraph, preprocess the policy text files:

`python privacy_policy_extractor/pre_processing_pp.py`

Please download PoliGraph from <https://github.com/UCI-Networking-Group/PoliGraph> and put `run_poligraph.py` into the PoliGraph directory, then run:

`python PoliGraph-master/run_poligraph.py`

### Map Policy Info to Data Types (via OpenAI)

Run the following scripts in order from the `privacy_policy_extractor/` folder:
```
python privacy_policy_extractor/step1_poligraph_preprocessing.py
python privacy_policy_extractor/step2_txtPP_to_csvPP.py
python privacy_policy_extractor/step3_csvPP_timeline_comparison.py
python privacy_policy_extractor/step4_allPP_for_one_app.py
python privacy_policy_extractor/step5_allPP_save_to_one_csv.py
python privacy_policy_extractor/step6_turn_pp_into_dataType_prompt.py
```

## Dataset

This dataset contains the log information generated during the matching and processing of Android APKs and their associated privacy policies. The data is stored in a CSV file called **`app_data_log.csv`**, which contains one row for each app at a given time (snapshot date).

Each row in the CSV corresponds to a unique `app_id` and its respective `time` (snapshot date), representing the processed APK and privacy policy pair. The key columns in the dataset and their meanings are as follows:

### Columns

1. **app_id**:  
   - A unique identifier for the application, typically the package name of the app.

2. **time**:  
   - The timestamp or folder name that represents the snapshot date (e.g., "202309").

3. **causeOfFailure**:  
   - Indicates the reason for any failure during the matching or processing pipeline.
   - **Values** and their meanings:
     - `5`: **Success** – Both APK and privacy policy were matched and processed successfully.
     - `1`: **Failed to download APK** – The APK could not be downloaded from APKMirror.
     - `2`: **Failed to retrieve privacy policy** – The privacy policy could not be retrieved from the Wayback Machine.
     - `3`: **Failed during APK extraction** – The APK extraction process failed with Androguard.
     - `4`: **Failed during privacy policy extraction** – The privacy policy extraction failed with PoliGraph.

4. **apk_permissions_categories_dataTypes_distribution**:  
   - A dictionary (stored as a string) representing the presence of data types as inferred from the APK's declared permissions. Each key in the dictionary corresponds to a specific permission category, and the value can be one of:
     - `True`: The data type is present (i.e., the APK requests this permission).
     - `False`: The data type is not present (i.e., the APK does not request this permission).
     - `-`: At least one of the APK or privacy policy is missing for this data type.

5. **privacy_policies_categories_dataTypes_distribution**:  
   - A dictionary (stored as a string) representing the presence of data types as inferred from the privacy policy text. Similar to the APK permissions, the values can be:
     - `True`: The data type is mentioned in the privacy policy.
     - `False`: The data type is not mentioned in the privacy policy.
     - `-`: At least one of the APK or privacy policy is missing for this data type.

### Example Row

| app_id         | time   | apk_permissions_categories_dataTypes_distribution | privacy_policies_categories_dataTypes_distribution | causeOfFailure |
|----------------|--------|----------------|--------------------------------------------------|----------------------------------------------------|
| com.example.app | 202309 | {"Address": "T", "App interactions": "F", "Approximate location": "F" ...} | {"Address": "-", "App interactions": "-", "Approximate location": "-" ...} | 5              | 

---

This structure provides an overview of each app's matching status, as well as the corresponding permissions and privacy policy data types for that snapshot date.
