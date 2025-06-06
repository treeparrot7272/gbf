import json
from models.pyx_class import VitalSignAssessor
import datetime as dt
from utils.gb_ai import build_text_list, pnons

# Load medication types from the JSON file
with open('/Users/matthewmittelstadt/Desktop/code/gb/medication_types.json', 'r') as file:
    medication_types = json.load(file)

class Condition:
    """
    A class to represent a medical condition for a patient.
    Attributes
    ----------
    patient : object
        The patient object associated with the condition.
    details_map : dict
        A dictionary to store details about the condition.
    detail_types : dict
        A dictionary to store types of details about the condition.
    code_map : dict
        A dictionary to map shorthand codes to detailed descriptions.
    code_keys : dict
        A dictionary to map shorthand keys to category titles.
    Methods
    -------
    pmhx_print():
        Returns a string representation of the condition class name.
    write_out_list(med_list, and_need=True):
        Converts a list of medications into a formatted string.
    assemble_what_found():
        Returns a default message indicating no specific condition code was overridden.
    input_condition_details():
        Prompts the user to input condition details in shorthand and parses the input.
    parse_shorthand(shorthand):
        Parses shorthand input into detailed condition information.
    print_condition_options():
        Prints available condition options based on the code map.
    is_on_med_class(class_tag):
        Checks if the patient is on a specific class of medication and returns a list of such medications.
    """
    def __init__(self, patient):
        self.patient = patient
        self.details_map = {}
        self.detail_types = {}
        self.code_map = {}
        self.code_keys = {}
    
    def pmhx_print(self):
        text = ""
        text += f"{__class__.__name__}"
        return text

    def assemble_what_found(self):
        text = "No code was overridden to look for condition specifics this condition."
        return text

    def input_condition_details(self):
        print(f"\nEnter details for {self.__class__.__name__} in shorthand:")
        self.print_condition_options()
        shorthand = input("Details: ")

        details = self.parse_shorthand(shorthand)
        
        print(f"Entered details: {details}")
        input("Press Enter to continue...")
        
        return details

    def parse_shorthand(self, shorthand):  
        details = {}
        for part in shorthand.split(';'):
            key = part[0]
            values = part[1:].split(',')
            if key in self.code_map:
                category_title = self.code_keys[key]
                details[category_title] = []
                for value in values:
                    if value in self.code_map[key]:
                        details[self.code_keys[key]].append(self.code_map[key][value])
                    else:
                        details[self.code_keys[key]].append(value)
                if len(details[self.code_keys[key]]) == 1:
                    details[self.code_keys[key]] = details[self.code_keys[key]][0]
            else:
                print(f"Invalid shorthand: {part}")
                input("Press Enter to continue...")
                return "Invalid details"
        return details

    def print_condition_options(self):
        for key, options in self.code_map.items():
            options_str = " | ".join([f"{k} - {v}" for k, v in options.items()])
            text = f"   {self.code_keys.get(key, "")}" 
            spacing = 22
            this_spaceing = spacing - len(self.code_keys.get(key, ""))
            text += f"{this_spaceing * ' '}{key}: {options_str}"
            print(text)

    def compare_home_hosp_meds(self, class_tag):
        home_list = self.is_on_med_class(class_tag)
        hosp_list = self.is_on_med_here(class_tag)
        if home_list == hosp_list:
            return home_list, "(continued in hospital)"
        elif len(home_list) > len(hosp_list):
            return home_list, "but not continued in hospital"
        elif len(home_list) < len(hosp_list):
            return hosp_list, "which is new in hospital"
        else:
            return [], "&your logic went weird&"

    def is_on_med_class(self, class_tag):
        med_list = []
        class_meds = [med_class for med_class in medication_types.keys() if class_tag in med_class]
        for med_dict in [self.patient.home_meds]:
            for med_name, med_details in med_dict.items():
                for class_med in class_meds:
                    if med_name.lower() in medication_types[class_med]:
                        med_list.append(med_name)
        return med_list

    def is_on_med_here(self, class_tag):
        med_list = []
        class_meds = [med_class for med_class in medication_types.keys() if class_tag in med_class]
        class_meds = medication_types.get(class_tag, [])
        for med_dict in [self.patient.hosp_meds]:
            for med_name, med_details in med_dict.items():
                if med_name.lower() in class_meds:
                    med_list.append(med_name)
        return med_list
        

    def is_condition_code_in_dictionary(self, condition, category):
        self.patient.pmhx.setdefault(category, [])
        for item in self.patient.pmhx[category]:
            if isinstance(item, condition):
                return True
        return False
    
    def get_pmhx_object_loc(self, condition, category):
        category_dict = self.patient.pmhx[category]
        for i in category_dict:
            if isinstance(i, condition):
                location = category_dict.index(i)
        return location


