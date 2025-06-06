import datetime as dt

class Patient:
    def __init__(self, i1, i2, age, gender, admit_date, discharge_date=None, pmhx=None, famhx=None, sochx=None, hosp_meds=None, home_meds=None, vitals=None, exams=None, labs=None, micro=None, imaging=None, issues=None, history=None, **kwargs):
        self.i1 = i1
        self.i2 = i2
        self.age = age
        self.gender = gender
        self.admit_date = admit_date
        self.discharge_date = discharge_date
        self.pmhx = pmhx if pmhx is not None else {}  # Initialize as an empty dictionary if not provided
        self.famhx = famhx if famhx is not None else {}  # Initialize as an empty dictionary if not provided
        self.sochx = sochx if sochx is not None else {}
        self.vitals = vitals if vitals is not None else []
        self.exams = exams if exams is not None else []
        self.hosp_meds = hosp_meds if hosp_meds is not None else {}
        self.home_meds = home_meds if home_meds is not None else {}
        self.labs = labs if labs is not None else {}
        self.history = history if history is not None else {}
        self.micro = micro if micro is not None else {}
        self.imaging = imaging if imaging is not None else {}
        self.issues = issues if issues is not None else {}


    def __str__(self):
        return f"{self.i1}{self.i2} {self.age}{self.gender} | {self.admit_date[5:]}"

    def add_pmhx(self, category, item):
        self.pmhx[category].append(item)

    def add_issue(self, category, item):
        self.issues.setdefault(category, {}).update(item)
