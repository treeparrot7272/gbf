from flask import Blueprint, request, redirect, url_for, flash, render_template

from utils.gb_ai import get_pt_list, save_pt_list
# Define the blueprint
meds_bp = Blueprint('meds', __name__)

@meds_bp.route('/add_med/<int:index>', methods=['POST'])
def add_med(index):
    pt_list = get_pt_list()
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]

    # Get form data
    med_name = request.form.get('med_name')
    if not med_name:
        flash("Medication name is required.", "error")
        return redirect(url_for('meds.edit_hosp_meds', index=index))

    # Add the new medication to hosp_meds
    patient.hosp_meds[med_name] = {
        "type": request.form.get('type', ''),
        "dose": request.form.get('dose', ''),
        "units": request.form.get('units', ''),
        "Formulation": request.form.get('Formulation', ''),
        "frequency": request.form.get('frequency', ''),
        "PRN": request.form.get('PRN') == 'on',
        "stop_date": request.form.get('stop_date', ''),
        "A/S/D": request.form.get('A/S/D', 'Active')
    }

    # Save the updated patient list
    save_pt_list(pt_list)
    flash(f"Medication '{med_name}' added successfully.", "success")
    return redirect(url_for('meds.edit_hosp_meds', index=index))

@meds_bp.route('/edit_hosp_meds/<int:index>', methods=['GET', 'POST'])
def edit_hosp_meds(index):
    pt_list = get_pt_list()
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]

    if request.method == 'POST':
        # Update hosp_meds with the submitted form data
        updated_meds = {}
        for key, value in request.form.items():
            if key.startswith("med_"):  # Medication fields are prefixed with "med_"
                new_key = key.replace("med_", "")  # Remove the prefix
                med_name, field = new_key.split("_", 1)
                if med_name not in updated_meds:
                    updated_meds[med_name] = {}
                updated_meds[med_name][field] = value

        # Save the updated medications back to the patient
        patient.hosp_meds = updated_meds
        save_pt_list(pt_list)
        flash("Hospital medications updated successfully.", "success")
        return redirect(url_for('patient_details', index=index))

    return render_template('edit_hosp_meds.html', patient=patient, index=index)

@meds_bp.route('/edit_home_meds/<int:index>', methods=['GET', 'POST'])
def edit_home_meds(index):
    """Render the Edit Home Medications page and handle form submission."""
    pt_list = get_pt_list()  # Retrieve the patient list
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]

    if request.method == 'POST':
        # Clear the existing home_meds dictionary
        patient['home_meds'] = {}

        # Iterate through the submitted form data to populate home_meds
        for key, value in request.form.items():
            if key.startswith('med_name_'):
                med_id = key.split('_')[-1]  # Extract the medication ID
                med_name = value
                med_dose = request.form.get(f'med_dose_{med_id}', '')
                med_route = request.form.get(f'med_route_{med_id}', '')
                med_frequency = request.form.get(f'med_frequency_{med_id}', '')

                # Add the medication to the home_meds dictionary
                patient['home_meds'][med_name] = {
                    'dose': med_dose,
                    'route': med_route,
                    'frequency': med_frequency
                }

        # Save the updated patient list
        save_pt_list(pt_list)
        flash("Home medications updated successfully.", "success")
        return redirect(url_for('patient_details', index=index))

    return render_template('edit_home_meds.html', index=index)

@meds_bp.route('/update_home_meds/<int:index>', methods=['POST'])
def update_home_meds(index):
    """Update the home medications for the patient."""
    pt_list = get_pt_list()  # Load the patient list
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]

    # Clear the existing home_meds dictionary
    updated_home_meds = {}

    # Iterate through the submitted form data to populate home_meds
    for key, value in request.form.items():
        if key.startswith('med_name_'):
            med_id = key.split('_')[-1]  # Extract the medication ID
            med_name = value
            med_dose = request.form.get(f'med_dose_{med_id}', '')
            med_route = request.form.get(f'med_route_{med_id}', '')
            med_frequency = request.form.get(f'med_frequency_{med_id}', '')

            # Add the medication to the home_meds dictionary
            updated_home_meds[med_name] = {
                'dose': med_dose,
                'route': med_route,
                'frequency': med_frequency
            }

    patient.home_meds = updated_home_meds  # Update the patient's home medications
    # Save the updated patient list
    save_pt_list(pt_list)
    flash("Home medications updated successfully.", "success")
    return redirect(url_for('patient_details', index=index))
