from flask import Blueprint, request, redirect, url_for, flash, render_template
from utils.gb_ai import get_pt_list, save_pt_list
import datetime

phys_bp = Blueprint('physical_exam', __name__)

@phys_bp.route('/phys/<int:index>', methods=['GET'])
def phys(index):
    """Render the Physical Exam page for the patient."""
    pt_list = get_pt_list()  # Retrieve the patient list
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]
    return render_template('phys.html', index=index, pt=patient)

@phys_bp.route('/save_exam/<int:index>', methods=['POST'])
def save_exam(index):
    """Save physical exam data to the patient's exams list."""
    pt_list = get_pt_list()  # Retrieve the patient list
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]

    # Get form data
    exam_date = request.form.get('exam_date')
    if exam_date:
        exam_date = exam_date.replace('T', ' ')  # Format datetime input
    else:
        # Default to current date/time if not provided
        exam_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Process CV exam data
    cv_sounds = request.form.getlist('cv_sounds')  # List of selected sounds (S1, S2, etc.)
    murmur = request.form.get('murmur', 'No Murmur')
    murmur_description = request.form.get('murmur_description', '') if murmur == 'Murmur Present' else ''

    cv_exam = {
        'sounds': cv_sounds,
        'murmur': murmur,
        'murmur_description': murmur_description
    }

    # Process Resp exam data
    air_entry = request.form.get('air_entry', 'Equal air entry')
    air_entry_description = request.form.get('air_entry_description', '') if air_entry == 'Abnormal' else ''
    crackles = request.form.get('crackles', 'No crackles')
    crackles_description = request.form.get('crackles_description', '') if crackles == 'Crackles present' else ''

    resp_exam = {
        'air_entry': air_entry,
        'air_entry_description': air_entry_description,
        'crackles': crackles,
        'crackles_description': crackles_description
    }

    # Process Abdominal exam data
    abd_exam = request.form.get('abd_exam', 'Soft and nontender')
    abd_description = request.form.get('abd_description', '') if abd_exam == 'Abnormal' else ''

    abdominal_exam = {
        'abd_exam': abd_exam,
        'abd_description': abd_description
    }

    # Create the exam entry
    exam_entry = {
        exam_date: {
            'cv': cv_exam,
            'resp': resp_exam,
            'abd': abdominal_exam
        }
    }

    # Ensure pt.exams exists
    if not hasattr(patient, 'exams') or patient.exams is None:
        patient.exams = []

        # Append the new exam entry
        patient.exams.append(exam_entry)

        # Save the updated patient list
        save_pt_list(pt_list)
        flash("Physical exam saved successfully.", "success")
        return redirect(url_for('patient_details', index=index))

    # Add the exam entry
    else:
        patient.exams.append(exam_entry)

        save_pt_list(pt_list)
        flash("Physical exam saved successfully.", "success")
        return redirect(url_for('patient_details', index=index))

@phys_bp.route('/save_vitals/<int:index>', methods=['POST'])
def save_vitals(index):
    """Save vital signs data to the patient's vitals list."""
    pt_list = get_pt_list()  # Retrieve the patient list
    if index < 0 or index >= len(pt_list):
        flash("Patient not found.", "error")
        return redirect(url_for('index'))

    patient = pt_list[index]

    # Get form data
    datetime_input = request.form.get('datetime')  # Rename variable to avoid conflict
    if datetime_input:
        datetime_input = datetime_input.replace('T', ' ')  # Remove the "T" from the datetime string
    else:
        # Default to current date/time if not provided
        datetime_input = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    o2modality = request.form.get('o2modality', 'Room Air')
    o2support = request.form.get('o2support', '') if o2modality != 'Room Air' else ''

    vitals_entry = {
        "temp": request.form.get('temp', ''),
        "bp": request.form.get('bp', ''),
        "hr": request.form.get('hr', ''),
        "rr": request.form.get('rr', ''),
        "o2sat": request.form.get('o2sat', ''),
        "o2modality": (o2modality, o2support)  # Save as a tuple
    }

    # Ensure pt.vitals exists
    if not hasattr(patient, 'vitals') or patient.vitals is None:
        patient.vitals = []

    # Append the new vitals entry
    patient.vitals.append({datetime_input: vitals_entry})

    # Save the updated patient list
    save_pt_list(pt_list)
    flash("Vital signs saved successfully.", "success")
    return redirect(url_for('patient_details', index=index))