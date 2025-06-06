import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gb')))

from models.patient_class import Patient

from app import app
