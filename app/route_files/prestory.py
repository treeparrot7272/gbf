from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from utils.gb_ai import get_pt_list, save_pt_list
from app.logic.history_logic import HISTORY_HANDLERS
from app.logic import write_ups  # Import the module containing all write-up functions

prestory_bp = Blueprint('prestory', __name__)

@prestory_bp.route('/prestory/<int:index>', methods=['GET', 'POST'])
def prestory(index):
    """Render the Prestory form and handle updates to patient details."""
    pt_list = get_pt_list()  # Retrieve the patient list from the session
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404

    patient = pt_list[index]  # Get the patient by their index

    # Ensure the presenting_complaint attribute exists
    patient_history = getattr(patient, 'history', None)

    complaint_forms = {
        "fall": {"id": "Fall", "heading": "Fall", "template": "history_forms/fall.html"},
        "confusion": {"id": "confusion", "heading": "Confusion", "template": "history_forms/confusion.html"},
        # Add more conditions as needed
    }

    if request.method == 'POST':
        # Update patient details from the form
        initials = request.form.get('initials')
        patient.i1 = initials[0] if len(initials) > 0 else ''
        patient.i2 = initials[1] if len(initials) > 1 else ''
        patient.age = request.form.get('age')
        patient.gender = request.form.get('gender')
        patient.admit_date = request.form.get('admit_date')

        # Handle complaint-specific logic
        selected_complaints = request.form.getlist('patient_history')  # Get all selected complaints as a list
        for complaint in selected_complaints:
            print(f"Handling complaint: {complaint}")
            if complaint in HISTORY_HANDLERS:
                # Call the appropriate handler function for the complaint
                HISTORY_HANDLERS[complaint](patient, request.form)

        save_pt_list(pt_list)  # Save the updated list back to the session

        # Check which button was clicked
        if request.form.get('action') == 'refresh':
            # Reload the prestory.html page
            return redirect(url_for('prestory.prestory', index=index))
        else:
            # Redirect to patient_details.html
            return redirect(url_for('patient_details', index=index))

    return render_template('prestory.html', index=index, patient=patient, complaint_forms=complaint_forms, patient_history=patient_history)


@prestory_bp.route('/get_write_up/<history_item>', methods=['GET'])
def get_write_up(history_item):
    """Return the write-up for a specific history item."""
    pt_list = get_pt_list()
    index = int(request.args.get('index', 0))  # Get patient index from query params
    print(f"Fetching write-up for: {history_item} with index: {index}")

    if index < 0 or index >= len(pt_list):
        print("Invalid patient index.")
        return "Patient not found.", 404

    patient = pt_list[index]
    print(f"Patient data: {patient}")

    # Dynamically load the write-up function
    function_name = f"{history_item.lower()}_write_up"
    write_up_function = getattr(write_ups, function_name, None)

    if write_up_function:
        return write_up_function(patient)  # Call the function and return its result

    print(f"No write-up function found for {history_item}.")
    return f"No write-up available for {history_item}.", 404