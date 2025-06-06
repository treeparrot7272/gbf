from models.medication_classes import OrderSheetProcessor
from app.route_files.prestory import prestory_bp
from app.route_files.meds import meds_bp
from app.route_files.pmhx import pmhx_bp
from app.route_files.physical_exam import phys_bp
from models.lab_new import process_lab_text  # ensure you import process_lab_text
from models.patient_class import Patient
from flask import render_template, redirect, url_for, session, request, flash, request 
from app import app
import json  # To serialize and deserialize pt_list
import datetime as datetime  # For handling datetime objects
from collections import defaultdict  # For creating default dictionaries
import pyperclip

from app.logic import write_ups
from app.logic.issue_logic.confusion_iss_logic import confusion_initial, new_day_updater  # Import the confusion_initial function
from utils.imaging_keywords import get_suggestions

from utils.gb_ai import add_patient, save_data, load_data, get_pt_list, save_pt_list

app.register_blueprint(prestory_bp, url_prefix='/prestory')
app.register_blueprint(meds_bp, url_prefix='/meds')
app.register_blueprint(pmhx_bp, url_prefix='/pmhx')
app.register_blueprint(phys_bp, url_prefix='/phys')

# Set a secret key for the session
app.secret_key = 'mondofarts'  # Replace with a secure key



@app.route('/')
@app.route('/index')
def index():
    pt_list = get_pt_list()  # Retrieve the patient list from the session
    week = {'week_name': 'Y2'}

    # Separate admitted and discharged patients
    admitted_patients = []
    discharged_patients = []
    for i, pt in enumerate(pt_list):
        if pt.discharge_date:
            discharged_patients.append({'index': i, 'patient': pt})
        else:
            admitted_patients.append({'index': i, 'patient': pt})

    return render_template(
        'index.html',
        week=week,
        admitted_patients=admitted_patients,
        discharged_patients=discharged_patients
    )


@app.route('/add_pt')
def add_pt():
    return render_template('add_pt.html')

@app.route('/add_patient', methods=['POST'])
def handle_add_patient():
    pt_list = get_pt_list()  # Retrieve pt_list from the session
    pt_list = add_patient(pt_list)  # Add a new patient to the list
    save_pt_list(pt_list)  # Save the updated pt_list back to the session
    return redirect(url_for('index'))  # Redirect to the index page


#Patient Details pages
@app.route('/patient/<int:index>', methods=['GET', 'POST'])
def patient_details(index):
    """Display details for a specific patient."""
    pt_list = get_pt_list()  # Retrieve pt_list from the session
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404

    pt = pt_list[index]  # Get the patient by their index


    # Group medications by type
    grouped_meds = defaultdict(list)
    for med, details in pt.hosp_meds.items():
        med_type = details.get('type', 'Unknown')  # Use 'Unknown' as the default type
        grouped_meds[med_type].append({'name': med, **details})

    return render_template(
        'patient_details.html',
        pt=pt,
        index=index,
        grouped_meds=grouped_meds,
        write_ups=write_ups  # Pass the entire module
    )

@app.route('/update_hosp_meds/<int:index>', methods=['POST'])
def update_hosp_meds(index):
    """Update the hospital medications for a specific patient using clipboard data."""
    pt_list = get_pt_list()  # Retrieve pt_list from the session
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404

    try:
        # Process the clipboard data using OrderSheetProcessor
        processor = OrderSheetProcessor()
        hosp_meds, _, _ = processor.create_med_dictionary_from_orders()  # Extract the hospital medications
        
        # Update the patient's hospital medications
        patient = pt_list[index]
        patient.hosp_meds = hosp_meds

        save_pt_list(pt_list)  # Save the updated list back to the session
        return redirect(url_for('patient_details', index=index))  # Redirect to the patient's details page
    except Exception as e:
        return str(e), 500

#SAVE AND LOAD AND DELETE
@app.route('/save_list', methods=['GET', 'POST'])
def handle_save_list():
    pt_list = get_pt_list()  # Retrieve pt_list from the session
    save_data(pt_list)  # Save pt_list to a file
    flash("Patient list saved successfully.", "success")
    return redirect(request.referrer or url_for('index'))

@app.route('/load_list', methods=['GET', 'POST'])
def handle_load_list():
    data = load_data("Y1.json")  # Adjust the filename/path as needed
    session['pt_list'] = json.dumps(data)
    return redirect(url_for('index'))

@app.route('/delete_patient/<int:index>', methods=['POST'])
def delete_patient(index):
    """Delete a patient from the list by their index."""
    pt_list = get_pt_list()  # Retrieve pt_list from the session
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404
    pt_list.pop(index)  # Remove the patient at the specified index
    save_pt_list(pt_list)  # Save the updated list back to the session
    return redirect(url_for('index'))  # Redirect back to the index page

@app.route('/discharge_patient/<int:index>', methods=['POST'])
def discharge_patient(index):
    """Set the discharge date for a specific patient to the current date."""
    pt_list = get_pt_list()  # Retrieve the patient list from the session
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404

    # Update the discharge date
    patient = pt_list[index]
    patient.discharge_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Set to current date

    save_pt_list(pt_list)  # Save the updated list back to the session
    return redirect(url_for('index'))

