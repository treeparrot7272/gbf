
def handle_fall(patient, form_data):
    """
    Updates the patient dictionary with fall-related information.

    Args:
        patient (dict): The patient dictionary to update.
        form_data (dict): The fall data to add to the patient dictionary.
    """

    # Extract fall-related data from the form
    fall_date = form_data.get('fall_date')
    fall_lost_consciousness = form_data.get('fall_lost_consciousness')
    fall_seizure = form_data.get('seizure_activity')
    fall_hit_head = form_data.get('hit_head')

    # Update the patient's history with the fall data
    if 'fall' not in patient.history:
        patient.history['fall'] = {}
    patient.history['fall'].update({
        'fall_date': fall_date,
        'fall_lost_consciousness': True if fall_lost_consciousness == 'on' else False,
        'fall_seizure': True if fall_seizure == 'on' else False,
        'fall_hit_head': True if fall_hit_head == 'on' else False
    })

def handle_confusion(patient, form_data):
    # Update the patient's history with the confusion data
    if 'confusion' not in patient.history:
        patient.history['confusion'] = {}
    confusion_onset_date = form_data.get('confusion_date')
    confusion_acute_onset = form_data.get('confusion_acute_onset')
    confusion_fluctuating = form_data.get('confusion_fluctuating')
    inattention = form_data.get('inattention')
    disorganized_thoughts = form_data.get('disorganized_thoughts')
    altered_level_of_consciousness = form_data.get('altered_level_of_consciousness')
    # Extract confusion-related data from the form
    confusion_noticed_by = form_data.get('confusion_noticed_by')
    
    
    ##############
    patient.history['confusion'] = {
        'confusion_onset_date': confusion_onset_date,
        'confusion_acute_onset': True if confusion_acute_onset == 'on' else False,
        'confusion_fluctuating': True if confusion_fluctuating == 'on' else False,
        'inattention': True if inattention == 'on' else False,
        'disorganized_thoughts': True if disorganized_thoughts == 'on' else False,
        'altered_level_of_consciousness': True if altered_level_of_consciousness == 'on' else False,
        'confusion_noticed_by': confusion_noticed_by
    }
    

HISTORY_HANDLERS = {
    'fall': handle_fall,
    'confusion': handle_confusion
    # Add other history handlers here as needed
}
