import json
from utils.gb_ai import build_text_list
#testing
from models.patient_class import Patient

# Load medication types from the JSON file
with open('/Users/matthewmittelstadt/Desktop/code/gb/medication_types.json', 'r') as file:
    medication_types = json.load(file)

class Issue:
    def __init__(self, patient):
        self.patient = patient

        self.category_meds = []

        self.relevant_vitals = []
        self.instance_home_meds = []
        self.instance_hosp_meds = []
        self.instance_labs = []
        self.instance_imaging = []

        self.detail_map = {}

    def analyze_details(self):
        for key, value in self.detail_map.items():
            print(f"{key}: {value}")
        
    def pull_relevancy(self):
        for item in self.category_meds:
            relevant_home_meds = self.is_on_med_class(item)
            relevant_hosp_meds = self.is_on_med_here(item)
            for med_match in relevant_home_meds:
                self.instance_home_meds.append(med_match)
            for med_match in relevant_hosp_meds:
                self.instance_hosp_meds.append(med_match)
            
    def is_on_med_here(self, class_tag):
        med_list = []
        class_meds = [med_class for med_class in medication_types.keys() if class_tag in med_class]
        for med_dict in [self.patient.hosp_meds]:
            for med_name, _ in med_dict.items():
                if med_name.lower() in class_meds:
                    med_list.append(med_name)
        return med_list
    
    def is_on_med_class(self, class_tag):
        med_list = []
        class_matches = [med_class for med_class in medication_types.keys() if class_tag in med_class]
        for specific_medication in [self.patient.home_meds]:
            for med_name, _ in specific_medication.items():
                for specific_class in class_matches:
                    if med_name.lower() in medication_types[specific_class]:
                        med_list.append((med_name, specific_class))
        return med_list
    
class Asthma(Issue):
    def __init__(self, patient):
        super().__init__(patient)
        self.category_meds = ["Puffer"]

        self.o2_record = []
        for vitals_record in self.patient.vitals.vitals:
            self.o2_record.append(vitals_record[5][1])

        self.max_o2 = max(self.o2_record)
        self.min_o2 = min(self.o2_record)

        self.detail_map = {
            "SABA": False,
            "ICS": False
        }
        
        self.pull_relevancy()

    def print_details(self):
        text = "Asthma Exacerbation:\n"
        if self.instance_home_meds:
            text += f"   At home, the patient is on:\n"
            for match in self.instance_home_meds:
                type_of_med = match[1].replace("Puffers - ", "")
                text += f"      {type_of_med}: {match[0]}\n"
        if self.o2_record:
            text += f"{self.max_o2}{self.min_o2}"
        return text

        


