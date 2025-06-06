import os, pyperclip, json
from models.patient_class import Patient
from utils.pt_grab import PtListGrab
import datetime as dt
import pyautogui as pag
from flask import request, session  # Assuming Flask is being used

current_patient = None  # Add this line to define the global variable

def get_pt_list():
    """Retrieve pt_list from the session or initialize it as an empty list."""
    if 'pt_list' in session:
        pt_list_dicts = json.loads(session['pt_list'])  # Deserialize pt_list from JSON
        new_list = []
        for p_dict in pt_list_dicts:
            # Convert dictionaries back to Patient objects
            patient = Patient(**p_dict)            
            new_list.append(patient)
        return new_list
    return []

def save_pt_list(pt_list):
    """Save pt_list to the session."""
    serialized = []
    for pt in pt_list:
        p_dict = pt.__dict__.copy()
        
        
        serialized.append(p_dict)
    session['pt_list'] = json.dumps(serialized)  # Serialize pt_list to JSON


def add_patient(pt_list):
    """
    Adds a new patient to the patient list using form data.
    """
    first_initial = request.form.get("first_initial")
    second_initial = request.form.get("second_initial")
    age = calculate_age(request.form.get("dob"))
    gender = request.form.get("gender").upper()
    admit_date = request.form.get("admit_date")

    # Create a new patient instance
    new_patient = Patient(first_initial, second_initial, age, gender, admit_date)

    # Add the new patient to the list
    pt_list.append(new_patient)

    # Return the updated patient list
    return pt_list

def calculate_age(birthdate):
    """
    Calculate the age of a patient based on their birthdate.

    Args:
        birthdate (str): The birthdate of the patient in the format 'YYYY-MM-DD'.

    Returns:
        int: The age of the patient in years.
    """
    today = dt.datetime.today()
    birthdate = dt.datetime.strptime(birthdate, '%Y-%m-%d')
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def save_data(pt_list):
    filepath = '/Users/matthewmittelstadt/Desktop/code/gbf/tps'
    filename = "Y2"
    file_type = filename + ".json"
    filepath = os.path.join(filepath, file_type)
    with open(filepath, "w") as f:
        json.dump(pt_list, f, default=lambda obj: obj.__dict__, indent=4)

def load_data(filename):
    filepath = '/Users/matthewmittelstadt/Desktop/code/gbf/tps/'
    filename = "Y2"
    file_type = filename + ".json"
    filepath = os.path.join(filepath, file_type)
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def pnons(gender, type):
    """
    Returns the appropriate pronoun based on the given gender and type.

    Parameters:
    gender (str): The gender of the person. Accepted values are:
                  "M" for male,
                  "F" for female,
                  "X" for non-binary.
    type (str): The type of pronoun. Accepted values are:
                "s" for subject pronoun (he, she, they),
                "p" for possessive pronoun (his, hers, theirs),
                "o" for object pronoun (him, her, their).

    Returns:
    str: The appropriate pronoun based on the given gender and type.

    Examples:
    >>> pnons("M", "s")
    'he'
    >>> pnons("F", "p")
    'hers'
    >>> pnons("X", "o")
    'their'
    """
    if gender == "M":
        if type == "s":
            return "he"
        elif type == "p":
            return "his"
        elif type == "o":
            return "him"
    elif gender == "F":
        if type == "s":
            return "she"
        elif type == "p":
            return "hers"
        elif type == "o":
            return "her"
    if gender == "X":
        if type == "s":
            return "they"
        elif type == "p":
            return "theirs"
        elif type == "o":
            return "their"

def normalize_med_name(med_name):
    if "_" in med_name:
        med_name = med_name.rsplit("_", 1)[0]
        return med_name.split()[0]  # Use the first word of the medication name
    return med_name

