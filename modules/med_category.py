from .Conditions.conditions import Hypertension, Condition, Dyslipidemia, CHF, Afib, CAD, Diabetes, Obesity, CKD, OSA, Cirrhosis

class MedicalCategory:
    def __init__(self, patient):
        self.patient = patient
        self.details_map = {}
        self.detail_types = {}
        self.print_map = {}
        self.condition_map = {}
        self.precheck_map = {}

    def input_details(self):
        print(f"Class Selected: {self.__class__.__name__}")
        
        print("Available conditions:\n")
        for code, condition in self.condition_map.items():
            print(f"{code} - {condition}", end=" | ")
        condition_code = input("\n\nEnter the condition code: ")
        
        #remove previous instances of PMHX that may be outdated
        category_name = self.__class__.__name__
        self.patient.pmhx.setdefault(category_name, []) #will create category if not made
        for condition in self.patient.pmhx[category_name]:
            print(condition)
            if isinstance(condition, type(self.condition_map.get(condition_code, ""))):
                print("there is a match")
                self.patient.pmhx[category_name].remove(condition)
                print(f"{condition} was removed and a new one will be created")
            
        item = self.condition_map.get(condition_code)
        
        if isinstance(item, Condition):
            item.run() # Run the condition's input method
            self.patient.add_pmhx(category_name, item) # Add the condition to the patient's PMHxCategory's list
            print(f"Added {item} to {category_name}") #show how the dicitonary was constructed
        else:
            self.patient.add_pmhx(category_name, {condition_code: {}})
            print(f"Added {item} to {category_name} as just a history item.")


    def print_condition_options(self, condition):
        for key, options in self.details_map[condition].items():
            options_str = " | ".join([f"{k} - {v}" for k, v in options.items()])
            print(f"     {key}: {options_str}")

          
class Hematology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.details_map = {
            "Lymphoma": {
                "s": {"i": "Stage I", "ii": "Stage II", "iii": "Stage III", "iv": "Stage IV"},
                "t": {"c": "Chemotherapy", "r": "Radiation", "s": "Surgery"}
            }
        }
        self.detail_types = {
            "Lymphoma": {
                "s": "Stage",
                "t": "Treatment"
            }
        }
class InfectiousDisease(MedicalCategory):
    def __init__(self, patient):
        self.patient = patient
        self.details_map = {
            "Infective Endocarditis": {
                "o": {"n": "Native Valve", "p": "Prosthetic Valve"},
                "m": {"a": "Antibiotics", "s": "Surgery"}
            },
            "Hepatitis C": {
                "g": {"1": "Genotype 1", "2": "Genotype 2", "3": "Genotype 3", "4": "Genotype 4"},
                "t": {"d": "Direct Acting Antivirals", "i": "Interferon"},
                "r": {"r": "Responder", "nr": "Non-Responder"}
            },
            "Herpes Zoster Infection": {
                "s": {"a": "Acute", "c": "Chronic"},
                "t": {"a": "Antivirals", "p": "Pain Management"},
                "c": {"y": "Yes", "n": "No"}
            }
        }
        self.detail_types = {
            "Infective Endocarditis": {
                "o": "Origin",
                "m": "Management"
            },
            "Hepatitis C": {
                "g": "Genotype",
                "t": "Treatment",
                "r": "Response"
            },
            "Herpes Zoster Infection": {
                "s": "Stage",
                "t": "Treatment",
                "c": "Complications"
            }
        }

        self.condition_map = {
            "ie": "Infective Endocarditis",
            "hepc": "Hepatitis C",
            "hzi": "Herpes Zoster Infection"
        }

        self.print_map = {
            "Infective Endocarditis": lambda: self.print_infective_endocarditis_details(self.patient.pmhx["InfectiousDisease"]["Infective Endocarditis"]),
            "Hepatitis C": lambda: self.print_hepatitis_c_details(self.patient.pmhx["InfectiousDisease"]["Hepatitis C"]),
            "Herpes Zoster Infection": lambda: self.print_herpes_zoster_infection_details(self.patient.pmhx["InfectiousDisease"]["Herpes Zoster Infection"]),
        }

    def print_herpes_zoster_infection_details(self, herpes_zoster_infection_details):
        """
        Prints the details of a patient's herpes zoster infection in a specific format.
        
        Parameters:
        herpes_zoster_infection_details (dict): A dictionary containing the details of the patient's herpes zoster infection.
        """
        # Print the heading
        text = "Herpes Zoster Infection"
        
        # Print the rest of the details
        if 's' in herpes_zoster_infection_details:
            text += f"\n  Stage: {herpes_zoster_infection_details['s']}"
        if 't' in herpes_zoster_infection_details:
            text += f"\n  Treatment: {herpes_zoster_infection_details['t']}"
        if 'c' in herpes_zoster_infection_details:
            text += f"\n  Complications: {herpes_zoster_infection_details['c']}"

        return text

