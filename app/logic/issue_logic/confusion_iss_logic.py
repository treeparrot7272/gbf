from utils.gb_ai import pnons, check_for_med_class, get_latest_lab_value, check_latest_vitals, get_imaging_result
import datetime

def confusion_assessor(patient):
    if "initial" not in patient.issues["confusion"]:
        # If the confusion issue has not been initialized, do so
        write_up = confusion_initial(patient)
    elif "resolved" in patient.issues["confusion"]:
        pass
    else:
        write_up = new_day_updater(patient)
    return write_up


#types of write-ups
def confusion_initial(patient):
    """
    Initializes the confusion issue for a patient.
    
    Args:
        patient (Patient): The patient object to initialize the confusion issue for.
    
    Returns:
        None
    """

###SET UP DICTIONARY ENTRY####
    #set up initial dictionary entry of confusion issue
    patient.issues["confusion"]["initial"] = {}
    new_data = patient.issues["confusion"]["initial"]
    new_data["date"] = patient.history["confusion"]["confusion_onset_date"]

    #initial CAM score
    new_data["cam_score"] = cam_score(confusion_history=patient.history["confusion"])
    # Check for medications that can cause confusion
    new_data["initial_meds"] = dims_drugs(patient.hosp_meds)


#####WRITE-UP PART####
    confusion_write_up = ""
    #get first date of confusion
    onset_date = patient.history["confusion"]["confusion_onset_date"][5:]
    
    # Check if the patient meets CAM criteria for delirium
    
    if new_data["cam_score"]:
        cam_comment = f"{pnons(patient.gender,"s").capitalize()} initially met CAM criteria for delirium. "
        cam_comment += "CAM score has a sensitivity of 94% and specificity of 89% for delirium. This should be checked throughout the patient's stay. "
    else:
        cam_comment = f"{pnons(patient.gender, 's').capitalize()} did not meet CAM criteria initially. "

    if new_data["initial_meds"]:
        meds_comment = "\nA medication review showed that the patient is currently taking  "
        meds_comment += ", ".join(new_data["initial_meds"]) + " and this could be a contributor. "
    else:
        meds_comment = "Patient is not currently taking any medications that are known to cause confusion. "

    # Check for infections
    infections = dims_infections(patient)

    # Metabolic derangements
    high_met, low_met, normal_met, missing_met = dims_metabolic(patient)

    # Check for structural lesions
    structural_lesions = dims_structural(patient)

# WRITE-UP
    confusion_write_up += f"Confusion was first noted on {onset_date}. {cam_comment}"

    confusion_write_up += f"\n\nWhen working up an etiology of confusion, it is important to consider the following categories: medications, metabolic derangements, structural lesions, and infections. "

# MEDS
    confusion_write_up +=f"\n\n1. MEDICATIONS:\n\nDrugs that are typically concerning for causing confusion include Anticholinergics, Benzodiazepines, Opioids, Antipsychotics, Antidepressants, Antihistamines, Muscle relaxants and substances (including alcohol). {meds_comment}"

# INFECTIONS
    confusion_write_up += f"\n\n2. INFECTIONS:\n\n{infections}"

# METABOLIC DERANGEMENTS
    confusion_write_up += "\n\n3. METABOLIC DERANGEMENTS:\n\nOf the metabolic markers we look at for confusion, we found:\n\n"

    if high_met:
        confusion_write_up += f"- Elevated values --> {', '.join(high_met)} \n"
    if low_met:
        confusion_write_up += f"- Low values --> {', '.join(low_met)}\n"
    if normal_met:
        confusion_write_up += f"- Normal findings --> {', '.join(normal_met)}\n\n"
    if missing_met:
        confusion_write_up += f"Studies not yet done include {', '.join(missing_met)}. I will order {"this" if len(missing_met) == 1  else "these"} for completion of work-up."

# STRUCTURAL LESIONS
    confusion_write_up += "\n\n4. STRUCTURAL LESIONS:\n\n"

    if structural_lesions:
        confusion_write_up += "Imaging studies concerning for structural lesions include:\n"
        for study in structural_lesions:
            confusion_write_up += f"- {study[0]} done on {study[1]['date']}\n"
    else:
        confusion_write_up += "No imaging studies concerning for structural lesions were found."

    return confusion_write_up

def new_day_updater(patient):
    last_entry, last_data = get_most_recent_entry(patient)
    return f"Confusion issue for patient last showed{last_data}.  Last entry was on {last_entry}."