def home_med_grabber():
    med_tab_label = (245, 368)
    print_meds_button = (101, 311)
    adobe_button = (966, 267)
    more_tools = (936, 248)
    last_box = (340, 419)
    units_box = (450, 419)
    fit_width_scrolling = (945, 275)
    show_button = (900, 393)

    pag.moveTo(med_tab_label)
    pag.click(clicks = 2)
    pag.PAUSE = 1
    pag.moveTo(last_box)
    pag.click()
    pag.typewrite('6')
    pag.PAUSE = 0.5
    pag.moveTo(units_box)
    pag.click()
    pag.typewrite('m')
    pag.moveTo(show_button)
    pag.click()
    pag.PAUSE = 1
    pag.moveTo(print_meds_button)
    pag.click()
    pag.PAUSE = 3
    pag.moveTo(adobe_button)
    pag.click()
    pag.PAUSE = 0.5
    pag.moveTo(more_tools)
    pag.click()
    pag.PAUSE = 0.5
    pag.moveTo(fit_width_scrolling)
    pag.click()
    pag.PAUSE = 0.5
    pag.click()
    pag.hotkey('command', 'a')
    pag.hotkey('command', 'c')

def check_for_med_class(med_dictionary, list_of_classes):
    """
    Checks if any medication in the provided dictionary belongs to the specified classes.
    Args:
        med_dictionary (dict): A dictionary where keys are medication names and values are dictionaries with details about the medication.
        list_of_classes (list): A list of medication classes to check against.
    Returns:
        list: A list of medication names that belong to the specified classes.
    """
    list_of_hits = []
    for med_name, details in med_dictionary.items():
        if any(drug in details["type"] for drug in list_of_classes):
            list_of_hits.append(med_name)
    return list_of_hits

def check_latest_vitals(vitals_dictionary, vital_name):
    latest_vital_entry = vitals_dictionary[-1]
    for date, vitals in latest_vital_entry.items():
        if vital_name in vitals:
            latest_vital_value = vitals[vital_name]
            latest_vital_date = date
            return latest_vital_value, latest_vital_date

def get_latest_lab_value(lab_dictionary, lab_name):
    """
    Retrieve the most recent value and date for a specified lab test from a lab dictionary.

    Args:
        lab_dictionary (dict): A dictionary where keys are lab test names and values are lists of tuples,
            each containing a lab value and its corresponding date (e.g., [(value1, date1), (value2, date2), ...]).
        lab_name (str): The name of the lab test to retrieve the latest value for.

    Returns:
        tuple: A tuple containing the latest lab value and its corresponding date.
            Returns (None, None) if the lab_name is not found in the lab_dictionary.
    """
    if lab_name not in lab_dictionary:
        return None, None
    # Get the latest lab value and date for the specified lab name
    latest_lab_value = lab_dictionary[lab_name][-1][0]
    latest_lab_date = lab_dictionary[lab_name][-1][1]

    return latest_lab_value, latest_lab_date

def get_imaging_result(patient, study_type, sub_types=None, keyword=None):
    """
    Retrieves imaging studies for a patient that match specified subtypes and contain a given keyword in their thoughts.

    Args:
        patient: An object representing the patient, expected to have an 'imaging' attribute structured as a dictionary.
        study_type (str or list): The type(s) of imaging study to search for (e.g., 'MRI', 'CT', or ['MRI', 'CT']).
        sub_types (list, optional): A list of subtypes to filter the studies. Only studies containing any of these subtypes will be considered.
        keyword (str, optional): A keyword to search for within the 'thoughts' field of each study.

    Returns:
        list: A list of imaging studies (dicts) that match the specified subtypes and contain the keyword in their 'thoughts'.
    """
    list_of_hits = []
    # Allow study_type to be a string or a list
    if isinstance(study_type, str):
        study_types = [study_type]
    else:
        study_types = study_type

    for stype in study_types:
        for study in patient.imaging.get(stype, []):
            if any(x in study.get("sub_types", []) for x in sub_types):
                if keyword.lower() in study.get("thoughts", "").lower():
                    list_of_hits.append((stype, study))
    return list_of_hits