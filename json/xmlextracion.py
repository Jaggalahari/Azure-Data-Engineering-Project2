import os
import csv
import xml.etree.ElementTree as ET

# ============================================
# Paths
# ============================================

xml_folder = r"C:\Users\User\Downloads\azure_practice_data\xml"

report_folder = r"C:\Users\User\Downloads\azure_practice_data\reports"

if not os.path.exists(report_folder):
    os.makedirs(report_folder)

structure_report_path = os.path.join(
    report_folder,
    "xml_structure_report.txt"
)

extraction_report_path = os.path.join(
    report_folder,
    "xml_extraction_report.csv"
)

schema_report_path = os.path.join(
    report_folder,
    "xml_schema_report.csv"
)

validation_report_path = os.path.join(
    report_folder,
    "xml_validation_report.txt"
)

# ============================================
# Global Variables
# ============================================

all_records = []
schema_tags = set()
xml_structures = {}

# ============================================
# Recursive Extraction
# ============================================

def extract_xml(element,
                level=0,
                structure_lines=None,
                data_dict=None,
                tag_set=None):

    value = ""

    if element.text and element.text.strip():
        value = element.text.strip()

    # Structure report
    if structure_lines is not None:
        structure_lines.append(
            "    " * level + f"{element.tag}: {value}"
        )

    # Leaf nodes only
    if len(element) == 0:

        if data_dict is not None:
            data_dict[element.tag] = value

        schema_tags.add(element.tag)

        if tag_set is not None:
            tag_set.add(element.tag)

    # Recursive
    for child in element:
        extract_xml(
            child,
            level + 1,
            structure_lines,
            data_dict,
            tag_set
        )


# ============================================
# Structure Report
# ============================================

try:

    with open(structure_report_path, "w", encoding="utf-8") as structure_file:

        for filename in os.listdir(xml_folder):

            if filename.lower().endswith(".xml"):

                print("Processing :", filename)

                file_path = os.path.join(xml_folder, filename)

                try:

                    tree = ET.parse(file_path)
                    root = tree.getroot()

                    structure_lines = []

                    record = {
                        "FileName": filename
                    }

                    tag_set = set()

                    extract_xml(
                        root,
                        structure_lines=structure_lines,
                        data_dict=record,
                        tag_set=tag_set
                    )

                    xml_structures[filename] = tag_set

                    all_records.append(record)

                    structure_file.write("\n")
                    structure_file.write("=" * 100 + "\n")
                    structure_file.write(f"FILE : {filename}\n")
                    structure_file.write("=" * 100 + "\n")

                    for line in structure_lines:
                        structure_file.write(line + "\n")

                except Exception as e:
                    print("Error processing", filename, ":", e)

except PermissionError:
    print("\nClose xml_structure_report.txt and rerun.")
    exit()

# ============================================
# Extraction Report
# ============================================

fieldnames = set()

for row in all_records:
    fieldnames.update(row.keys())

fieldnames = sorted(fieldnames)

try:

    with open(extraction_report_path,
              "w",
              newline="",
              encoding="utf-8") as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in all_records:
            writer.writerow(row)

except PermissionError:
    print("\nClose xml_extraction_report.csv and rerun.")
    exit()

# ============================================
# Schema Report
# ============================================

try:

    with open(schema_report_path,
              "w",
              newline="",
              encoding="utf-8") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow(["Tag_Name"])

        for tag in sorted(schema_tags):
            writer.writerow([tag])

except PermissionError:
    print("\nClose xml_schema_report.csv and rerun.")
    exit()

# ============================================
# Validation Report
# ============================================

validation_status = "SUCCESS"

reference_file = list(xml_structures.keys())[0]
reference_structure = xml_structures[reference_file]

try:

    with open(validation_report_path,
              "w",
              encoding="utf-8") as f:

        f.write("=" * 80 + "\n")
        f.write("XML STRUCTURE VALIDATION REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Reference XML : {reference_file}\n")
        f.write(f"Total XML Files : {len(xml_structures)}\n\n")

        mismatch_found = False

        for file, structure in xml_structures.items():

            if structure != reference_structure:

                mismatch_found = True
                validation_status = "FAILURE"

                missing_tags = reference_structure - structure
                extra_tags = structure - reference_structure

                f.write(f"\nMismatch XML : {file}\n")

                if missing_tags:

                    f.write("\nMissing Tags:\n")

                    for tag in sorted(missing_tags):
                        f.write(tag + "\n")

                if extra_tags:

                    f.write("\nExtra Tags:\n")

                    for tag in sorted(extra_tags):
                        f.write(tag + "\n")

        if not mismatch_found:

            f.write("\nSUCCESS\n")
            f.write("All XML files have identical structure.\n")

except PermissionError:
    print("\nClose xml_validation_report.txt and rerun.")
    exit()

# ============================================
# Console Output
# ============================================

print("\n" + "=" * 60)

if validation_status == "SUCCESS":

    print("SUCCESS")
    print("All XML files have identical structure.")

else:

    print("FAILURE")
    print("Structure mismatch found.")

print("\nTotal XML Files :", len(xml_structures))

print("\nReports Location:")
print(report_folder)

print("=" * 60)