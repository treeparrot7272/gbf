import random

def rann(gender="m"):
    male_names = ["Mario", "Luigi", "Wario", "Link"]
    female_names = ["Peach", "Daisy", "Rosalina", "Zelda"]
    index = random.randint(0, 2)

    if gender == "m":
        return male_names[index]
    elif gender == "f":
        return female_names[index]
    
def pnons(type, gender):
    """
    Returns the appropriate pronoun based on the type and gender provided.

    Args:
        type (str): The type of pronoun. 
                    's' for subject pronoun (he/she),
                    'p' for possessive pronoun (his/her),
                    'o' for object pronoun (him/her).
        gender (str): The gender for the pronoun.
                    'm' for male,
                    'f' for female.
    Returns:
    str: The corresponding pronoun based on the type and gender.
    """

    if gender == "m":
        if type == "s":
            return "he"
        elif type == "o":
            return "him"
        elif type == "p":
            return "his"
    elif gender == "f":
        if type == "s":
            return "she"
        elif type == "o" or type == "p":
            return "her"



relations_dict = {
    "hu": ["husband", "m"],
    "wi": ["wife", "f"],
    "dt": ["daughter", "f"],
    "so": ["son", "m"],
    "pa": ["partner", "m"]
}

def fnr():
    fnr_string = ""
    fnr_input = input("Friends and relations>> ")
    fnr_list = fnr_input.split(",")
    if fnr_list[0].lower() == "n":
        return ""
    fnr_list = fnr_list[1:]
    fnr_string += f" as well as {pnons('p','f')} "

    for key, rel_list in relations_dict.items():
        if key in fnr_list:
            fnr_string += f'{rel_list[0]} ({rann(rel_list[1])}) and '
    fnr_string = fnr_string.strip(' and ')

    return fnr_string


def goc_note(patient_name=""):
    if not patient_name:
        patient_name = rann('f')
    friends_and_relations = fnr()
    return patient_name, friends_and_relations

    
if __name__ == "__main__":
    patient_name, family_stuff = goc_note()
    goc_string = f"""
Spoke with {patient_name}{family_stuff}. We discussed {pnons('p','f')} hospital stay thus far and what the treatment plans has been. Unfortunately, despite our best efforts . As such, code status has been changed and relevant orders added/discontinued."""
    print(goc_string)

