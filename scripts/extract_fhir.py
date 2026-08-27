import os
import json
import pandas as pd

# Set up the base directory and data folder path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, 'data', 'synthea_sample_data_fhir_latest')

print(f"Looking for FHIR data in: {DATA_FOLDER}")

# Loop through all files in the data folder and load JSON files
file_count = 0
for file_name in os.listdir(DATA_FOLDER):

    if file_name.endswith('.json'):
        file_path = os.path.join(DATA_FOLDER, file_name)

        with open(file_path, 'r', encoding='utf-8') as f:
            patient_data = json.load(f)

            print(f"Succesfully loaded: {file_name} | Type: {patient_data.get('resourceType')}")

            file_count += 1

print(f"\nFinished looping; Total files verified: {file_count}")