#CARDIAC
class CAD(Condition):
    def __init__(self, patient):
        super().__init__(patient)
        
        self.code_map = {
            "e": {"e": "Format is year, type of event, separated by a comma"},
            "p": {"y": "year", "t": "type"},
            "c": {"y": "year", "t": "type"},
        }

        self.code_keys = {
                "e": "Event",
                "p": "PCI",
                "c": "CABG",
            }
        
        self.details_map = {
        }

        self.assembly_text = self.assemble_what_found()

    def __repr__(self):
        return __class__.__name__

    def pmhx_print(self):
        # Extract the function status if available
        # Print the heading with the event in brackets
        text = f"Coronary Artery Disease"

        return text
    
    def chronic_issue_print(self):
        text = f"{__class__.__name__}"
        return text

    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def assemble_what_found(self):
        text = "No code was overridden to look for condition specifics this condition."
        return text

class CHF(Condition):
    def __init__(self, patient):
        super().__init__(patient)
        
        self.code_map = {
            "r": {"h": "Hypertension", "c": "CAD"},
            "f": {"p": "Preserved", "mr": "Moderately Reduced", "r": "Reduced"},
            "g": {"b": "beta blocker", "a": "ACE/ARB", "m": "MRA", "e": "Entresto", "s": "SGLT2 Inhibitor"},
            "e": {"#": "Enter ejection fraction in %"},
        }

        self.code_keys = {
                "r": "Risk Factors",
                "f": "Function",
                "g": "GDMT",
                "e": "Ejection Fraction"
            }
        
        self.details_map = {
        }

        self.assembly_text = self.assemble_what_found()

    def __repr__(self):
        return __class__.__name__

    def pmhx_print(self):
        # Extract the function status if available
        function_status = self.details_map.get('Function', 'Unknown Function Status')
        eject_fraction = self.details_map.get('Ejection Fraction', 'Unknown Ejection Fraction')
        
        # Print the heading with the function status in brackets
        text = f"Congestive Heart Failure ({function_status} - {eject_fraction}%)"
        
        # Print the rest of the details
        if 'Risk Factors' in self.details_map:
            text += f"\n  Risk Factors: {self.details_map['Risk Factors']}"
        if 'GDMT' in self.details_map:
            text += f"\n  GDMT: {self.details_map['GDMT']}"

        return text

    def chronic_issue_print(self):
        text = f"Heart Failure"
        if self.details_map.get('Function'):
            text += f"  (with {self.details_map['Function']} function)"

        on_dialysis = False
        diuretics = self.is_on_med_class("Diuretic")
        if self.is_condition_code_in_dictionary(CKD, "Nephrology"):
            if "Dialysis" in self.patient.pmhx["Nephrology"][self.get_pmhx_object_loc(CKD, "Nephrology")].details_map.keys():
                on_dialysis = True
        
        beta_blockers = self.is_on_med_class("Beta")
        ace_arbs = self.is_on_med_class("ACE")
        sglt2 = self.is_on_med_class("SGLT2")

        function_status = self.details_map.get('Function', 'Unknown Function Status')
        if function_status == "Reduced":
            text += f"\n      {pnons(self.patient.gender, 'p').capitalize()} ejection fraction is {self.details_map['Ejection Fraction']}% which is reduced. Patient should be on guideline directed medical therapy (GDMT). "
            if on_dialysis:
                text += f"As the patient has CKD and is on dialysis, they are at higher risk of cardiovascular complications. Furthermore, diuresis and volume management will best be left to nephrology's purview and there is no need for diuretics. "
        elif function_status == "Unknown":
            text += f"\n      {pnons(self.patient.gender, 'p').capitalize} ejection fraction is unknown. In order to determine if we need GDMT, we will need an echo. "

        gdmt_categories = [beta_blockers, ace_arbs, sglt2]
        if all(gdmt_categories):
            text += f"\n      Patient is on all appropriate meds for GDMT. "

        if beta_blockers:
            text += f"\n      Beta-blocker: {build_text_list(beta_blockers)} "
        if ace_arbs:
            text += f"\n      ACE/ARBs: {build_text_list(ace_arbs)} "
        if sglt2:
            text += f"\n      SGLT2 inhibitors: {build_text_list(sglt2)} "
        if diuretics:
            text += f"\n      Diuretics: {build_text_list(diuretics)} "
        
        #GDMT assessor
        


        
        
        return text

    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def assemble_what_found(self):
        text = "No code was overridden to look for condition specifics this condition."
        return text