class Cardiology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.condition_map = {
            "hf": CHF(patient),
            "af": Afib(patient),
            "cad": CAD(patient),
            "htn": Hypertension(patient),
            "dl": Dyslipidemia(patient),
        }

class Endocrinology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)
        
        self.condition_map = {
            "d": Diabetes(patient),
            "o": Obesity(patient),
            "ht": "Hypothyroidism",
            "hyp": "Hypoparathyroidism",
        }

        self.details_map = {
            
            "Hypothyroidism": {
                "m": {"l": "Levothyroxine"}
            },
            "Hypoparathyroidism": {
                "c": {"a": "Autoimmune", "s": "Surgical"},
                "m": {"c": "Calcium", "v": "Vitamin D"}
            }
        }
        self.detail_types = {
         
            "Hypothyroidism": {
                "m": "Medications"
        },
            "Hypoparathyroidism": {
                "c": "Cause",
                "m": "Medications"
        }}
        self.print_map = {
        
            "Hypothyroidism": lambda: self.print_hypothyroidism_details(self.patient.pmhx["Endocrinology"]["Hypothyroidism"]),
            "Hypoparathyroidism": lambda: self.print_hypoparathyroidism_details(self.patient.pmhx["Endocrinology"]["Hypoparathyroidism"]),
        }
    
    
    def print_hypothyroidism_details(self, hypothyroidism_details):
        """
        Prints the details of a patient's hypothyroidism in a specific format.
        
        Parameters:
        hypothyroidism_details (dict): A dictionary containing the details of the patient's hypothyroidism.
        """
        
        # Print the heading with the severity in brackets
        text = f"Hypothyroidism"
        
        # Print the rest of the details
        if 'm' in hypothyroidism_details:
            text += f" ({hypothyroidism_details['m']})"

        return text
    
    def print_hypoparathyroidism_details(self, hypoparathyroidism_details):
        """
        Prints the details of a patient's hypoparathyroidism in a specific format.
        
        Parameters:
        hypoparathyroidism_details (dict): A dictionary containing the details of the patient's hypoparathyroidism.
        """
        
        # Print the heading with the severity in brackets
        text = f"Hypoparathyroidism"
        
        # Print the rest of the details
        if 'c' in hypoparathyroidism_details:
            text += f"\n  Cause: {hypoparathyroidism_details['c']}"
        if 'm' in hypoparathyroidism_details:
            text += f"\n  Medications: {hypoparathyroidism_details['m']}"

        return text

