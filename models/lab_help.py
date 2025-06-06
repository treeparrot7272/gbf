# Description: This file contains the Lab class and LabAnalysis class. The Lab class is used to store lab results and the LabAnalysis class is used to analyze lab results. The LabAnalysis class has methods to compare lab trends and assess lab ranges. The lab_norms dictionary contains normal ranges for various lab tests. The LabAnalysis class is used to analyze lab results and print a summary of the analysis.

lab_skip = [
    'St Boniface',
    'Procedure/Order ID:',
]

lab_categories = {
    "cbc": ["HGB", "MCV", "PLT", "WBC"],
    "Electrolyes": ["Sodium Level", "Potassium Level", "Chloride Level", "CO2 Total", "Urea", "Creatinine (Plasma)", "Calcium Level", "Phosphate Level", "Magnesium Level"],
    "Liver": ["ALT.", "AST..", "Alkaline Phosphatase", "GGT", "INR", "PT"]
    
}

replacement_dictionary = {
            "Sodium Level": "Na",
            "Potassium Level": "K",
            "Chloride Level": "Cl",
            "CO2 Total": "Bicarb",
            "Urea": "Urea",
            "Creatinine (Plasma)": "Cr",
            "Bilirubin Total": "Bili T",
            "ALT.": "ALT",
            "AST..": "AST",
            "Alkaline Phosphatase": "ALP",
            "C-Reactive Protein": "CRP",
            "Triglycerides Non-Fasting": "TG",
            "NT-proBNP": "BNP",
            "Prothrombin Time.": 'PT',
            "Troponin T High Sensitivity": "Troponin",
        }

lab_ref = {
'Abs Basophils': '',
'Abs Eosinophils': '',
'Abs Lymphocytes': '',
'Abs Immature Gran': '',
'Abs Monocytes': '',
'Abs Neutrophils': '',
'Basophils percent': '',
'Eosinophils percent': '',
'HCT': '',
'HGB': '',
'INR': '',
'Immature Gran percent': '',
'Lymphocytes percent': '',
'MCH': '',
'MCHC': '',
'MCV': '',
'MPV': '',
'Monocytes percent': '',
'Neutrophils percent': '',
'PLT': '',
'Prothrombin Time.': '',
'RBC': '',
'RDW': '',
'WBC': '',
'Sodium Level': '',
'Potassium Level': '',
'Chloride Level': '',
'CO2 Total': '',
'Anion Gap': '',
'Glucose Level': '',
'Urea': '',
'Creatinine (Plasma)': '',
'Urea/Creatinine Ratio': '',
'Calcium Level': '',
'Magnesium Level': '',
'Phosphate Level': '',
'Creatine Kinase': '',
'Troponin T High Sensitivity': '',
'Venous pH': '',
'Venous CO2': '',
'Venous O2': '',
'Venous Bicarbonate': '',
'Venous Base Excess': '',
'Venous Saturation': '',
'Haemoglobin': '',
'Venous O2 Content': '',
'Potassium - Blood Gas': '',
'Ionic Calcium - Blood Gas': '',
'Venous Lactate': '',
'Glucose - Blood Gas': '',
'Arterial pH': '',
'Arterial CO2': '',
'Arterial O2': '',
'Arterial Bicarbonate': '',
'Arterial Base Excess': '',
'Arterial Saturation': '',
'TSH': '',
'Free T4': '',
'C-Reactive Protein': '',
'Triglycerides Non-Fasting': '',
'NT-proBNP': '',
'Albumin': '',
"ALT.": "",
"AST..": "",
"Alkaline Phosphatase": "",
"GGT": "",


}

lab_norms = {
    "Troponin": (0, 20),
    "Na": (135, 145),
    "K": (3.5, 5.2),
    "Cl": (98, 108),
    "Bicarb": (22, 29),
    "Urea": (3.0, 8.0),
    "Cr": (30, 110),
    "Bili T": (0, 21),
    "ALT": (0, 55),
    "AST": (0, 34),
    "ALP": (30, 120),
    "GGT": (0, 55),
    "INR": (0.9, 1.1),
    "PT": (11, 13),
    "CRP": (0, 5),
    "TG": (0, 1.7),

}





    
