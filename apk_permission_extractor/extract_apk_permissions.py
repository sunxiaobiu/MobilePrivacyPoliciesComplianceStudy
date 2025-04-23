import os
from androguard.core.apk import APK

def analyze_apk_permissions(input_apk_path, output_txt_path):
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_txt_path)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Load the APK file
        apk = APK(input_apk_path)
        permissions = apk.get_permissions()

        # Write permissions info to the output TXT file
        with open(output_txt_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f"APK File: {input_apk_path}\n\n")
            output_file.write("Permissions:\n")
            for permission in permissions:
                output_file.write(f"{permission}\n")

        print(f"Permission analysis completed and saved to {output_txt_path}")
    except Exception as e:
        print(f"Error processing {input_apk_path}: {e}")

def traverse_apk_files(base_folder):
    # Create the output folder for storing APK permissions (same level as base_folder)
    permissions_folder = os.path.join(base_folder, "apk_permissions")
    os.makedirs(permissions_folder, exist_ok=True)

    # Traverse each month-level folder inside base_folder
    for month_folder in os.listdir(base_folder):
        month_path = os.path.join(base_folder, month_folder)
        
        if os.path.isdir(month_path):
            output_month_folder = os.path.join(permissions_folder, month_folder)

            # Skip this month if TXT files already exist
            if os.path.exists(output_month_folder) and any(f.endswith('.txt') for f in os.listdir(output_month_folder)):
                print(f"Skipping {month_folder}, permission files already exist.")
                continue

            os.makedirs(output_month_folder, exist_ok=True)

            # Traverse APK files in the current month folder
            for file_name in os.listdir(month_path):
                if file_name.endswith('.apk'):
                    apk_path = os.path.join(month_path, file_name)
                    output_txt_path = os.path.join(output_month_folder, f"{file_name}.txt")

                    # Extract permission info
                    analyze_apk_permissions(apk_path, output_txt_path)

# List of app folders to process
base_folders = [
    r"C:\Users\Softf\Desktop\APKMirror\com_peacocktv_peacockandroid\APK LINKS\apkmirror2\apk",
    r"C:\Users\Softf\Desktop\APKMirror\com_reddit_frontpage\APK LINKS\apkmirror2\apk",
    r"C:\Users\Softf\Desktop\APKMirror\com_zzkko\APK LINKS\apkmirror2\apk",
    r"C:\Users\Softf\Desktop\APKMirror\com_snapchat_android\APK LINKS\apkmirror2\apk",
    r"C:\Users\Softf\Desktop\APKMirror\com_walmart_android\APK LINKS\apkmirror2\apk",
    r"C:\Users\Softf\Desktop\APKMirror\com_whatsapp\APK LINKS\apkmirror2\apk",
    # Add more APK folders as needed
]

# Run permission extraction for each folder
for base_folder in base_folders:
    traverse_apk_files(base_folder)
