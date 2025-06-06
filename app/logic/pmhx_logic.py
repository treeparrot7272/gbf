def handle_afib(patient, form_data):
    """Handle Atrial Fibrillation-specific PMHx logic."""
    afib_type = form_data.get('afib_type')
    rate_or_rhythm = form_data.get('rate_or_rhythm_control')
    anticoagulation = form_data.get('anticoagulation')
    chads_score = form_data.get('chads_score')
    patient.pmhx.setdefault('Atrial Fibrillation', {})
    patient.pmhx['Atrial Fibrillation'].update({
        'afib_type': afib_type,
        'rate_or_rhythm_control': rate_or_rhythm,
        'anticoagulation': anticoagulation,
        'chads_score': chads_score
    })

def handle_chf(patient, form_data):
    """Handle CHF-specific PMHx logic."""
    heart_failure = form_data.get('heart_failure')
    ef = form_data.get('ef')
    last_echo = form_data.get('last_echo')
    gdmt = form_data.getlist('gdmt')  # Use getlist for checkboxes
    other_findings = form_data.get('other_findings')
    patient.pmhx.setdefault('CHF', {})
    patient.pmhx['CHF'].update({
        'heart_failure': heart_failure,
        'ef': ef,
        'last_echo': last_echo,
        'gdmt': gdmt,
        'other_findings': other_findings
    })


def handle_copd(patient, form_data):
    """Handle COPD-specific PMHx logic."""
    respirologist = form_data.get('respirologist')
    baseline_mmrc = form_data.get('baseline_mmrc')
    home_o2 = form_data.get('home_o2')
    meds = form_data.get('meds')
    patient.pmhx.setdefault('COPD', {})
    patient.pmhx['COPD'].update({
        'respirologist': respirologist,
        'baseline_mmrc': baseline_mmrc,
        'home_o2': home_o2,
        'meds': meds
    })


def handle_cirrhosis(patient, form_data):
    """Handle Cirrhosis-specific PMHx logic."""
    etiology = form_data.get('etiology_cirrhosis')
    ascites = form_data.get('ascites')
    varices = form_data.get('varices')
    hcc_screening = form_data.get('hcc_screening')
    hepatologist = form_data.get('hepatologist')
    patient.pmhx.setdefault('Cirrhosis', {})
    patient.pmhx['Cirrhosis'].update({
        'etiology_cirrhosis': etiology,
        'ascites': ascites,
        'varices': varices,
        'hcc_screening': hcc_screening,
        'hepatologist': hepatologist
    })

def handle_diabetes(patient, form_data):
    """Handle Diabetes-specific PMHx logic."""
    diabetes_type = form_data.get('diabetes_type')
    last_a1c = form_data.get('last_a1c')
    endocrinologist = form_data.get('endocrinologist')
    complications = form_data.getlist('complications')
    diabetes_meds = form_data.get('diabetes_meds')
    patient.pmhx.setdefault('Diabetes', {})
    patient.pmhx['Diabetes'].update({
        'diabetes_type': diabetes_type,
        'last_a1c': last_a1c,
        'endocrinologist': endocrinologist,
        'complications': complications,
        'diabetes_meds': diabetes_meds
    })

def handle_hypertension(patient, form_data):
    """Handle Hypertension-specific PMHx logic."""
    agents = form_data.getlist('agents')
    patient.pmhx.setdefault('Hypertension', {})
    patient.pmhx['Hypertension'].update({
        'agents': agents
    })

def handle_ckd(patient, form_data):
    baseline = form_data.get('baseline_creatinine')
    etiology = form_data.get('ckd_etiology')
    stage = form_data.get('ckd_stage')
    dialysis = form_data.get('dialysis')
    nephrologist = form_data.get('nephrologist')
    print(f"Ckd etiology: {etiology}")
    patient.pmhx.setdefault('CKD', {})
    patient.pmhx['CKD'].update({
        'baseline': baseline,
        'etiology': etiology,
        'stage': stage,
        'dialysis': dialysis,
        'nephrologist': nephrologist
    })


def handle_prior_surgeries(patient, form_data):
    """Handle Prior Surgeries-specific PMHx logic."""
    surgeries = form_data.getlist('surgeries')  # Get all selected surgeries
    patient.pmhx.setdefault('Prior Surgeries', []).extend(surgeries)


# Add more handlers for other conditions as needed...

CONDITION_HANDLERS = {
    'Atrial Fibrillation': handle_afib,
    'CHF': handle_chf,
    'COPD': handle_copd,
    'Cirrhosis': handle_cirrhosis,
    'Diabetes': handle_diabetes,
    'Hypertension': handle_hypertension,
    'Prior Surgeries': handle_prior_surgeries,
    'CKD': handle_ckd,
    # Add more conditions here...
}