class Gastroenterology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.condition_map = {
            "o": "Obstruction",
            "g": "GERD",
            "gib": "GI Bleed",
            "cir": Cirrhosis(patient),
        }
        self.details_map = {
            "GERD": {
                "t": {"p": "PPI", "h": "H2 Blocker"}
            },
            "Crohn’s": {
                "a": {"i": "Ileal", "c": "Colonic", "i+c": "Ileocolonic"},
                "m": {"n": "None", "s": "Steroids", "i": "Immunomodulators"}
            },
            "Obstruction": {
                "e": {"e": "Event details in format year, type, separated by a comma"},
                "t": {"s": "Surgery", "d": "Decompression"}
            },
            "GI Bleed": {
                "s": {"u": "Upper", "l": "Lower"},
                "c": {"v": "Variceal", "n": "Non-variceal"},
                "t": {"e": "Endoscopic", "m": "Medical", "s": "Surgical"}
            }
        }
        self.detail_types = {
            "GERD": {
                "s": "Severity",
                "t": "Treatment"
            },
            "Crohn’s": {
                "a": "Affected Area",
                "m": "Medications"
            },
            "Obstruction": {
                "e": "Event",
                "t": "Treatment Type"
            },
            "GI Bleed": {
                "s": "Site",
                "c": "Cause",
                "t": "Treatment"
            }
        }
        self.print_map = {
            "Obstruction": lambda: self.print_obstruction_details(self.patient.pmhx["Gastroenterology"]["Obstruction"]),
            "GERD": lambda: self.print_gerd_details(self.patient.pmhx["Gastroenterology"]["GERD"]),
            "GI Bleed": lambda: self.print_gi_bleed_details(self.patient.pmhx["Gastroenterology"]["GI Bleed"]),
        }

    def print_obstruction_details(self, obstruction_details):
        """
        Prints the details of a patient's bowel obstruction in a specific format.
        
        Parameters:
        obstruction_details (dict): A dictionary containing the details of the patient's bowel obstruction.
        """
        # Print the heading
        text = "Bowel Obstruction"
        
        # Print the rest of the details
        if 'e' in obstruction_details:
            text += f"\n  Event(s): {obstruction_details['e']}"
        if 'p' in obstruction_details:
            text += f"\n  Pseudo vs Nonpseudo: {obstruction_details['p']}"
        if 't' in obstruction_details:
            text += f"\n  Treatment: {obstruction_details['t']}"

        return text

    def print_gerd_details(self, gerd_details):
        """
        Prints the details of a patient's GERD in a specific format.
        
        Parameters:
        gerd_details (dict): A dictionary containing the details of the patient's GERD.
        """
        # Extract the severity of GERD if available
        
        # Print the heading with the severity in brackets
        text = f"Gastroesophageal Reflux Disease"
        
        # Print the rest of the details
        if 't' in gerd_details:
            text += f" ({gerd_details['t']})"

        return text

    def print_gi_bleed_details(self, gi_bleed_details):
        """
        Prints the details of a patient's GI bleed in a specific format.
        
        Parameters:
        gi_bleed_details (dict): A dictionary containing the details of the patient's GI bleed.
        """
        # Print the heading
        text = "GI Bleed"
        
        # Print the rest of the details
        if 's' in gi_bleed_details:
            text += f"\n  Site: {gi_bleed_details['s']}"
        if 'c' in gi_bleed_details:
            text += f"\n  Cause: {gi_bleed_details['c']}"
        if 't' in gi_bleed_details:
            text += f"\n  Treatment: {gi_bleed_details['t']}"

        return text

class Nephrology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)

        self.condition_map = {
            "ckd": CKD(patient),
        }


    def print_ckd_details(self, ckd_details):
        """
        Prints the details of a patient's chronic kidney disease in a specific format.
        
        Parameters:
        ckd_details (dict): A dictionary containing the details of the patient's chronic kidney disease.
        """
        
        # Print the heading with the stage in brackets
        text = f"Chronic Kidney Disease"
        
        # Print the rest of the details
        if 'd' in ckd_details:
            text += f"\n  {ckd_details['d']}"
            text += f" {ckd_details['w']}" if 'w' in ckd_details else ""
        if 'e' in ckd_details:
            text += f"\n  Etiology: {ckd_details['e']}"

        return text