class IssueCategory:
    def __init__(self, patient):
        self.patient = patient
        self.details_map = {}
        self.detail_types = {}
        self.print_map = {}
        self.condition_map = {}

    def input_details(self):
        print(f"Class Selected: {self.__class__.__name__}")
        
        print("Available issues:\n")
        for code, issue in self.condition_map.items():
            print(f"{code} - {issue}", end=" | ")
        issue_code = input("\n\nEnter the issue code: ")
        item = self.condition_map.get(issue_code)
        if not item:
            print(f"Invalid issue code: {issue_code}")
            return
        
        if item in self.details_map:
            details = self.input_issue_details(item)
        else:
            details = input("Enter details for the issue: ")

        self.patient.issues.setdefault(self.__class__.__name__, {})  # Ensure dictionary is present
        self.patient.issues[self.__class__.__name__][item] = details
        print(f"Added {item} to {self.__class__.__name__} with details: {details}")

    def input_issue_details(self, issue):
        print(f"\nEnter details for {issue} in shorthand:")
        self.print_issue_options(issue)
        shorthand = input("Details: ")
        if shorthand == "--":
            details = {""}
        else:
            details = self.parse_shorthand(issue, shorthand)
        print(f"Entered details: {details}")
        input("Press Enter to continue...")
        return details

    def print_issue_options(self, issue):
        for key, options in self.details_map[issue].items():
            options_str = " | ".join([f"{k} - {v}" for k, v in options.items()])
            print(f"     {key}: {options_str}")

    def parse_shorthand(self, issue, shorthand):  
        details = {}
        for part in shorthand.split(';'):
            key = part[0]
            values = part[1:].split(',')
            if key in self.details_map[issue]:
                details[key] = []
                for value in values:
                    if value in self.details_map[issue][key]:
                        details[key].append(self.details_map[issue][key][value])
                    else:
                        details[key].append(value)
                if len(details[key]) == 1:
                    details[key] = details[key][0]
            else:
                print(f"Invalid shorthand: {part}")
                input("Press Enter to continue...")
                return "Invalid details"
        return details
    
    def print_details(self, category, issue):
        if issue in self.print_map:
            return self.print_map[issue]()
        else:
            details = self.patient.issues[category][issue]
            result = f"{issue}\n"
            if isinstance(details, dict):
                for key, value in details.items():
                    detail_type = self.detail_types[issue].get(key, "Unknown")
                    if isinstance(value, list):
                        value = ", ".join(value)
                    result += f"     {detail_type}: {value}\n"
            return result.strip()

    def is_on_med_class(self, class_tag):
        class_meds = medication_types.get(class_tag, [])
        for med_dict in [self.patient.hosp_meds]:
            for med_name, med_details in med_dict.items():
                if med_name.lower() in class_meds and med_details.get("A/S/D") == "Active":
                    return True
        return False

    def pull_med_name(self, class_tag):
        class_meds = medication_types.get(class_tag, [])
        for med_dict in [self.patient.hosp_meds]:
            for med_name, med_details in med_dict.items():
                if med_name.lower() in class_meds and med_details.get("A/S/D") == "Active":
                    return med_name
        return None

    def is_on_max_dose_acetaminophen(self):
        """
        Checks if the patient is currently on a max dose of acetaminophen (975mg QID/q6h and NOT PRN).
        
        Returns:
            bool: True if the patient is on a max dose of acetaminophen, False otherwise.
        """
        for med_dict in [self.patient.hosp_meds, self.patient.home_meds]:
            for med_name, med_details in med_dict.items():
                if med_name.lower() == "acetaminophen" and med_details.get("A/S/D") == "Active":
                    if med_details.get("dose") == "975" and med_details.get("units") == "mg" and not med_details.get("PRN"):
                        if med_details.get("frequency") in ["QID", "q6h"]:
                            return True
        return False

