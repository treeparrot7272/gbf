def get_suggestions(findings):
    """
    Analyze the findings and return a list of suggestions based on keywords.
    """
    suggestions = []
    keyword_mapping = {
        "NG ": ["Feeding tube well placed", "Feeding tube needs advancement"],
        "feeding tube": ["Feeding tube well placed", "Feeding tube needs advancement"],
        "Abdomen": ["No free fluid", "Free fluid present", "No free air", "Free air present", "Fecal loading", "No bowel obstruction", "Bowel obstruction present", "No gallstones", "Gallstones present", "No renal stones", "Renal stones present"],
        "Chest": ["Pleural effusion", "No pleural effusion", "No pulmonary edema", "Evidence of pulmonary edema", "Consolidation present", "No consolidation", "Nonspecific pulmonary nodules", "Pulmonary nodules present", "No pulmonary embolism", "Pulmonary embolism present", "Heart enlargement", "No heart enlargement", "No pneumothorax", "Pneumothorax present", "No mediastinal shift", "Mediastinal shift present"],
        "CT Brain": ["Acute intracranial hemorrhage present", "No midline shift", "Midline shift present", "Nil acute intracranial abnormality", "Hematomas - stable/chronic", "Hematomas - acute"],
        "CT Chest Abdomen Pelvis": ["No evidence of malignancy", "Evidence of malignancy"],
        "MR": ["Study not performed"],
        "US Kidney": ["No hydronephrosis", "Hydronephrosis present", "No renal stones", "Renal stones present"],
    }

    for keyword, suggestion_list in keyword_mapping.items():
        if keyword in findings:
            suggestions.extend(suggestion_list)  # Add all suggestions for the keyword

    return suggestions