# Split the report into lines
import re
import pprint


deletable_strings = ['St Boniface General Hospital Confidential Page:', 'End of Report', 'SBGH-']

lab_string = ""

patient_labs = {}

skip_keys = ['Urea/Creatinine']

lab_name = {
    'WBC': 'WBC',
    'HGB': 'HGB',
    'PLT': 'PLT',
    'Sodium Level': 'Na',
    'Potassium Level': 'K',
    'Chloride Level': 'Cl',
    'CO2 Total': 'CO2',
    'Anion Gap': 'AG',
    'Glucose Level': 'Glucose',
    'Urea': 'Urea',
    'Creatinine (Plasma)': 'Creatinine',
    'Calcium Level': 'Ca',
    'Magnesium Level': 'Mg',
    'Albumin': 'Albumin',
    'Phosphate Level': 'PO4',
    'AST..': 'AST',
    'ALT.': 'ALT',
    'LD': 'LD',
    'GGT': 'GGT',
    'Alkaline Phosphatase': 'ALP',
    'Triglycerides Non-Fasting': 'Triglycerides',
}

def remove_deletable_lines(text):
    """
    Returns a new string with any line containing any of the items in deletable_strings removed.
    """
    # Split the text into lines
    lines = text.splitlines()
    
    # Filter out any line that contains one of the deletable strings
    filtered_lines = []
    for line in lines:
        if not any(deletable_item in line for deletable_item in deletable_strings):
            filtered_lines.append(line)
    
    # Return the filtered text preserving the original newline characters
    return "\n".join(filtered_lines)

def split_lab_string(lab_string):
    """
    Splits lab_string into segments at each occurrence of a date of format 
    dd-mmm-yyyy hh:mm. Returns a list of segments, where each segment begins with the date.
    """
    # Pattern will match e.g. "24-Nov-2024 15:26"
    pattern = r"(\d{1,2}-[A-Za-z]{3}-\d{4} \d{1,2}:\d{2})"
    parts = re.split(pattern, lab_string)
    
    segments = []
    # If there is any header text before the first date, add it (optional)
    if parts[0].strip():
        segments.append(parts[0].strip())
    
    # parts will have the structure:
    # [ pre_text, date1, text1, date2, text2, ... ]
    # We combine each date with its following text.
    for i in range(1, len(parts), 2):
        date_part = parts[i].strip()
        text_part = parts[i+1].strip() if i+1 < len(parts) else ""
        segments.append(f"{date_part} {text_part}")
    
    return segments

def extract_lab_values(segments):
    """
    Processes a list of segments and extracts lab values.
    For each segment it extracts the date (from the segment's first line using the format
    dd-mmm-yyyy hh:mm) and then iterates through each line. For any line starting with one of the keys
    in the lab_name dictionary (unless it starts with a string in skip_keys), the function extracts
    the first token after the key (assumed to be the lab value) and appends a tuple (lab_value, date)
    to the patient_labs entry corresponding to the shorthand value found in lab_name.
    """
    # A regex to capture the date from the very first token of the segment.
    date_pattern = re.compile(r'^(\d{1,2}-[A-Za-z]{3}-\d{4} \d{1,2}:\d{2})')
    
    # Iterate over each segment
    for segment in segments:
        lines = segment.splitlines()
        if not lines:
            continue

        # Extract date from the first line
        m = date_pattern.match(lines[0])
        if not m:
            continue
        segment_date = m.group(1)

        # Iterate through each line in the segment
        for line in lines:
            # Skip any line that starts with a string in skip_keys
            if any(line.startswith(skip_term) for skip_term in skip_keys):
                continue

            # Check each lab key in lab_name
            for lab_key, lab_short in lab_name.items():
                if line.startswith(lab_key):
                    remainder = line[len(lab_key):].strip()
                    tokens = remainder.split()
                    if tokens:
                        lab_value = tokens[0]
                        patient_labs.setdefault(lab_short, []).append((lab_value, segment_date))
    return patient_labs

def process_lab_text(text):
    """
    Processes the given text by removing deletable lines, 
    splitting it into segments, and then extracting lab values, culture information, and imaging reports.
    Returns a dictionary with lab values, cultures, and imaging reports.
    """
    filtered_text = remove_deletable_lines(text)
    segments = split_lab_string(filtered_text)
    
    # Initialize results
    labs = {}
    cultures = []
    imaging_to_analyze = []

    # Process each segment
    for segment in segments:
        # Check if the segment relates to a culture
        if "culture" in segment.splitlines()[0].lower():
            # Analyze the culture and add it to the cultures list
            culture_info = analyze_culture_string(segment)
            cultures.append(culture_info)
        elif "Interpreting Radiologist" in segment:
            # Analyze the imaging report and add it to the imaging reports list
            imaging_to_analyze.append(segment)
        else:
            # Otherwise, process it as lab values
            extract_lab_values([segment])  # Pass the segment as a single-item list

    imaging_reports = analyze_imaging_list(imaging_to_analyze)

    # Return labs, cultures, and imaging reports
    return {
        "labs": patient_labs,
        "cultures": cultures,
        "imaging": imaging_reports
    }