class Pain(IssueCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.condition_map = {
            "g": "General Pain",
            "c": "Chest Pain",
        }

        self.details_map = {
            "General Pain": {
                "s": {"a": "Acute", "c": "Chronic"},
                "y": {"s": "Somatic (local/ache/throb/cramp)", "v": "Visceral (deep/pressure/colicky)", "n": "Neuropathic (burning/shooting/shock-like)"},
                "l": {"c": "chest", "g": "generalized", "b": "back", "a": "abdomen"},
                "c": {"y": "controlled pain", "n": "not controlled"}
            },
            "Chest Pain": {
                "f": {"y": "yes", "n": "no"},
                "l": {"r": "retrosternal", "l": "lateral", "b": "back", "s": "shoulder", "e": "epigastric", "v": "variable"},
                "m": {"y": "yes", "n": "no"},
                "n": {"y": "yes", "n": "no"},
                "o": {"s": "sudden", "g": "gradual", "c": "constant", "i": "intermittent"},
                "q": {"s": "sharp", "h": "heaviness/pressure", "b": "burning", "k": "knifelike", "a": "aching", "c": "crushing"},
                "r": {"y": "yes", "n": "no"},
                "s": {"y": "yes", "n": "no"}
            }
        }
        self.detail_types = {
            "General Pain": {
                "s": "Status",
                "y": "Type",
                "l": "Location",
                "c": "Control",
            },
            "Chest Pain": {
                "f": "Forward Lean Improvement",
                "l": "Location",
                "m": "Meal-Related",
                "n": "Nitro Response",
                "o": "Onset",
                "q": "Quality",
                "r": "Rest-Improved",
                "s": "Syncope Association"
            }
        }

        self.print_map = {
            "General Pain": self.print_general_pain,
            "Chest Pain": self.print_chest_pain
        }

    def print_analgesics(self):
        text = ""
        opioid_meds = []
        non_opioid_meds = []

        # Get all analgesic medications
        analgesic_meds = []
        for med_class, meds in medication_types.items():
            if "Analgesic" in med_class:
                analgesic_meds.extend(meds)

        # Separate opioid and non-opioid medications
        for med_dict in [self.patient.hosp_meds, self.patient.home_meds]:
            for med_name, med_details in med_dict.items():
                if med_name.lower() in analgesic_meds and med_details.get("A/S/D") == "Active":
                    med_info = f"{med_name.title()} {med_details['dose']} {med_details['units']} {med_details['frequency']}"
                    if med_details.get("PRN"):
                        med_info += " (PRN)"
                    if "Opioid" in med_details.get("type", ""):
                        opioid_meds.append(med_info)
                    else:
                        non_opioid_meds.append(med_info)

        if non_opioid_meds:
            text += "\n     Non-opioid Pain Medications:\n" + "\n".join([f"          - {med}" for med in non_opioid_meds])
        if opioid_meds:
            text += "\n     Opioid Pain Medications:\n" + "\n".join([f"          - {med}" for med in opioid_meds])
        
        return text
    
    def print_general_pain(self):
        """
        MEDICAL SOURCES: UpToDate, WHO Pain Ladder, Harrison's Principles of Internal Medicine
        
        Generates a detailed text summary of the patient's general pain management plan.
        This method evaluates the patient's pain issues, checks for contraindications to NSAIDs,
        and constructs a text summary based on the WHO analgesic ladder. It also includes the 
        patient's description of pain and current analgesic medications if available.
        Returns:
            str: A formatted string containing the general pain management plan.
        """

        general_pain_details = self.patient.issues["Pain"]["General Pain"]
        opioids_status = self.is_on_med_class("Analgesic, Opioids")
        pain_controlled = False

        nsaid_contradiction = [contraindications for contraindications in ["GI Bleed", "CKD", "Liver Disease"] if contraindications in self.patient.pmhx]
        if nsaid_contradiction:
            nsaid_comment = f"NSAIDs are contraindicated in patients with {', '.join(nsaid_contradiction)} so we will avoid them in this circumstance."
        else:
            nsaid_comment = "Patient has no contraindications to NSAIDs so we will use them for pain control as needed."

        text = f"Pain ({general_pain_details['l']})\n"
        text += "Treatment of pain follows the WHO analgesic ladder, which is as follows:\n"
        text += f"\n    STEP 1 - Non-opioid analgesics\n    This mostly refers to acetaminophen and NSAIDs. I believe that regular dosing of same will give better pain relief than sporadic dosing. {nsaid_comment} Note that these medications have a ceiling, and when reaching said dosing ceiling we then need to increase up to the latter ladder steps."
        text += "\n\n    STEP 2 & 3 - 'Weak' vs. 'Strong' opioid analgesics\n    Although practice used to focus more on starting with a 'weaker' opioid like codeine/morphine, in the absence of other contraindication practice now starts with lower doses of 'stronger' opioids like hydromorphone with escalation as needed.\n"

        if "s" in general_pain_details:
            text += f"    Status: {general_pain_details['s']}"
        if "y" in general_pain_details:
            if general_pain_details["y"].startswith("S"):
                text += f"\n    Patient's description of pain is most consistent with somatic pain."
            elif general_pain_details["y"].startswith("V"):
                text += f"\n    Patient's description of pain is most consistent with visceral pain."
            elif general_pain_details["y"].startswith("N"):
                text += f"\n    Patient's description of pain is most consistent with neuropathic pain."

        if self.print_analgesics():
            text += f'\n\n  Current medications are as follows: {self.print_analgesics()}'
        else:
            text += f'\n  Currently not on any pain medications. '

        if general_pain_details['c'].startswith('c'):
            pain_controlled = True

        if not opioids_status:
            text += '\n\n     As patient is not currently on opioids, I would consider them at Step 1. '
        else:
            text += '\n\n     Given the presence of opioids, they are in the STEP 2-3 range. '

        if pain_controlled:
            text += "\n\nGiven that patient reports no ongoing pain, we will leave them on this current regimen and monitor closely."

        else:
            text += "\n\n     As patient is still experiencing pain, I would recommend the following:"
            if not self.is_on_max_dose_acetaminophen() and opioids_status:
                text += "\n      - Ensure they are on a max dose of Acetaminophen (1g q6h scheduled).\n      - If patient is still having pain following this, an increase in opioid frequency would be appropriate."
            elif not self.is_on_max_dose_acetaminophen() and not opioids_status:
                text += "\n      - Ensure they are on a max dose of Acetaminophen (1g q6h scheduled). Should that not provide relief, I think it would be warranted to start them on opioids and increase to step 2/3."
            elif self.is_on_max_dose_acetaminophen and not opioids_status:
                text += "\n      - As they are already on maximum appropriate Acetaminophen, I think we need to start opioids at this time."
            elif self.is_on_max_dose_acetaminophen and opioids_status:
                text += "\n      - They are already on opioids, and we will look to increase the frequency to prevent any peaks/troughs in dosing. "

        return text

    def diamond_forrester(self):
        chest_pain_score = 0
        try:
            if self.patient.issues["Pain"]["Chest Pain"]["l"] == "retrosternal":
                chest_pain_score += 1
            if self.patient.issues["Pain"]["Chest Pain"]["n"].startswith('y'):
                chest_pain_score += 1
            if self.patient.issues["Pain"]["Chest Pain"]["r"].startswith('y'):
                chest_pain_score += 1
        except KeyError:
            return "No Diamond-Forrester score can be calculated due to missing information."

        if chest_pain_score <= 1:
            if self.patient.gender == "F" and int(self.patient.age) < 60:
                return "In considering the common features of anginal chest pain, this patient's chest pain is not consistent with angina. When factoring in the patient's demographics, this patient is at low risk for CAD detection on angiography."
            if self.patient.gender == "M" and int(self.patient.age) < 40:
                return "In considering the common features of anginal chest pain, this patient's chest pain is not consistent with angina. When factoring in the patient's demographics, this patient is at low risk for CAD detection on angiography."
            return "In considering the common features of anginal chest pain, this patient's chest pain is not consistent with angina, but due to patient demographics they still are at intermediate risk. A decision on angiography will be made in consideration of entire patient case."
        elif chest_pain_score == 2:
            return "This patient's chest pain would be considered atypical angina. They are at an intermediate risk for CAD detection on angiography."
        else:
            return "This patient's chest pain is consistent with angina according to the Diamond-Forrester literature on risk statification (endorsed by CCS)."

    def print_chest_pain(self):
    
    #heading and pre-amble
        text = f"Chest Pain \n"
        text += "    The goal of undifferentiated chest pain presentations is to rule out life-threatening causes such as ACS, dissection, PE or pneumothorax. Should these be ruled out, we of course want to identify and treat whatever the etiology is.\n"
        labs_text = ""
        caution_text = ""

    #Initialize working dictionary
        chest_pain_details = self.patient.issues["Pain"]["Chest Pain"]

    #HISTORY
        history_text = f"    Patient describes chest pain as {chest_pain_details.get('q', 'UNKNOWN')} " \
                       f"in nature, located primarily {chest_pain_details.get('l', 'UNKNOWN')}. "

        key_map = {
            "f": ("Leaning forward improves their chest pain. ", "Leaning forward does not improve their chest pain. "),
            "m": ("\n    Their chest pain is meal-related. This could be a sign of a gastrointestinal etiology, although redistribution to splanchnic vasculature in severe CAD can cause postprandial angina and we cannot use this alone to rule out MI. ", "Their chest pain is not meal-related. "),
            "n": ("Nitroglycerin improves their chest pain. ", "Nitroglycerin does not improve their chest pain. "),
            "r": ("Rest improves their chest pain. ", "Rest does not improve their chest pain. "),
            "s": ("Their chest pain is associated with syncope. ", "Their chest pain is not associated with syncope. "),
        }

        for key, (yes_text, no_text) in key_map.items():
            value = chest_pain_details.get(key)
            if value is None:
                caution_text += f"\n  - No '{self.detail_types["Chest Pain"][key]}' information provided. "
            else:
                if value.startswith('y'):
                    history_text += yes_text
                else:
                    history_text += no_text

        text += history_text
        
    #ADD DIAMOND FORRESTER Comment
        text += f"\n    {self.diamond_forrester()}"

    #LABS
        troponin_labs = self.patient.labs.lab_value_checker("Troponin")
        if not troponin_labs:
            labs_text += "\n\n     No troponin has been drawn and we will need to do one immediately. Chest pain presentation suspicion for ACS requires a troponin done at presentation with a repeat 3-6 hours thereafter if ACS is considered. "
        else:
            labs_text += "\n\n     Troponin values drawn so far are as follows:. "
            for value, date in troponin_labs.lab_results:
                labs_text += f"\n          - {value} on {date} "
            labs_text += troponin_labs.print_lab_assessment()

        


        text += labs_text 
        if caution_text:
            text += f"\n\n     Caution: \n{caution_text}"

        return text

class Constipation(IssueCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.condition_map = {
            "c": "Constipation",
        }

        self.details_map = {
            "Constipation": {
                "b": {"#": "Number of days since last bowel movement"}
            },
        }
        self.detail_types = {
            "Constipation": {
                "b": "Last bowel Movement"
            },
        }

        self.print_map = {
            "Constipation": self.print_constipation
        }

    def print_constipation(self):
        """
        MEDICAL SOURCES: Harrison's Principles of Internal Medicine
        
        Generates a detailed text summary of the patient's constipation management plan.
        This method evaluates the patient's constipation issues, checks for opioid-induced
        constipation, and constructs a text summary based on the patient's current bowel habits.
        Returns:
            str: A formatted string containing the constipation management plan.
        """

        #standard statements
        on_opioids = self.is_on_med_class("Analgesic, Opioids")
        on_stimulants = self.is_on_med_class("Laxative, Stimulant")
        on_osmotics = self.is_on_med_class("Laxative, Osmotic")
        on_softeners = self.is_on_med_class("Laxative, Softener")

        current_treatment = []
        things_to_add = []
        for items in [on_stimulants, on_osmotics, on_softeners]:
            if items:
                current_treatment.append(self.pull_med_name(items))
        
        for med_class in ["Laxative, Stimulant", "Laxative, Osmotic", "Laxative, Softener"]:
            if not self.is_on_med_class(med_class):
                things_to_add.append(med_class.split(", ")[1])

        
        constipation_drug_statement = "Treatment of constipation includes stimulant and osmotic laxatives, fluids and enemas if needed."
        fiber_statement = "Regular intake of dietary fiber is recommended to promote regular bowel movements."
        current_treatment_statement = f"Current treatment includes {', '.join(current_treatment)}."
        if current_treatment == []:
            current_treatment_statement = "Patient is currently not recieving treatment for constipation."
        things_to_add_statement = f"For next steps we can consider adding {', '.join(things_to_add)} laxatives to their regimen."

        if on_opioids:
            fiber_statement = "Since opioids are being given, fibers are not recommended."
        
        constipation_details = self.patient.issues["Constipation"]["Constipation"]
        bowel_movement = constipation_details.get("b", "Unknown")

        text = f"Constipation\n"
        text += f"         Reported last bowel movement was {bowel_movement} days ago."
        text += f" {constipation_drug_statement}"
        text += f" {fiber_statement} {current_treatment_statement} {things_to_add_statement}"
        text += " Should the patient's constipation persist, we can consider enemas. If suspicion of dysmotlity comes up, metoclopramide would be a good option."


        return text

class Infection(IssueCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.details_map = {
            "UTI": {
                "s": {"a": "Acute", "r": "Recurrent"},
                "t": {"a": "Antibiotics", "p": "Probiotics"}
            }
        }
        self.detail_types = {
            "UTI": {
                "s": "Status",
                "t": "Treatment"
            }
        }

class Injury(IssueCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.details_map = {
            "Fracture": {
                "l": {"a": "Arm", "l": "Leg"},
                "t": {"c": "Cast", "s": "Surgery"}
            }
        }
        self.detail_types = {
            "Fracture": {
                "l": "Location",
                "t": "Treatment"
            }
        }


if __name__ == "__main__":
    patient = Patient("M", "M", 30, "M", "03-Dec-2024")
    patient.labs["Troponin"] = [(0.01, "05-Dec-2024")]
    issue_handler = IssueCategory(patient)
    print(issue_handler.has_lab_value("Troponin"))