class Hypertension(Condition):
    def __init__(self, patient):
        super().__init__(patient)

        self.antihypertensives = [med for med in self.is_on_med_here("Antihypertensive")]
       
        self.code_map = {
            "t": {"p": "primary", "s": "secondary"},
        }

        self.code_keys ={
            "t": "Type",
        }
        
        self.details_map = {
            "Antihypertensives": {
                "on_meds": self.antihypertensives,
                "med_count": len(self.antihypertensives),
                "med_list": [med for med in self.antihypertensives if self.antihypertensives]
            }
        }

        self.check_text = self.assemble_what_found()
    
    def __repr__(self):
        return __class__.__name__

    def run(self):
        print(self.check_text)
        self.details_map.update(self.input_condition_details())

    def assemble_what_found(self):
        text = ""
        if self.antihypertensives:
            text += f"Was able to fine the following -- Antihypertensives: {build_text_list(self.antihypertensives)}\n\n"
        else:
            text += f"Was not able to find anything relevant to {__class__.__name__} in other areas of database.\n\n"
        return text
    
    def pmhx_print(self):
        text = ""
        
        text += f"Hypertension"
        if self.details_map["Type"]:
            text += f" ({self.details_map['Type']})"

        # Number of agents
        med_count = self.details_map['Antihypertensives']['med_count']
        if med_count:
            count_text = f" {med_count} agents -"
        if self.antihypertensives:
            text += f"\n      {count_text} {build_text_list(self.antihypertensives)}"
        return text
    
    def chronic_issue_print(self):
        text = f"Hypertension"
        if self.antihypertensives:
            text += f"\n      Current agents are {build_text_list(self.antihypertensives)}."
        return text
    
class Dyslipidemia(Condition):
    def __init__(self, patient):
        super().__init__(patient)

        self.lipid_meds = self.is_on_med_class("Statins")

        self.code_map = {
            "f": {"s": "silent", "h": "hypertensive"},
        }
        
        self.details_map = {
            "on_statin": True if self.lipid_meds else False,
            "lipid_agents": [med for med in self.lipid_meds if self.lipid_meds]
        }

        self.assembly_text = self.assemble_what_found()

    def __repr__(self):
        return __class__.__name__
    
    def pmhx_print(self):
        text = f"Dyslipidemia"
        return text
    
    def chronic_issue_print(self):
        pass
    
    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def assemble_what_found(self):
        text = ""
        return text

