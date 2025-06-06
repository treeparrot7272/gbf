from flask import Blueprint, request, redirect, url_for, flash, render_template
from utils.gb_ai import get_pt_list, save_pt_list
from app.logic.pmhx_logic import CONDITION_HANDLERS

pmhx_bp = Blueprint('pmhx', __name__)

@pmhx_bp.route('/pmhx/<int:index>', methods=['GET', 'POST'])
def pmhx(index):
    """Render the PMHx form and handle adding multiple conditions to a patient's PMHx."""
    pt_list = get_pt_list()  # Retrieve the patient list from the session
    if index < 0 or index >= len(pt_list):
        return f"Patient at index {index} not found.", 404

    patient = pt_list[index]  # Get the correct patient
    patient_pmhx = getattr(patient, 'pmhx', {})  # Get the patient's PMHx
    patient_pmhx = patient_pmhx.keys() if isinstance(patient_pmhx, dict) else patient_pmhx  # Ensure it's a list

    if request.method == 'POST':
        # Get all selected conditions from the form
        selected_conditions = request.form.getlist('condition')  # Get all selected conditions as a list

        # Iterate through each selected condition and handle it
        for condition in selected_conditions:
            if condition in CONDITION_HANDLERS:
                # Call the appropriate handler function for the condition
                CONDITION_HANDLERS[condition](patient, request.form)
            else:
                flash(f"Condition '{condition}' is not supported.", "error")

        # Save the updated patient list back to the session
        save_pt_list(pt_list)
        flash("PMHx updated successfully.", "success")
        return redirect(url_for('patient_details', index=index))

    # Define the condition_forms dictionary for rendering forms dynamically
    condition_forms = {
        "Atrial Fibrillation": {"id": "Atrial Fibrillation", "heading": "Atrial Fibrillation", "template": "pmhx_items/afib.html"},
        "Alcohol Use Disorder": {"id": "Alcohol Use Disorder", "heading": "Alcohol Use Disorder", "template": "pmhx_items/alcohol.html"},
        "CHF": {"id": "CHF", "heading": "CHF", "template": "pmhx_items/chf.html"},
        "CKD": {"id": "CKD", "heading": "Chronic Kidney Disease", "template": "pmhx_items/ckd.html"},
        "Cirrhosis": {"id": "Cirrhosis", "heading": "Cirrhosis", "template": "pmhx_items/cirrhosis.html"},
        "COPD": {"id": "COPD", "heading": "COPD", "template": "pmhx_items/copd.html"},
        "Coronary Artery Disease": {"id": "Coronary Artery Disease", "heading": "Coronary Artery Disease", "template": "pmhx_items/cad.html"},
        "Diabetes": {"id": "Diabetes", "heading": "Diabetes", "template": "pmhx_items/diabetes.html"},
        "Dyslipidemia": {"id": "Dyslipidemia", "heading": "Dyslipidemia", "template": "pmhx_items/dyslipidemia.html"},
        "Hypertension": {"id": "Hypertension", "heading": "Hypertension", "template": "pmhx_items/hypertension.html"},
        "Stroke": {"id": "Stroke", "heading": "Stroke", "template": "pmhx_items/stroke.html"},
        "Prior Surgeries": {"id": "Prior Surgeries", "heading": "Prior Surgeries", "template": "pmhx_items/prior_surgeries.html"},
    }

    # Render the template with the condition_forms dictionary
    return render_template('pmhx.html', index=index, patient=patient, condition_forms=condition_forms, patient_pmhx=patient_pmhx)