@app.route('/update_patient_dates/<int:index>', methods=['POST'])
def update_patient_dates(index):
    """Update the admit and discharge dates for a specific patient."""
    pt_list = get_pt_list()  # Retrieve the patient list from the session
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404

    # Get the new dates from the form
    new_admit_date = request.form.get('admit_date')
    new_discharge_date = request.form.get('discharge_date')

    # Update the patient's dates
    patient = pt_list[index]
    patient.admit_date = new_admit_date
    patient.discharge_date = new_discharge_date

    save_pt_list(pt_list)  # Save the updated list back to the session
    return redirect(url_for('patient_details', index=index))



###Lab Logic
@app.route('/update_labs/<int:index>', methods=['POST'])
def update_labs(index):
    """Update patient.labs and patient.micro using the clipboard text processed by process_lab_text."""
    pt_list = get_pt_list()  # Retrieve the patient list from the session
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404

    patient = pt_list[index]

    # Get lab data from the clipboard
    lab_string = pyperclip.paste()
    # Process the lab text to get a dictionary of lab values and cultures
    processed_data = process_lab_text(lab_string)
    # Update the patient's labs and microbiology
    patient.labs = processed_data.get("labs", {})
    patient.micro = processed_data.get("cultures", [])
    patient.imaging = processed_data.get("imaging", {})

    save_pt_list(pt_list)  # Save the updated pt_list back to the session
    return redirect(url_for('patient_details', index=index))


#ISSUES
@app.route('/update_issues/<int:index>', methods=['POST'])
def update_issues(index):
    """Update a patient's issues list based on selected history items."""
    pt_list = get_pt_list()
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404
    
    patient = pt_list[index]
    
    # Get selected issues from form
    selected_issues = request.form.getlist('selected_issues')
    
    # Update patient's issues list
    issues_dictionary = {}
    for issue in selected_issues:
        issues_dictionary[issue] = {}  # Create an Issue object for each selected issue
    patient.issues = issues_dictionary
    
    # Save the updated patient list
    save_pt_list(pt_list)
    
    # Redirect back to the issues page
    flash('Patient issues updated successfully', 'success')
    return redirect(url_for('issues', index=index))

@app.route('/issues/<int:index>', methods=['GET'])
def issues(index):
    """Render the Issues page for the patient."""
    pt_list = get_pt_list()  # Retrieve the patient list
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]
    return render_template('issues.html', index=index, patient=patient)

@app.route('/issues_forms/<issue_name>/<int:index>')
def issue_form(issue_name, index):
    pt_list = get_pt_list()
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404
    patient = pt_list[index]
    template_name = f'issues_forms/{issue_name}_iss.html'

    return render_template(template_name, patient=patient, index=index)

@app.route('/issues_forms/confusion/<int:index>')
def confusion_iss(index):
    pt_list = get_pt_list()
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404
    patient = pt_list[index]
    cam_statement = confusion_initial(patient)
    testing_ground = new_day_updater(patient)
    save_pt_list(pt_list)  # Save the updated patient list
    return render_template(
        'issues_forms/confusion_iss.html',
        patient=patient,
        index=index,
        cam_statement=cam_statement,
        testing_ground=testing_ground
    )

@app.route('/add_confusion_entry/<int:index>', methods=['POST'])
def add_confusion_entry(index):
    pt_list = get_pt_list()
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404
    patient = pt_list[index]
    date_of_entry = request.form.get('date_of_entry')
    notes = request.form.get('notes')
    # You can add more fields as needed

    # Ensure the issues.confusion dictionary exists
    if "confusion" not in patient.issues:
        patient.issues["confusion"] = {}
    # Save the new entry
    patient.issues["confusion"][date_of_entry] = {
        "notes": notes,
        "days_since_onset": (datetime.datetime.strptime(date_of_entry, '%Y-%m-%d') - datetime.datetime.strptime(patient.history["confusion"]["confusion_onset_date"], '%Y-%m-%d')).days,
        # Add more fields as needed
    }
    save_pt_list(pt_list)
    flash("Confusion entry added.", "success")
    return redirect(request.referrer or url_for('confusion_iss', index=index))


##IMAGING
@app.route('/update_imaging_thoughts/<int:index>', methods=['POST'])
def update_imaging_thoughts(index):
    """Update the 'Thoughts' field for imaging studies."""
    pt_list = get_pt_list()  # Retrieve the patient list
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]

    # Iterate through the imaging studies and update the 'Thoughts' field
    for study_type, studies in patient.imaging.items():
        for i, study in enumerate(studies):
            field_name = f"thoughts_{study_type}_{i + 1}"
            if field_name in request.form:
                study["thoughts"] = request.form[field_name]

    save_pt_list(pt_list)  # Save the updated patient list
    flash("Imaging thoughts updated successfully.", "success")
    return redirect(url_for('patient_details', index=index))

@app.route('/imaging_thoughts/<int:index>', methods=['GET'])
def imaging_thoughts(index):
    """Render the Imaging Thoughts page for the patient."""
    pt_list = get_pt_list()  # Retrieve the patient list
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]

    # Add suggestions for each study
    for study_type, studies in patient.imaging.items():
        for study in studies:
            study["suggestions"] = get_suggestions(study["findings"])

    return render_template('imaging_thoughts.html', pt=patient, index=index)