class Neurology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.condition_map = {
            "s": "Stroke",
            "e": "Epilepsy",
            "p": "Parkinson's",
            "d": "Dementia"
        }
        
        self.details_map = {
            "Stroke": {
                "t": {"i": "Ischemic", "h": "Hemorrhagic"},
                "s": {"m": "Mild", "mo": "Moderate", "se": "Severe"},
                "e": {"e": "Event details in format year, type, separated by a comma"}
            },
            "Epilepsy": {
                "f": {"g": "Generalized", "p": "Partial"},
                "m": {"n": "None", "a": "Antiepileptic Drugs"},
            },
            "Parkinson's": {
                "s": {"m": "Mild", "mo": "Moderate", "se": "Severe"},
                "m": {"n": "None", "l": "Levodopa", "d": "Dopamine Agonists"},
                "c": {"s": "Swallowing", "m": "Memory", "o": "Mood"},
                "b": {"b": "Baseline function details"}
            },
            "Dementia": {
                "t": {"a": "Alzheimer's", "v": "Vascular", "l": "Lewy Body", "f": "Frontotemporal"},
                "s": {"m": "Mild", "mo": "Moderate", "se": "Severe"},
                "m": {"n": "None", "d": "Donepezil", "r": "Rivastigmine", "g": "Galantamine"}
            }
        }
        self.detail_types = {
            "Stroke": {
                "t": "Type",
                "s": "Severity",
                "e": "Event(s)"
            },
            "Epilepsy": {
                "f": "Form",
                "m": "Medications"
            },
            "Parkinson's": {
                "s": "Severity",
                "m": "Medications",
                "c": "Complications",
                "b": "Baseline"
            },
            "Dementia": {
                "t": "Type",
                "s": "Severity",
                "m": "Medications"
            }
        }

        self.print_map = {
            "Parkinson's": lambda: self.print_parkinsons_details(self.patient.pmhx["Neurology"]["Parkinson's"]),
            "Dementia": lambda: self.print_dementia_details(self.patient.pmhx["Neurology"]["Dementia"]),
        }

    def print_parkinsons_details(self, parkinsons_details):
        """
        Prints the details of a patient's Parkinson's disease in a specific format.
        
        Parameters:
        parkinsons_details (dict): A dictionary containing the details of the patient's Parkinson's disease.
        """
        
        # Print the heading with the severity in brackets
        text = f"Parkinson's Disease"
        
        # Print the rest of the details
        if 's' in parkinsons_details:
            text += f"\n  Severity: {parkinsons_details['s']}"
        if 'm' in parkinsons_details:
            text += f"\n  Medications: {parkinsons_details['m']}"
        if 'c' in parkinsons_details:
            text += f"\n  Complications: {parkinsons_details['c']}"
        if 'b' in parkinsons_details:
            text += f"\n  Baseline Function: {parkinsons_details['b']}"

        return text

    def print_dementia_details(self, dementia_details):
        """
        Prints the details of a patient's dementia in a specific format.
        
        Parameters:
        dementia_details (dict): A dictionary containing the details of the patient's dementia.
        """
        # Print the heading
        text = "Dementia"
        
        # Print the rest of the details
        if 't' in dementia_details:
            text += f"\n  Type: {dementia_details['t']}"
        if 's' in dementia_details:
            text += f"\n  Severity: {dementia_details['s']}"
        if 'm' in dementia_details:
            text += f"\n  Medications: {dementia_details['m']}"

        return text

class Oncology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.details_map = {
            "Lung Cancer": {
                "s": {"i": "Stage I", "ii": "Stage II", "iii": "Stage III", "iv": "Stage IV"},
                "t": {"c": "Chemotherapy", "r": "Radiation", "s": "Surgery"}
            },
            "Urothelial Carcinoma": {
                "s": {"i": "Stage I", "ii": "Stage II", "iii": "Stage III", "iv": "Stage IV"},
                "t": {"c": "Chemotherapy", "r": "Radiation", "s": "Surgery", "i": "Immunotherapy"},
                "d": {"name": "Enter the name of the oncologist following the patient"},
            }
        }
        self.detail_types = {
            "Lung Cancer": {
                "s": "Stage",
                "t": "Treatment"
            },
            "Urothelial Carcinoma": {
                "s": "Stage",
                "t": "Treatment Received"
            }
        }

        self.print_map = {
            "Urothelial Carcinoma": lambda: self.print_urothelial_carcinoma_details(self.patient.pmhx["Oncology"]["Urothelial Carcinoma"]),
        }

    def print_urothelial_carcinoma_details(self, urothelial_carcinoma_details):
        """
        Prints the details of a patient's urothelial carcinoma in a specific format.
        
        Parameters:
        urothelial_carcinoma_details (dict): A dictionary containing the details of the patient's urothelial carcinoma.
        """
        # Print the heading
        text = "Urothelial Carcinoma"
        
        # Print the rest of the details
        if 's' in urothelial_carcinoma_details:
            text += f"\n  Stage: {urothelial_carcinoma_details['s']}"
        if 't' in urothelial_carcinoma_details:
            text += f"\n  Treatment: {urothelial_carcinoma_details['t']}"
        if 'd' in urothelial_carcinoma_details:
            text += f"\n  Oncologist: {urothelial_carcinoma_details['d']}"

        return text

