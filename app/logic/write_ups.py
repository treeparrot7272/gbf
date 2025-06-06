from utils.gb_ai import pnons

def fall_write_up(patient):
    """Generates a write-up for the patient's fall history."""
    fall_history = patient.history.get('Fall', {})
    if not fall_history:
        return "No fall history available."
    
    gender = patient.gender

    write_up = f""
    write_up += f"{pnons(gender, "s").capitalize()} experienced a fall on {fall_history.get('fall_date', 'unknown date')[5:]}.\n"
    if fall_history.get('fall_lost_consciousness'):
        write_up += "The patient lost consciousness during the fall.\n"
    else:
        write_up += "No reported loss of consciousness during or after the fall.\n"
    if fall_history.get('fall_seizure'):
        write_up += "The patient experienced seizure activity during the fall.\n"
    else:
        write_up += "No reported seizure-like activity or evidence of fecal/urinary incontinence.\n"
    if fall_history.get('fall_hit_head'):
        write_up += f"{pnons(gender, "s").capitalize()} did hit {pnons(gender, "p")} head during the fall.\n"
    else:
        write_up += "The patient did not hit their head during the fall.\n"
    return write_up

def confusion_write_up(patient):
    """Generates a write-up for the patient's altered level of consciousness (confusion) history."""
    confusion_history = patient.history.get('confusion', {})
    if not confusion_history:
        return "No ALOC history available"
    
    g = patient.gender

    writeup = f""
    writeup += f"{pnons(g, "s").capitalize()} experienced onset of confusion around {confusion_history.get('confusion_onset_date', 'unknown date')[5:]}.\n"

    if confusion_history.get('confusion_acute_onset'):
        writeup += "Onset was acute.  "

    if confusion_history.get('confusion_fluctuating'):
        writeup += "It has been notably fluctuating.  "

    if confusion_history.get('inattention'):
        writeup += "Exam showed evidence of inattention. "

    if confusion_history.get('disorganized_thoughts'):
        writeup += "Exam shows evidence of disorganized thoughts. "
    if confusion_history.get('altered_level_of_consciousness'):
        writeup += f"{pnons(g, "s").capitalize()} is showing signs of altered level of consciousness. "

    if confusion_history.get('confusion_noticed_by'):
        writeup += f"The confusion was first noticed by {confusion_history.get('confusion_noticed_by', 'unknown')}. "
    
    return writeup

# Add more write-up functions here
def chf_write_up(patient):
    """Generates a write-up for CHF history."""
    # Example implementation
    return "CHF write-up goes here."

def diabetes_write_up(patient):
    """Generates a write-up for diabetes history."""
    # Example implementation
    return "Diabetes write-up goes here."