class Afib(Condition):
    def __init__(self, patient):
        super().__init__(patient)

        self.code_map = {
            "e": {"e": "EtOH", "c": "Coronary Artery Disease", "t": "Thyroid Disease", "o": "OSA"},
            "t": {"p": "Paroxysmal", "r": "Persistent", "c": "Chronic"},
            "a": {"n": "None", "w": "Warfarin", "d": "DOAC"},
            "c": {"0": "0", "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6"},
            "s": {"1": "Class I", "2": "Class II", "3": "Class III", "4": "Class IV"}
        }

        self.code_keys = {
            "e": "Etiology",
            "t": "Type",
            "a": "Anticoagulation",
            "c": "CHADS Score",
            "s": "SAF Scale"
        }

        self.details_map = {}

        self.assembly_text = self.assemble_what_found()
    
    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def __repr__(self):
        return __class__.__name__
    
    def pmhx_print(self):
        text = f"Atrial Fibrillation"
        if 'Type' in self.details_map:
            text += f" ({self.details_map['Type']})"
        if 'Anticoagulation' in self.details_map:
            text += f"\n  Anticoagulation: {self.details_map['Anticoagulation']}"
        if 'CHADS Score' in self.details_map:
            text += f"\n  CHADS Score: {self.details_map['CHADS Score'][0]} {self.details_map['CHADS Score'][1] if self.details_map['CHADS Score'][1] else ''}"
        return text
    
    def assemble_what_found(self):
        text = ""
        if self.is_on_med_class("Anticoagulant"):
            self.details_map["Anticoagulation"] = self.is_on_med_class("Anticoagulant")
            text += f"Found that patient is on {self.is_on_med_class("Anticoagulant")}"
        else:
            self.details_map["Anticoagulation"] = "None"
            text += "No anticoagulation found in meds. "
        chads_score, chads_items = self.calculate_chads()
        self.details_map["CHADS Score"] = (chads_score, chads_items)
        text += "\n" + f"{chads_score}" + f"{(chads_items)}"
        return text
    
    def calculate_chads(self):
        chads_score = 0
        chads_items = ""
        
        #CHF
        chf = self.is_condition_code_in_dictionary(CHF, "Cardiology")
        if chf:
            chads_score += 1
            chads_items += "C"
        #HTN
        htn = self.is_condition_code_in_dictionary(Hypertension, "Cardiology")
        if htn:
            chads_score += 1
            chads_items += "H"

        if int(self.patient.age) >= 75:
            chads_score += 1
            chads_items += "A"
        
        dm = self.is_condition_code_in_dictionary(Diabetes, "Endocrinology")
        if dm:
            chads_score += 1
            chads_items += "D"

        return chads_score, chads_items
    
    def chronic_issue_print(self):
        print("\n\n     == Atrial Fibrillation ==")
        text = ""

        if 'SAF Scale' in self.details_map:
            saf_scale = self.details_map['SAF Scale']
        else:
            saf_scale = ""

        anticoagulated = self.is_on_med_class("Anticoagulant")
        ror_meds, ror_text = self.compare_home_hosp_meds("Afib Meds")
        
        #handle rate issues
        vital_sign_a = VitalSignAssessor(self.patient)

        tachycardia_episodes = vital_sign_a.get_specific_vital_abnormalities('Tachycar')
        latest_vitals_datetime = self.patient.vitals.vitals[-1][-1]

        vitals_text = "     "
        vitals_text += f"For rate control {pnons(self.patient.gender, "s")} is on {build_text_list(ror_meds)}, {ror_text}. "
        
        
        if tachycardia_episodes:
            string_dates = [dt.datetime.strftime(date, "%b %d") for date in tachycardia_episodes]
            if latest_vitals_datetime in tachycardia_episodes:
                vitals_text += f"Latest vitals show persistence of tachycardia, so we will consider increasing his meds/starting a new agent. "
            else:
                vitals_text += f"Tachycardia was recorded on {build_text_list(string_dates)}. Fortunately, latest vitals do not indicate ongoing tachycardia."
        
        #comment on anticoagulation
        
        anticoagulation_text = ""
        chads_score = self.details_map["CHADS Score"][0]
        if chads_score >= 1:
            if anticoagulated:
                anticoagulation_text += f" Qualifies for anticoagulation given CHADS of {chads_score}. "
            else:
                anticoagulation_text += f"Although CHADS score is {chads_score}, {pnons(self.patient.gender), "s"} is not on anticoagulation. "
        elif int(self.patient.age) >= 65:
            anticoagulation_text += f"Patient's CHADS score is 0, but CCS recommends anticoagulation for anyone with atrial fibrillation who is 65 and older. "
        else:
            anticoagulation_text += f"Given CHADS score of 0 and age <65, they do not need anticoagulation for atrial fibrillation. "
        anticoagulation_text += f"{pnons(self.patient.gender, "s")} is currently anticoagulated with {build_text_list(anticoagulated)}. "

        text += vitals_text
        text += anticoagulation_text

        #SAF scale
        if saf_scale:
            text += f"Patient reports symptoms consistent with {saf_scale} at baseline. "

        return text

#ENDO
class Diabetes(Condition):
    def __init__(self, patient):
        super().__init__(patient)

        self.code_map = {
            "t": {"1": "Type 1", "2": "Type 2"},
            "m": {"i": "Insulin", "o": "Oral Medications"},
            "a": {"#": "enter A1c value"},
            "c": {"b": "Neuropathy", "r": "Retinopathy", "n": "Nephropathy"}
        }

        self.code_keys = {
            "t": "Type",
            "m": "Medications",
            "a": "A1c",
            "c": "Complications"
        }

        self.details_map = {}

        self.assembly_text = self.assemble_what_found()

    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def __repr__(self):
        return __class__.__name__
    
    def pmhx_print(self):
        text = f"Diabetes"
        if 'Type' in self.details_map:
            text += f" ({self.details_map['Type']})"
        if 'A1c' in self.details_map:
            text += f" - A1c: {self.details_map['A1c']}%"
        if 'Medications' in self.details_map:
            text += f"\n  Medications: {build_text_list(self.details_map['Medications'])}"
        if 'Complications' in self.details_map:
            text += f"\n  Complications: {self.details_map["Complications"]}"
        return text
    
    def assemble_what_found(self):
        if "A1c" in self.patient.labs.pt_labs:
            last_a1c = self.patient.labs.pt_labs["A1c"][-1][1]
            self.details_map['A1c'] = last_a1c
            print("I found an A1c")

