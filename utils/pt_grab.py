import re
from models.patient_class import Patient

class PtListGrab:
    def __init__(self, string):
        self.string = string

        self.split_string = string.split('\n')
        age_date_pattent = r'(\d\d)\w\s(\w)\s(\d{2}-\w{3}-\d{4})'
        self.pts_to_import = []

        for line in self.split_string:
            if re.match(age_date_pattent, line):
                self.pts_to_import.append(
                    {"age": re.match(age_date_pattent, line).group(1),
                    "gender": re.match(age_date_pattent, line).group(2),
                    "admit_date": re.match(age_date_pattent, line).group(3),
                    }
                )
            else:
                pass

        self.list_of_patient_classes = []
        start_num = 0
        for pt in self.pts_to_import:
            self.list_of_patient_classes.append(Patient("$", str(start_num), pt["age"], pt["gender"], pt["admit_date"]))
            start_num += 1