class Respirology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.condition_map = {
            "osa": OSA(patient),
            "copd": "COPD"
        }
        self.details_map = {
            
            "COPD": {
                "s": {"m": "Mild", "mo": "Moderate", "se": "Severe", "v": "Very Severe"},
                "t": {"b": "LABA", "m": "LAMA", "i": "ICS", "s": "Steroids"},
                "o": {"#": "Enter the amount of home oxygen in L/min"},
            }
        }
        self.detail_types = {
            
            "COPD": {
                "s": "Severity",
                "t": "Treatment",
                "o": "Home Oxygen"
            }
        }

        self.print_map = {
            "COPD": lambda: self.print_copd_details(self.patient.pmhx["Respirology"]["COPD"]),
        }

    def print_copd_details(self, copd_details):
        """
        Prints the details of a patient's COPD in a specific format.
         
        Parameters:
        copd_details (dict): A dictionary containing the details of the patient's COPD.
        """
        # Print the heading
        text = "COPD"
        
        # Print the rest of the details
        if 's' in copd_details:
            text += f"\n  Severity: {copd_details['s']}"
        if 't' in copd_details:
            text += f"\n  Treatment: {copd_details['t']}"

        return text

class Rheumatology(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)
        self.condition_map = {
            "ra": "Rheumatoid Arthritis",
            "g": "Gout",
            "op": "Osteoporosis"
        }
        self.details_map = {
            "Rheumatoid Arthritis": {
                "s": {"a": "Active", "r": "Remission"},
                "m": {"n": "NSAIDs", "d": "DMARDs", "b": "Biologics"}
            },
            "Gout": {
                "f": {"a": "Acute", "c": "Chronic"},
                "m": {"n": "None", "a": "Allopurinol", "f": "Febuxostat", "p": "Probenecid"},
                "t": {"y": "Year of first attack"}
            },
            "Osteoporosis": {
                "s": {"m": "Mild", "mo": "Moderate", "se": "Severe"},
                "t": {"b": "Bisphosphonates", "d": "Denosumab", "r": "Raloxifene"}
            }
        }
        self.detail_types = {
            "Rheumatoid Arthritis": {
                "s": "Status",
                "m": "Medications"
            },
            "Gout": {
                "f": "Form",
                "m": "Medications",
                "t": "Timeline"
            },
            "Osteoporosis": {
                "s": "Severity",
                "t": "Treatment"
            }
        }

        self.print_map = {
            "Rheumatoid Arthritis": lambda: self.print_rheumatoid_arthritis_details(self.patient.pmhx["Rheumatology"]["Rheumatoid Arthritis"]),
            "Gout": lambda: self.print_gout_details(self.patient.pmhx["Rheumatology"]["Gout"]),
            "Osteoporosis": lambda: self.print_osteoporosis_details(self.patient.pmhx["Rheumatology"]["Osteoporosis"]),
        }

    def print_gout_details(self, gout_details):
        """
        Prints the details of a patient's gout in a specific format.
        
        Parameters:
        gout_details (dict): A dictionary containing the details of the patient's gout.
        """
        # Print the heading
        text = "Gout"
        
        # Print the rest of the details
        if 'f' in gout_details:
            text += f"\n  Form: {gout_details['f']}"
        if 'm' in gout_details:
            text += f"\n  Medications: {gout_details['m']}"
        if 't' in gout_details:
            text += f"\n  Year of first attack: {gout_details['t']}"

        return text
    
    def print_rheumatoid_arthritis_details(self, rheumatoid_arthritis_details):
        """
        Prints the details of a patient's rheumatoid arthritis in a specific format.
        
        Parameters:
        rheumatoid_arthritis_details (dict): A dictionary containing the details of the patient's rheumatoid arthritis.
        """
        # Print the heading
        text = "Rheumatoid Arthritis"
        
        # Print the rest of the details
        if 's' in rheumatoid_arthritis_details:
            text += f"\n  Status: {rheumatoid_arthritis_details['s']}"
        if 'm' in rheumatoid_arthritis_details:
            text += f"\n  Medications: {rheumatoid_arthritis_details['m']}"

        return text
    
    def print_osteoporosis_details(self, osteoporosis_details):
        """
        Prints the details of a patient's osteoporosis in a specific format.
        
        Parameters:
        osteoporosis_details (dict): A dictionary containing the details of the patient's osteoporosis.
        """
        # Print the heading
        text = "Osteoporosis"
        
        # Print the rest of the details
        if 's' in osteoporosis_details:
            text += f"\n  Severity: {osteoporosis_details['s']}"
        if 't' in osteoporosis_details:
            text += f"\n  Treatment: {osteoporosis_details['t']}"

        return text

