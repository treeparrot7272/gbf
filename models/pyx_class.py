import datetime as dt
from models.patient_class import Patient
import pprint as pp
import os
from utils.gb_ai import build_text_list

class PhysicalExam:
    def __init__(self, patient):
        self.patient = patient
        self.vitals = []
        self.exams = []

        self.exam_types = {

            "General": {
                "Cyanosis": "cy",
                "Pallor": "pa",
                "Jaundice": "ja",
                "Diaphoresis": "dia",
                "Anxious": "anx",
                "Lethargic": "let",
                "Confused": "con",
                "Agitated": "ag",
                "Unresponsive": "unr",
                "Uncomfortable": "uncom",
            },

            "Cardiovascular": {
                "Irregular Rhythm": "ir",
                "S1": "s1",
                "S2": "s2",
                "S3": "s3",
                "S4": "s4",
                "Murmur": "mu",
            },
            "Respiratory": {
                "Crackles": "cr",
                "Wheezes": "wh",
                "Decreased Breath Sounds": "dbs",
                "Accessory Muscle Use": "amu",
            },
            "Abdominal": {
                "Distended": "di",
                "Tender": "te",
                "Guarding": "gu",
                "Rebound": "re",
                "Mass": "ma",
                "Hepatomegaly": "he",
                "Splenomegaly": "sp",
                "Murphy's Sign": "mu",
                "McBurney's Point": "mc",
            },
            "Cranial Nerves": {
                "II": "ii",
                "III": "iii",
                "IV": "iv",
                "V": "v",
                "VI": "vi",
                "VII": "vii",
                "VIII": "viii",
                "IX": "ix",
                "X": "x",
                "XI": "xi",
                "XII": "xii",
            },
            "Motor": {
                "Strength": "st",
                "Tone": "to",
                "Tremor": "tr",
                "Involuntary Movements": "im",
            },
            "Sensory": {
                "Light Touch": "lt",
                "Pain": "pa",
                "Temperature": "te",
                "Vibration": "vi",
                "Position": "po",
            },
        }

    def exam_shorthand(self, exam_dictionary, working_dictionary):
        for key in exam_dictionary:
            print(key, exam_dictionary[key])
        shorthand_input = input("Enter the shorthand for the exam: ")
        shorthand_input_split = shorthand_input.split(";")
        for key, value in exam_dictionary.items():
            if value in shorthand_input_split:
                working_dictionary[key] = True
            else:
                working_dictionary[key] = False 
            os.system('clear')

    def add_vitals(self, sbp=None, dbp=None, hr=None, rr=None, temp=None, o2=(None, None), datetime=None):
        if not datetime:
            datetime = dt.datetime.now()
        if not sbp:
            sbp = int(input("Enter the systolic blood pressure: "))
        else:
            sbp = int(sbp)
        if not dbp:
            dbp = int(input("Enter the diastolic blood pressure: "))
        else:
            dbp = int(dbp)
        if not hr:
            hr = int(input("Enter the heart rate: "))
        else:
            hr = int(hr)
        if not rr:
            rr = int(input("Enter the respiratory rate: "))
        else:
            rr = int(rr)
        if not temp:
            temp = float(input("Enter the temperature: "))
        else:
            temp = float(temp)
        if not o2[0]:
            sat_and_type = input("Enter oxygen and type of oxygen delivery separated by a comma")
            sat_and_type_split = sat_and_type.split(',')
            sat = int(sat_and_type_split[0])
            type = sat_and_type_split[1]
            o2 = (sat, type)
        else:
            o2 = (int(o2[0]), o2[1])
        self.vitals.append((sbp, dbp, hr, rr, temp, o2, datetime))
        
    def add_exam(self, datetime=None):
        this_exam = {}
        if not datetime:
            datetime = dt.datetime.now()
        this_exam["datetime"] = datetime
        for exam_type in self.exam_types:
                print(exam_type)
                this_exam[exam_type] = {}
                self.exam_shorthand(self.exam_types[exam_type], this_exam[exam_type])
        self.exams.append(this_exam)

    def print_exam_details(self, exam):
        exam_of_interest = self.patient.vitals.exams[exam]
        text = ""
        if not exam_of_interest:
            print("No exam to print")
            return
        text += f"Exam Date:"
        text += self.vitals_text(-1) + "\n"
        text += self.general_exam_text(exam_of_interest) + "\n"
        text += self.cardiovascular_exam_text(exam_of_interest) + "\n"
        text += self.respiratory_exam_text(exam_of_interest) + "\n"
        text += self.abdominal_exam_text(exam_of_interest)

        return text

    def vitals_text(self, index=None):
        text = "\nVitals:\n"
        if not index:
            for vital in self.vitals:
                text += f"  {dt.datetime.strftime(vital[6], '%b %d')} -> BP: {vital[0]}/{vital[1]}, HR: {vital[2]}, RR: {vital[3]}, Temp: {vital[4]}, O2: {vital[5][0]}% {vital[5][1]}\n"
        else:
            vital = self.vitals[index]
            text += f"  {dt.datetime.strftime(vital[6], '%b %d')} -> BP: {vital[0]}/{vital[1]}, HR: {vital[2]}, RR: {vital[3]}, Temp: {vital[4]}, O2: {vital[5][0]}% {vital[5][1]}\n"
        return text
    
    
    def general_exam_text(self, exam):
        
        appearance = [appearance_attribute for appearance_attribute in exam["General"] if exam["General"][appearance_attribute] and appearance_attribute in ["Anxious", "Agitated", "Uncomfortable"]]
        
        mental_status = [mental_status_attribute for mental_status_attribute in exam["General"] if exam["General"][mental_status_attribute] and mental_status_attribute in ["Lethargic", "Confused", "Unresponsive"]]

        positive_findings = [finding for finding in exam["General"] if exam["General"][finding] if finding in ["Cyanosis", "Pallor", "Jaundice", "Diaphoresis"]]
        negative_findings = [finding for finding in exam["General"] if not exam["General"][finding] if finding in ["Cyanosis", "Pallor", "Jaundice", "Diaphoresis"]]
        
        text = ""
        text += f"On initial general appearance the patient is {build_text_list(appearance).lower() if build_text_list(appearance) else 'calm and comfortable'}."
        text += f" Mental status appears {build_text_list(mental_status).lower() if build_text_list(mental_status) else 'normal'}."
        if positive_findings:
            text += f" There is {build_text_list(positive_findings).lower()}."
        if negative_findings:
            text += f" Notably, there is no {build_text_list(negative_findings, 'nor').lower() if build_text_list(negative_findings) else ''}."

        return text

    def cardiovascular_exam_text(self, exam):
        text = ""
        
        #Heart Sounds
        heart_sounds = [heart_sound for heart_sound in exam["Cardiovascular"] if exam["Cardiovascular"][heart_sound] if heart_sound in ["S1", "S2", "S3", "S4"]]

        text += f"Heart sounds include {build_text_list(heart_sounds)}."

        #Murmur
        murmur = exam["Cardiovascular"]["Murmur"]
        if murmur:
            text += f" A murmur is appreciated "
            describe_murmur = input("Describe the murmur: ")
            text += f"and can be described as {describe_murmur}. "
        else:
            text += f" No murmur is appreciated. "

        #Rhythm
        rhythm = exam["Cardiovascular"]["Irregular Rhythm"]
        if rhythm:
            text += f"The rhythm is irregular. "
        else:
            text += f"The rhythm is regular. "

        return text

    def respiratory_exam_text(self, exam):
        text = ""
        
        #Breath Sounds
        decreased_breath_sounds = exam["Respiratory"]["Decreased Breath Sounds"]
        if decreased_breath_sounds:
            text += f"Breath sounds are decreased "
            where_decreased = input("Where are the decreased breath sounds: ")
            text += f"in {where_decreased}. "
        else:
            text += f"Breath sounds heard to both bases. "
        
        #Crackles
        crackles = exam["Respiratory"]["Crackles"]
        if crackles:
            text += f"Crackles are appreciated "
            where_crackles = input("Where are the crackles: ")
            crackle_description = input("Describe the crackles: ")
            text += f"in {where_crackles} and can be described as {crackle_description}. "
        else:
            text += f"No crackles appreciated. "

        #Wheezes
        wheezes = exam["Respiratory"]["Wheezes"]
        if wheezes:
            text += f"Wheeze is appreciated. "
        else:
            text += f"No wheeze appreciated on this exam. "

        #Accessory Muscle Use
        accessory_muscle_use = exam["Respiratory"]["Accessory Muscle Use"]
        if accessory_muscle_use:
            text += f"Accessory muscle use is noted. "
        else:
            text += f"No accessory muscle use. "

        return text

    def abdominal_exam_text(self, exam):
        text = ""

        negative_findings = []

        #Distention
        distention = exam["Abdominal"]["Distended"]
        if distention:
            text += f"The abdomen is distended. "
        else:
            negative_findings.append("Distention")

        #Tenderness
        tenderness = exam["Abdominal"]["Tender"]
        if tenderness:
            text += f"The abdomen is tender "
            where_tender = input("Where is the abdomen tender: ")
            text += f"in {where_tender}. "
        else:
            negative_findings.append("Tenderness")

        #Guarding
        guarding = exam["Abdominal"]["Guarding"]
        if guarding:
            text += f"The patient is guarding. "
        else:
            negative_findings.append("Guarding")

        #Rebound
        rebound = exam["Abdominal"]["Rebound"]
        if rebound:
            text += f"Rebound tenderness is present. "
        else:
            negative_findings.append("Rebound Tenderness")
        
        #Mass
        mass = exam["Abdominal"]["Mass"]
        if mass:
            text += f"A mass is palpated "
            where_mass = input("Where is the mass palpated: ")
            text += f"in {where_mass}. "
        else:
            negative_findings.append("Mass")

        #Hepatomegaly
        hepatomegaly = exam["Abdominal"]["Hepatomegaly"]
        if hepatomegaly:
            text += f"Hepatomegaly was palpated. "
        else:
            negative_findings.append("Hepatomegaly")
        
        #Splenomegaly
        splenomegaly = exam["Abdominal"]["Splenomegaly"]
        if splenomegaly:
            text += f"Splenomegaly was appreciated. "
        else:
            negative_findings.append("Splenomegaly")

        #Murphy's Sign
        murphys_sign = exam["Abdominal"]["Murphy's Sign"]
        if murphys_sign:
            text += f"Murphy's sign is appreciated. "
        else:
            negative_findings.append("Murphy's Sign")

        #McBurney's Point
        mcburneys_point = exam["Abdominal"]["McBurney's Point"]
        if mcburneys_point:
            text += f"McBurney's point tenderness is appreciated. "
        else:
            negative_findings.append("McBurney's Point")

        text += f"Notably, there is no {build_text_list(negative_findings, 'nor').lower() if build_text_list(negative_findings) else ''}.\n"
        
        return text

    def cranial_nerves_exam_text(self):
        pass

    def motor_exam_text(self):
        pass

    def sensory_exam_text(self):
        pass

