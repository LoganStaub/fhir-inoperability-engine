import json
import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data", "synthea_sample_data_fhir_latest")


def first_value(value):
    """Return the first item from a FHIR list, or the value itself."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def get_nested(resource, *keys):
    """Read a nested FHIR value and return None when a path is absent."""
    value = resource
    for key in keys:
        if not isinstance(value, (dict, list)):
            return None
        try:
            value = value[key]
        except (KeyError, IndexError, TypeError):
            return None
    return value


def load_resources():
    resources = []

    for file_name in sorted(os.listdir(DATA_FOLDER)):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(DATA_FOLDER, file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            bundle = json.load(file)

        if bundle.get("resourceType") != "Bundle":
            continue

        resources.extend(
            entry["resource"]
            for entry in bundle.get("entry", [])
            if isinstance(entry, dict) and isinstance(entry.get("resource"), dict)
        )

    return resources


def extract_dataframes(resources):
    patients = []
    encounters = []
    conditions = []

    for resource in resources:
        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            patients.append(
                {
                    "id": resource.get("id"),
                    "birthDate": resource.get("birthDate"),
                    "gender": resource.get("gender"),
                    "given": first_value(get_nested(resource, "name", 0, "given")),
                    "family": get_nested(resource, "name", 0, "family"),
                    "postalCode": get_nested(resource, "address", 0, "postalCode"),
                }
            )
        elif resource_type == "Encounter":
            encounters.append(
                {
                    "id": resource.get("id"),
                    "subject_reference": get_nested(resource, "subject", "reference"),
                    "period_start": get_nested(resource, "period", "start"),
                    "period_end": get_nested(resource, "period", "end"),
                    "type_code": get_nested(resource, "type", 0, "coding", 0, "code"),
                }
            )
        elif resource_type == "Condition":
            conditions.append(
                {
                    "id": resource.get("id"),
                    "subject_reference": get_nested(resource, "subject", "reference"),
                    "recordedDate": resource.get("recordedDate"),
                    "code": get_nested(resource, "code", "coding", 0, "code"),
                }
            )

    patient_df = pd.DataFrame(
        patients,
        columns=["id", "birthDate", "gender", "given", "family", "postalCode"],
    )
    encounter_df = pd.DataFrame(
        encounters,
        columns=["id", "subject_reference", "period_start", "period_end", "type_code"],
    )
    condition_df = pd.DataFrame(
        conditions,
        columns=["id", "subject_reference", "recordedDate", "code"],
    )

    return patient_df, encounter_df, condition_df


resources = load_resources()
patient_df, encounter_df, condition_df = extract_dataframes(resources)

print(f"Loaded {len(resources)} FHIR resources from: {DATA_FOLDER}")
print(f"Patient DataFrame: {patient_df.shape}")
print(f"Encounter DataFrame: {encounter_df.shape}")
print(f"Condition DataFrame: {condition_df.shape}")