class Other(MedicalCategory):
    def __init__(self, patient):
        super().__init__(patient)

        self.condition_map = {
            "bph": "BPH",
            "nl": "Nephrolithiasis",
            "ccy": "Cholecystectomy",
            "surg": "Surgery",
            "mh": "Mental Health"
        }

        self.details_map = {
            "BPH": {
                "m": {"t": "Tamsulosin", "f": "Finasteride", "d": "Dutasteride"}
            },
            "Nephrolithiasis": {
                "l": {"c": "Calcium", "u": "Uric Acid", "s": "Struvite", "c": "Cystine"},
                "s": {"p": "Passable", "u": "Unpassable"},
                "t": {"c": "Conservative", "s": "Surgical"},
                "z": {"#": "Enter size in mm"}
            },
            "Surgery": {
                "d": {"y": "Year of surgery"},
                "e": {"e": "Enter details of surgeries separated by |"}
            }, 
            "Mental Health": {
                "e": {"e": "Enter details of MH issues separated by |"}
        }}
        
        self.detail_types = {
            "BPH": {
                "m": "Medication"
            },
            "Nephrolithiasis": {
                "l": "Stone Type",
                "s": "Passability",
                "t": "Treatment",
                "z": "Size"
            },
            "Surgery": {
                "e": "General Surgery Input"
            }
        }

        self.print_map = {
            "BPH": lambda: self.print_bph_details(self.patient.pmhx["Other"]["BPH"]),
            "Nephrolithiasis": lambda: self.print_nephrolithiasis_details(self.patient.pmhx["Other"]["Nephrolithiasis"]),
            "Surgery": lambda: self.print_surgery_details(self.patient.pmhx["Other"]["Surgery"]),
        }

    def print_bph_details(self, bph_details):
        """
        Prints the details of a patient's benign prostatic hyperplasia (BPH) in a specific format.
        
        Parameters:
        bph_details (dict): A dictionary containing the details of the patient's BPH.
        """
        # Print the heading
        text = "Benign Prostatic Hyperplasia"
        
        # Print the medication details
        if 'm' in bph_details:
            text += f"  ({bph_details['m']})"

        return text
    
    def print_nephrolithiasis_details(self, nephrolithiasis_details):
        """
        Prints the details of a patient's nephrolithiasis in a specific format.
        
        Parameters:
        nephrolithiasis_details (dict): A dictionary containing the details of the patient's nephrolithiasis.
        """
        
        # Print the heading with the stone type in brackets
        text = f"Nephrolithiasis"
        
        # Print the rest of the details
        if 'l' in nephrolithiasis_details:
            text += f"\n  Stone Type: {nephrolithiasis_details['l']}"
        if 's' in nephrolithiasis_details:
            text += f"\n  Passability: {nephrolithiasis_details['s']}"
        if 't' in nephrolithiasis_details:
            text += f"\n  Treatment: {nephrolithiasis_details['t']}"
        if 'z' in nephrolithiasis_details:
            text += f"\n  Size: {nephrolithiasis_details['z']} mm"

        return text
  
    def print_surgery_details(self, surgery_details):
        """
        Prints the details of a patient's surgeries in a specific format.
        
        Parameters:
        surgery_details (dict): A dictionary containing the details of the patient's surgeries.
        """
        # Print the heading
        text = "Past Surgical Procedures:"
        
        # Print the rest of the details
        if 'e' in surgery_details:
            surgeries_list = surgery_details['e'].split("|")
            for surgery in surgeries_list:
                text += f"\n  {surgery}"

        return text