class VitalSignAssessor:
    def __init__(self, patient):
        self.patient = patient
        self.vitals = self.patient.vitals.vitals

        self.abnormal_vitals = []
        
        for vital in self.vitals:
            date_specific = [vital[-1]]
            if vital[0] > 140:
                date_specific.append(f"Hypertension ({vital[0]})")
            if vital[1] > 130:
                date_specific.append(f"Diastolic Hypertension ({vital[1]})")
            if vital[2] > 100:
                date_specific.append(f"Tachycardia ({vital[2]})")
            if vital[2] < 55:
                date_specific.append(f"Bradycardia ({vital[2]})")
            if vital[3] > 24:
                date_specific.append(f"Tachypnea ({vital[3]})")
            if vital[4] < 36:
                date_specific.append(f"Hypothermia ({vital[4]})")
            if vital[4] > 38:
                date_specific.append(f"Fever ({vital[3]})")
            if vital[5] < 88:
                date_specific.append(f"Desaturation ({vital[4]})")
            if len(date_specific) > 1:
                self.abnormal_vitals.append(date_specific)


    def print_abnormal_vitals(self):
        print("The following abnormal vitals were noted:")
        for vital in self.abnormal_vitals:
            print(f"  On {dt.datetime.strftime(vital[0], '%b %d')} there was {build_text_list(vital[1:], 'and')}.")

    def get_specific_vital_abnormalities(self, abnomality_type):
        instances_of_target = []
        for abn in self.abnormal_vitals:
            for entry in abn[1:]:
                if abnomality_type in entry:
                    instances_of_target.append(abn[0])
        return instances_of_target

    
if __name__ == "__main__":
    patient = Patient("M", "M", 30, "M", "03-Dec-2024")
    pe = PhysicalExam(patient)
    pe.add_vitals(180, 70, 130, 20, 37.5, 98, dt.datetime.strptime("27-Dec-2024", "%d-%b-%Y"))
    pe.add_vitals(120, 80, 80, 12, 35, 85, dt.datetime.strptime("28-Dec-2024", "%d-%b-%Y"))
    assessment = VitalSignAssessor(pe)