class Obesity(Condition):
    def __init__(self, patient):
        super().__init__(patient)

        self.code_map = {
            "w": {"#": "enter weight in kg"},
            "h": {"#": "enter height in cm"},
            "b": {"#": "enter BMI"},
            "c": {"#": "enter waist circumference in cm"}
        }

        self.code_keys = {
            "w": "Weight",
            "h": "Height",
            "b": "BMI",
            "c": "Waist Circumference"
        }

        self.details_map = {}

        self.assembly_text = self.assemble_what_found()

    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def __repr__(self):
        return __class__.__name__
    
    def pmhx_print(self):
        text = f"Obesity"
        if 'BMI' in self.details_map:
            text += f" - BMI of {self.details_map['BMI']}"
        if 'Weight' in self.details_map:
            text += f" ({self.details_map['Weight']} kg)"
        return text
    
    def assemble_what_found(self):
        text = "No code was overridden to look for condition specifics this condition."
        return text

#Nephrology
class CKD(Condition):
    def __init__(self, patient):
        super().__init__(patient)

        self.code_map = {
            "s": {"1": "Stage 1", "2": "Stage 2", "3": "Stage 3", "4": "Stage 4", "5": "Stage 5"},
            "d": {"h": "Hemodialysis", "p": "Peritoneal Dialysis", "n": "None"},
            "e": {"d": "Diabetes", "h": "Hypertension", "g": "Glomerulonephritis"},
            "w": {"m": "Monday", "t": "Tuesday", "w": "Wednesday", "th": "Thursday", "f": "Friday", "s": "Saturday", "su": "Sunday"},
            "b": {"#": "enter baseline creatinine"}
                
            }
        self.code_keys = {
            "s": "Stage",
            "d": "Dialysis",
            "e": "Etiology",
            "w": "Dialysis Days",
            "b": "Baseline Creatinine"
        }

        self.details_map = {}

        self.assembly_text = self.assemble_what_found()

    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def __repr__(self):
        return __class__.__name__
    
    def pmhx_print(self):
        text = f"Chronic Kidney Disease"
        if 'Baseline Creatinine' in self.details_map:
            text += f" - Baseline Creatinine: {self.details_map['Baseline Creatinine']}"
        if 'Stage' in self.details_map:
            text += f" - Stage {self.details_map['Stage']}"
        if 'Dialysis' in self.details_map:
            text += f"\n  Dialysis: {self.details_map['Dialysis']}"
        if 'Etiology' in self.details_map:
            text += f"\n  Etiology: {self.details_map['Etiology']}"
        if 'Dialysis Days' in self.details_map:
            text += f"\n  Dialysis Days: {self.details_map['Dialysis Days']}"
        

#Resp
class OSA(Condition):
    def __init__(self, patient):
        super().__init__(patient)

        self.code_map = {
            "s": {"m": "Mild", "m": "Moderate", "s": "Severe"},
            "c": {"y": "Compliant with treatment", "n": "Suspected non-compliance"},
        }

        self.code_keys = {
            "s": "Severity",
            "c": "Compliance"
        }

        self.details_map = {}

        self.assembly_text = self.assemble_what_found()

    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def __repr__(self):
        return __class__.__name__
    
    def pmhx_print(self):
        text = f"Obstructive Sleep Apnea"
        if 'Severity' in self.details_map:
            text += f" ({self.details_map['Severity']})"
        if "Compliance" in self.details_map:
            text += f"\n  {self.details_map['Compliance']}"
        return text

#GI
class Cirrhosis(Condition):
    def __init__(self, patient):
        super().__init__(patient)

        self.code_map = {
            "e": {"a": "Alcohol", "n": "Non-alcoholic", "v": "Viral", "a": "Autoimmune", "b": "Biliary", "m": "Metabolic", "g": "Genetic", "o": "Other"},
            "s": {"c": "Compensated", "d": "Decompensated"},
            "a": {"y": "Yes", "n": "No"},
            "v": {"y": "Yes", "n": "No"},
        }

        self.code_keys = {
            "e": "Etiology",
            "s": "Compensation Status",
            "a": "Ascites",
            "v": "Varices",
        }

        self.details_map = {}

        self.assembly_text = self.assemble_what_found()

    def run(self):
        print(self.assembly_text)
        self.details_map.update(self.input_condition_details())

    def __repr__(self):
        return __class__.__name__
    
    def pmhx_print(self):
        text = f"Cirrhosis"
        if 'Etiology' in self.details_map:
            text += f" ({self.details_map['Etiology']})"
        if 'Compensation Status' in self.details_map:
            text += f" - {self.details_map['Compensation Status']}"
        if 'Ascites' in self.details_map:
            text += f"\n  Ascites: {self.details_map['Ascites']}"
        if 'Varices' in self.details_map:
            text += f"\n  Varices: {self.details_map['Varices']}"
        return text