#general functions
def cam_score(confusion_history):
    """
    Evaluates the CAM (Confusion Assessment Method) score based on a patient's confusion history.
    Parameters:
        confusion_history (dict): A dictionary containing boolean values for the following keys:
            - "inattention": Indicates presence of inattention.
            - "disorganized_thoughts": Indicates presence of disorganized thoughts.
            - "altered_level_of_consciousness": Indicates altered level of consciousness.
            - "confusion_fluctuating": Indicates fluctuating course of confusion.
            - "confusion_acute_onset": Indicates acute onset of confusion.
    Returns:
        bool: True if the CAM criteria for delirium are met, False otherwise.
    """
    
    cam_positive = True

    if not (confusion_history["inattention"]):
        cam_positive = False

    if not (confusion_history["disorganized_thoughts"] or confusion_history["altered_level_of_consciousness"]):
        cam_positive = False

    if not (confusion_history["confusion_fluctuating"] or confusion_history["confusion_acute_onset"]):
        cam_positive = False
    
    return cam_positive
    
def dims_drugs(patient_meds):
    """
    Returns any potential medications that can cause confusion in a patient if they are currently taking them. If no medications are found, returns an empty list.
    Args:
        meds (dict): A dictionary of medications currently taken by the patient, where keys are medication names and values are dictionaries with details about the medication.
    Returns:
        list: A list of medication names that can cause confusion, or an empty list if none are found.
    """

    confusion_drug_list = [
        "Anticholinergics",
        "Benzodiazepines",
        "Opioids",
        "Antipsychotics",
        "Antidepressants",
        "Antihistamines",
        "Muscle relaxants",
        "Alcohol"
    ]
    concerning_patient_drugs = check_for_med_class(patient_meds, confusion_drug_list)
    
    return concerning_patient_drugs
    
def dims_infections(patient):
    infections_info = ""
    recent_temp = float(check_latest_vitals(patient.vitals, "temp")[0])
    wbc = float(get_latest_lab_value(patient.labs, "WBC")[0])


    if recent_temp > 37.9:
        infections_info += f"Temperature is elevated at {recent_temp}°C, which may indicate an infection. "
    if wbc > 11:
        infections_info += f"White blood cell count is elevated at {wbc} cells/uL, which may indicate an infection. "

    return infections_info
    
def dims_metabolic(patient):
    metabolic_cut_offs = {
        "Na": (135, 145),
        "Ca": (2.0, 2.5),
        "Glucose": (3.9, 25),
        "Urea": (0, 7.5),
        "B12": (180, 900),
        "TSH": (0.4, 4.0),
    }

    metabolic_findings = {
        "Na": None,
        "Ca": None,
        "Glucose": None,
        "Urea": None,
        "B12": None,
        "TSH": None
    }

    elevated_values = []
    low_values = []
    normal_values = []
    missing_values = []

    for lab, (low, high) in metabolic_cut_offs.items():
        value = get_latest_lab_value(patient.labs, lab)[0]
        if value is not None:
            if float(value) < low:
                discrepancy = 'l'
            elif float(value) > high:
                discrepancy = 'h'
            else:
                discrepancy = 'n'
            metabolic_findings[lab] = [value, discrepancy]
        else:
            metabolic_findings[lab] = [None, None]
            missing_values.append(lab)

    for lab, (value, discrepancy) in metabolic_findings.items():
        if value is not None:
            if discrepancy == 'l':
                low_values.append(f"{lab} ({value})")
            elif discrepancy == 'h':
                elevated_values.append(f"{lab} ({value})")
            else:
                normal_values.append(f"{lab} ({value})")

    print(elevated_values, low_values, normal_values, missing_values)

    return elevated_values, low_values, normal_values, missing_values

def dims_structural(patient):
    
    concerning_studies = get_imaging_result(patient, ["CT", "MRI"], sub_types=["Brain", "Head", "Intracranial"], keyword="Stroke")

    return concerning_studies

def get_most_recent_entry(patient):
    
    if len(patient.issues["confusion"].keys()) == 1:
        relevant_entry, relevant_data = "initial", patient.issues["confusion"]["initial"]
        return relevant_entry, relevant_data
    
    elif len(patient.issues["confusion"].keys()) > 1:
        # Get the most recent entry based on the date
        
        entries = [entry for entry in patient.issues["confusion"] if entry != "initial"]
        
        most_recent_date = max(entries, key=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"))
        
        relevant_data = patient.issues["confusion"][most_recent_date]

        return most_recent_date, relevant_data
    else:
        return None, None