def analyze_culture_string(culture_string):
    """
    Analyzes a culture string and extracts the following information:
    - Date of the culture
    - Type of culture (e.g., blood, urine, etc.)
    - Gram stain results (if present)
    - Bacteria grown (if present, preceded by "#)")
    
    Returns a dictionary with the extracted information.
    """
    # Regex to capture the date in the format dd-mmm-yyyy hh:mm
    date_pattern = re.compile(r'^(\d{1,2}-[A-Za-z]{3}-\d{4} \d{1,2}:\d{2})')
    # Regex to capture gram stain results
    gram_stain_pattern = re.compile(r'GRAM STAIN.*?\n(.*?)\n', re.DOTALL)
    # Regex to capture bacteria names preceded by "#)"
    bacteria_pattern = re.compile(r'(?<!\()\d\)\s+(.*)')

    # Keywords to identify culture types
    culture_keywords = {
        "blood": ["Blood"],
        "urine": ["Urine", "Midstream Urine", "MSU"],
        "peritoneal fluid": ["Peritoneal", "Intraperitoneal"],
        "MRSA Screen": ["MRSA SURVEILLANCE CULTURE"],
        "fluid": ["Fluid"],
        "stool": ["Stool"],
        "sputum": ["Sputum"],
        "yeast": ["Yeast"],
        "csf": ["CSF", "Cerebrospinal Fluid"]
    }

    # Initialize the result dictionary
    results = {
        "date": None,
        "culture_type": None,
        "gram_stain": None,
        "bacteria": []
    }

    # Extract the date
    date_match = date_pattern.search(culture_string)
    if date_match:
        results["date"] = date_match.group(1)

    # Extract the culture type using keywords
    for culture_type, keywords in culture_keywords.items():
        for keyword in keywords:
            if keyword.lower() in culture_string.lower():
                results["culture_type"] = culture_type
                break
        if results["culture_type"]:
            break

    # Extract gram stain results
    gram_stain_match = gram_stain_pattern.search(culture_string)
    if gram_stain_match:
        results["gram_stain"] = gram_stain_match.group(1).strip()

    # Extract bacteria names
    bacteria_matches = bacteria_pattern.findall(culture_string)
    if bacteria_matches:
        results["bacteria"] = [bacteria.strip() for bacteria in bacteria_matches]

    return results

def analyze_imaging_list(imaging_list):
    """
    Splits the imaging string into individual reports based on the start of each report.
    Each report starts with a line in the format: dd-mmm-yyyy hh:mm followed by the type of test.
    Only processes portions of the text that contain "Interpreting Radiologist."
    
    Returns a dictionary organized by study type (e.g., "X-ray", "CT", etc.).
    """

    # Mapping for study types
    study_type_mapping = {
        "XR": "X-ray",
        "CT": "CT",
        "MR": "MRI",
        "US": "Ultrasound"
    }

    sub_type_mapping = {
        "Chest": "Chest",
        "Abdomen": "Abdomen",
        "Pelvis": "Pelvis",
        "Head": "Head",
        "Neck": "Neck",
        "Spine": "Spine",
        "Brain": "Brain",
        "Angio": "Angiography",
    }

    # Initialize the result dictionary, including the "Other" key
    organized_reports = {study: [] for study in study_type_mapping.values()}
    organized_reports["Other"] = []  # Add the "Other" key to handle unmatched study types

    for imaging_report in imaging_list:
        cleaned_part = imaging_report.split("Interpreting Radiologist")[0].strip()  # Keep only the part before "Interpreting Radiologist"
        date = cleaned_part[:12]

        # get subtype
        sub_types = []
        for sub_type in sub_type_mapping.keys():
            if sub_type in cleaned_part:
                sub_types.append(sub_type_mapping[sub_type])

        # Extract the first line of the cleaned part
        first_line = cleaned_part.splitlines()[0]
        for key, value in study_type_mapping.items():
            if key in first_line:
                study_type = value
                break
            else:
                study_type = "Other"

        # Extract findings (everything except the first line)
        findings = "\n".join(cleaned_part.splitlines()[1:]).strip()

        findings_spaced = findings.replace("IMPRESSION", "\n\nIMPRESSION")

        # Create the dictionary for this study
        study_dict = {
            "date": date,
            "sub_types": sub_types,
            "findings": findings_spaced,
            "thoughts": ""
        }

        # Add the study dictionary to the appropriate list in the result dictionary
        organized_reports[study_type].append(study_dict)

    return organized_reports

if __name__ == '__main__':
    results = process_lab_text(lab_string)
    
