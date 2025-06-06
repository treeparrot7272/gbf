import pyperclip, re
import datetime
import difflib
import json, pprint


STANDARDIZED_MED_NAMES_PATH = '/Users/matthewmittelstadt/Desktop/code/gb/standardized_med_names.json'
MEDICATION_TYPES_PATH = '/Users/matthewmittelstadt/Desktop/code/gb/medication_types.json'  # Path to the medication types JSON file

class OrderSheetProcessor:
    def __init__(self):
        self.dictionary_of_findings = {
            "ACP": "",
            "request_date": "",
        }
        self.medication_types = self.load_medication_types()  # Load the medication types from JSON
        self.load_standardized_med_names()  # Load the standardized medication names

        self.find_and_build = ["Goals of Care"]
        self.med_deletables = ["Medications, Alert", "All orders for this chart", "SBGH", "Page:", "By Department Ex", "Req", "St. Boniface", "Auto Compl"]
        self.keywords_for_new_med = ["Routine Ac", "Routine Pe", " STAT ", "Cancelled", " Stop Date Reached ", "Discontinued", "Active", "Completed"]

        self.hosp_med_dict = {}
        self.home_med_dict = {}
        self.iv_fluids = {}

   #SAVE/LOAD JSON FUNCTIONS
    def load_standardized_med_names(self):
        global standardized_med_names
        try:
            with open(STANDARDIZED_MED_NAMES_PATH, 'r') as f:
                standardized_med_names = json.load(f)
        except FileNotFoundError:
            standardized_med_names = {}

    def save_standardized_med_names(self):
        global standardized_med_names
        try:
            with open(STANDARDIZED_MED_NAMES_PATH, 'r') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = {}

        # Update the existing data with the new entries
        existing_data.update(standardized_med_names)

        with open(STANDARDIZED_MED_NAMES_PATH, 'w') as f:
            json.dump(existing_data, f, indent=4)

    def load_medication_types(self):
        try:
            with open(MEDICATION_TYPES_PATH, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_medication_types(self):
        try:
            with open(MEDICATION_TYPES_PATH, 'w') as f:
                json.dump(self.medication_types, f, indent=4)
        except Exception as e:
            print(f"Error saving medication types: {e}")

    #HOSPITAL MED FUNCTIONS
    def create_med_dictionary_from_orders(self): 
        """Creates a dictionary of medications from the orders in the clipboard text.

        This method processes the text from the clipboard to extract and organize
        medication information into a dictionary. It performs the following steps:
        1. Isolates the relevant text chunks by removing unnecessary parts.
        2. Extracts the request date and general patient details.
        3. Isolates medication and IV therapy information.
        4. Cleans up the medication text by removing deletable items.
        5. Builds a dictionary of medications line by line.

        Returns:
            None: The resulting dictionary is stored in the instance variable `self.hosp_med_dict`.

        Raises:
            AttributeError: If there is no text in the clipboard.
            IndexError: If the patient is not on IV fluids.
        """

        try:
            #gets rid of labs and beyond, returns remaining as a string
            split_up_string = self.isolate_text_chunks(pyperclip.paste(), 'Medication', 'IV Therapy', 'Blood Product','Laboratory Alert Date')
            relevant_orders = split_up_string[1:-1] #ignores patient infor from first part and lab orders from last part
            
        except AttributeError:
            print("No text in clipboard.")
            return

        #MEDICATIONS
        string_of_meds = relevant_orders[0]

        string_of_meds = self.delete_things(string_of_meds, self.med_deletables) #deletes the unnecessary lines

        med_dict = self.line_by_line_dict_builder(string_of_meds) #builds the dictionary of medications

        #IV AND BLOOD PRODUCTS
        if len(relevant_orders) > 1:
            string_of_iv = relevant_orders[1]
            iv_dict = self.iv_fluid_builder(string_of_iv)
        else:
            iv_dict = {}
        if len(relevant_orders) > 2:
            string_of_blood = relevant_orders[2]
            blood_dict = self.blood_product_builder(string_of_blood)
        else:
            blood_dict = {}

        return med_dict, iv_dict, blood_dict
    
    def blood_product_builder(self, string):
        """
        Builds a dictionary of blood products from the input text.

        :param string: The input text containing blood product information.
        :returns: A dictionary of blood products.
        """
        blood_dict = {}
        list_of_blood_products = string.split("\n")
        target_based_text = ""

        for line in list_of_blood_products:
            if any(keyword in line for keyword in self.keywords_for_new_med) and "CBS" not in line:
                target_based_text += '$$$' + line
            else:
                target_based_text += '\n' + line

        target_based_text = target_based_text.split("$$$")
        target_based_text = target_based_text[1:]
        
        for section in target_based_text:
            sub_target_text = section.split("\n")
            type_of_product, date = self.get_name_and_date(sub_target_text[0])
            split_the_line = sub_target_text[1].split(" ")
            if "Giv" in split_the_line[0]:
                amount = split_the_line[1]
            else:
                amount = split_the_line[0]
            if blood_dict.get(type_of_product, '') == '':
                blood_dict[type_of_product] = {}
            if blood_dict[type_of_product].get(date, '') == '':
                if amount == 'Prothrombin':
                    amount = 1
                else:
                    blood_dict[type_of_product][date] = int(amount)
            else:
                blood_dict[type_of_product][date] = blood_dict[type_of_product][date] + int(amount) 

        return blood_dict
    
    def iv_fluid_builder(self, string):
        """
        Builds a dictionary of IV fluids from the input text.

        :param string: The input text containing IV fluid information.
        :returns: A dictionary of IV fluids.
        """
        iv_dict = {}
        list_of_iv_fluids = string.split("\n")
        target_based_text = ""

        for line in list_of_iv_fluids:
            if any(keyword in line for keyword in self.keywords_for_new_med):
                target_based_text += '$' + line
            else:
                target_based_text += '\n' + line
        
        target_based_text = target_based_text.split("$")
        target_based_text = target_based_text[1:]
        try:
            for section in target_based_text:
                sub_target_text = section.split("\n")
                name, date = self.get_name_and_date(sub_target_text[0])
                amount = sub_target_text[1].split(" ")[0]
                if "%" in sub_target_text[1]: #because KCL has a % in it on the second line, whereas the rest don't have this
                    units = sub_target_text[2].split(" ")[1]
                else:
                    units = sub_target_text[1].split(" ")[1]
                if iv_dict.get(name, '') == '':
                    iv_dict[name] = {}
                if iv_dict[name].get(date, '') == '':
                    iv_dict[name][date] = {
                        "amount": amount.replace(',', ''),
                        "units": units,
                    }
                else:
                    iv_dict[name][date]["amount"] = int(iv_dict[name][date]["amount"]) + int(amount.replace(',', ''))

            return iv_dict
        except:
            print("Error with IV fluids")
            return iv_dict

        

    #UTILITIES FOR HOSPITAL MEDS
    def isolate_text_chunks(self, text: str, *args, count=1) -> list:
        """
        Takes a text, and will split it at specific key words listed in args and returns a list of each of the splits

        :param: text | any text that you want to split up
        :param: count | amount of times to do the replacement for each, defaults to 1
        :returns: list | created in order of how splits were made
        """
        for items in args:
            text = text.replace(items, "$" + items, count)
        list_of_breaks = text.split("$")
        return list_of_breaks

    def find_request_date(self, string: str) -> str:
        """
        Takes the text from an order sheet, and specifically finds the string of the date and time that the order sheet was accessed

        :param: string The clipboard string taken from order sheet

        :returns: str | gets date and time as DD-MMM-YYYY HH:MM


        """
        list_of_string = string.split("\n") #turns string into list so you can go line by line
        for item in list_of_string:
            if "Requested By: Mittelstadt, Matthew (MD)" in item:
                return list_of_string[list_of_string.index(item) + 1][:17] # gets date and time DD-MMM-YYYY HH:MM

    def delete_things(self, string, delete_list):

        list_by_lines = string.split("\n") #turns string into list, one line each
        new_list = [item for item in list_by_lines if not any(word in item for word in delete_list)] #adds to new list if not in deletables

        string_of_list = ("\n").join(new_list) #turns new list into string

        reg_bd_mrn_patt = r'\d{2}-\w{3}-\d{4}\s\d+\s\/\s\d+' #take out the BD MRN number
        if re.search(reg_bd_mrn_patt, string_of_list):
            text_pattern = re.search(reg_bd_mrn_patt, string_of_list).group()

            string_of_list = string_of_list.replace(text_pattern, "")


        return string_of_list

    def get_acp_status(self, string):
        list_of_hits = []
        list_of_string = string.split("\n")
        for item in list_of_string:
            if "Goals of Care" in item:
                list_of_hits.append(list_of_string.index(item))
        if len(list_of_hits) == 2: #in case there are multiple orders, just get the latest (closest from the top)
            list_of_acp_order = list_of_string[list_of_hits[-1]].split(" ")
            self.dictionary_of_findings["ACP"] = list_of_acp_order[0]

    def get_name_and_date(self, string):        
        test_string = string #get the text
        test_pattern = r"(.+?)\s+(\d{2}-\w{3}-\d{4})" #pattern to look for

        match_find = re.match(test_pattern, test_string) #creates a match object

        if match_find:
            return match_find.group(1), match_find.group(2) #returns the name and date

    def get_stop_date(self, string):
        string_to_assess = string
        test_pattern = r'\d{2}-\w{3}-\d{4}\s\d{2}:\d{2}'

        match_find = re.search(test_pattern, string_to_assess)

        if match_find:
            return match_find.group()

    def get_med_line_info(self, line, dictionary):
        """
        This function takes a line from the order sheet and returns the medication name, start date, stop date, status.

        Will also handle if this is a new entry of a previously recognized name in which it will do the _# suffix

        sets current med for the next part of the build
        """
        try:
            name, date = self.get_name_and_date(line)
            name = name.lower().strip()
            if "inj" in name:
                name = name.replace("inj", "").strip()
            if "ec" in name:
                name = name.replace(" ec", "").strip()
            if "inh" in name:
                name = name.replace("inh ", "").strip()
            
            # Find the medication type
            medication_type = "Unknown"
            for med_class, meds in self.medication_types.items():
                if any(med in name for med in meds):
                    if "-" in med_class:
                        split_class = med_class.split("-", 1)
                        medication_type = split_class[0].strip()
                    else:
                        medication_type = med_class
                    break
            
            if medication_type == "Unknown":
                standardized_name = input(f"Enter medication type for '{name}': ")
                if standardized_name == "":
                    self.medication_types["Unknown"].append(name)
                else:
                    if standardized_name not in self.medication_types:
                        self.medication_types[standardized_name] = []
                    self.medication_types[standardized_name].append(name)
                self.save_medication_types()  # Save the updated medication types

            if name not in dictionary.keys():  # name never seen before
                dictionary[name] = {
                    "start_date": "",
                    "stop_date": "",
                    "A/S/D": "",
                    "Formulation": "",
                    "dose": "",
                    "units": "",
                    "frequency": "",
                    "PRN": False,
                    "count": 1,
                    "type": medication_type  # Add the medication type
                }
                dictionary[name]["start_date"] = date

            else:  # name seen before, add _# to the name
                dictionary[name]["count"] += 1
                name = name + f"_{dictionary[name]['count']}"
                dictionary[name] = {
                    "start_date": "",
                    "stop_date": "",
                    "A/S/D": "",
                    "Formulation": "",
                    "dose": "",
                    "units": "",
                    "frequency": "",
                    "PRN": False,
                    "type": medication_type  # Add the medication type
                }
                dictionary[name]["start_date"] = date

            return name
        except Exception as e:
            print(f"Error in get_med_line_info for {line}: {e}")

    def filter_medications_by_type(self, dictionary, med_type):
        """
        Filters the medications by their type.

        :param dictionary: The dictionary containing medication information.
        :param med_type: The type of medication to filter by.
        :returns: A dictionary of medications filtered by the specified type.
        """
        filtered_meds = {name: details for name, details in dictionary.items() if details.get("type") == med_type}
        return filtered_meds

    def asd_and_stop_date(self, line, dictionary, name):
        if "Stop Date Reached" in line: # this part is to get the stop date
                try:
                    stop_date = self.get_stop_date(line)
                    dictionary[name]["stop_date"] = stop_date
                    dictionary[name]["A/S/D"] = "Stop Date Reached"
                except KeyError: 
                    print(f'Could not get stop date for {line}')

                    
        elif "Discontinued" in line:
            stop_date = self.get_stop_date(line)
            try:
                dictionary[name]["stop_date"] = stop_date
                dictionary[name]["A/S/D"] = "Discontinued"
            except:
                print(f'Could not get stop date for {line}')
        elif "Active" in line:
            try:
                dictionary[name]["A/S/D"] = "Active"
            except KeyError:
                print(f'Could not get status for {line}')
        elif "Cancelled" in line:
            dictionary[name]["A/S/D"] = "Cancelled"

    def update_form_prn_freq(self, line, dictionary, current):
        #Formulation
        if "IntraVenous" in line:
            dictionary[current]["Formulation"] = "IV"
        if "By Mouth" in line:
            dictionary[current]["Formulation"] = "PO"
        if "Puff(s)" in line:
            dictionary[current]["Formulation"] = "INH"
        if "SubCutaneous" in line:
            dictionary[current]["Formulation"] = "SC"

        #PRN
        if "PRN" in line:
            dictionary[current]["PRN"] = True

        #frequency
        if "ONCE" in line:
            dictionary[current]["frequency"] = "x1"
        if "Every " in line:
            try:
                dictionary[current]["frequency"] = line[line.index("Q"):line.index("H") + 1]
            except: 
                pass
        if "Daily" in line:
            dictionary[current]["frequency"] = "daily"
        if "BID" in line:
            dictionary[current]["frequency"] = "BID"
        if "TID" in line:
            dictionary[current]["frequency"] = "TID"
        if "QID" in line:
            dictionary[current]["frequency"] = "QID"
        if "Every Hemodialysis" in line:
            dictionary[current]["frequency"] = "qHD"

        #Breakfast and Supper
        if "Supper" in line or "Breakfast" in line:
            count = 0
            if "Supper" in line:
                count += 1
            if "Breakfast" in line:
                count += 1
            if count == 2:
                dictionary[current]["frequency"] = "BID"
            elif count == 1:
                dictionary[current]["frequency"] = "daily"     

    def line_by_line_dict_builder(self, string):

        dictionary_of_medications = {}

        list_of_meds = string.split("\n")
        current_med = ""

        for line in list_of_meds:
            if any(keyword in line for keyword in self.keywords_for_new_med) and "via" not in line and "Auto Completed" not in line:   #med name line
                name = self.get_med_line_info(line, dictionary_of_medications)
                self.asd_and_stop_date(line, dictionary_of_medications, name)
                current_med = name #initiates name for the next part of the build

            else: # not the a new name of a medication
                try: #dose and units
                    int(line[0])
                    string_split = line.split(" ")
                    if string_split[1] == "to":
                        dictionary_of_medications[current_med]["dose"] = string_split[0] + " to " + string_split[2]
                        dictionary_of_medications[current_med]["units"] = string_split[3]
                    else:
                        dictionary_of_medications[current_med]["dose"] = string_split[0]
                        dictionary_of_medications[current_med]["units"] = string_split[1]
                except:
                    continue

                self.update_form_prn_freq(line, dictionary_of_medications, current_med)


        return dictionary_of_medications

    def are_similar(self, name1, name2, threshold=0.8):
        """
        Determines if two medication names are similar based on a similarity threshold.

        :param: name1 | first medication name
        :param: name2 | second medication name
        :param: threshold | similarity threshold (default is 0.8)
        :returns: bool | True if names are similar, False otherwise
        """
        similarity = difflib.SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
        return similarity >= threshold


    #HOME MED FUNCTIONS#############
    def extract_drug_info(self, text_block):
        """
        Extracts drug information from a text block.
        """
        date_pattern = r'\d{2}-\w{3}-\d{4}'
        drug_name_pattern = r'{(.+?)(\(.+\))?\s?\[(.+?)\]'
        day_number_pattern = r'}.+?(\d)+\s'
        pill_number_pattern = r'(\d\d?\d?)\sDrug\sProgram'
        
        date_match = re.search(date_pattern, text_block)
        drug_name_match = re.search(drug_name_pattern, text_block, re.DOTALL)
        number_of_days_match = re.search(day_number_pattern, text_block, re.DOTALL)
        pill_number_match = re.search(pill_number_pattern, text_block, re.DOTALL)
        
        if date_match and drug_name_match:
            date = date_match.group(0)
            drug_name_with_breaks = drug_name_match.group(1)
            dose = drug_name_match.group(3).replace("\n", " ").strip()
            drug_name_without_breaks = drug_name_with_breaks.replace("\n", " ").strip()

            # Standardize the medication name
            standardized_name = standardized_med_names.get(drug_name_without_breaks)
            if not standardized_name:
                standardized_name = input(f"Enter standardized name for '{drug_name_without_breaks}': ")
                if standardized_name == "":
                    standardized_med_names[drug_name_without_breaks] = drug_name_without_breaks.lower()
                else:    
                    standardized_med_names[drug_name_without_breaks] = standardized_name
                self.save_standardized_med_names()  # Save the updated dictionary

            dose = dose.split(" ")  

            number_tester = number_of_days_match.group(0).replace("}", "").strip()
            pill_number = pill_number_match.group(0).replace(" Drug Program", "").strip()
            
            pills_per_day = int(pill_number) / float(number_tester)
            
            return standardized_name, {'date': date, 'dose': dose[0], 'units': dose[1] if len(dose) > 1 else "", 'days': number_tester, 'pills': pill_number, 'pills_per_day': pills_per_day}
        else:
            return None, None

    def home_med_dictionary_builder(self, dictionary_to_modify):
        """
        Builds a dictionary of home medications from input text.
        """
        pause = input("Click enter when on clipboard>>>")
        input_text = pyperclip.paste()

        insert_the_symbol = input_text.replace("Network", "Network$")
        text_block = insert_the_symbol.split("$")

        for block in text_block:
            drug_name, info = self.extract_drug_info(block)

            if drug_name and info:
                drug_name_lower = drug_name.lower()

                if drug_name_lower in dictionary_to_modify:
                    existing_date = dictionary_to_modify[drug_name_lower]['date']
                    current_date = info['date']

                    if datetime.datetime.strptime(current_date, '%d-%b-%Y') > datetime.datetime.strptime(existing_date, '%d-%b-%Y'):
                        dictionary_to_modify[drug_name_lower] = info
                else:
                    dictionary_to_modify[drug_name.lower()] = info

        return dictionary_to_modify


    #PRINT FUNCTIONS
    def print_out_home_meds(self, dictionary_to_print):
        sorted_meds = sorted(
            dictionary_to_print.items(),
            key=lambda item: datetime.datetime.strptime(item[1]['date'], '%d-%b-%Y'),
            reverse=True
        )
        for med_name, values in sorted_meds:
            last_prescribed = values['date']
            print(f"{med_name} {values['dose']} {values['units'].lower()} ({last_prescribed[:6]})")

    def print_out_hosp_meds(self, dictionary_to_print, include_prn=False, include_inactive=False):
        med_dates = {}
        for med_name, values in dictionary_to_print.items():
            if (not include_prn and values["PRN"]) or (not include_inactive and values["A/S/D"] != "Active"):
                continue

            base_name = med_name.split('_')[0] #if multiple orders

            #handle start date
            dt_start = datetime.datetime.strptime(values["start_date"], "%d-%b-%Y")
            formatted_start_date = datetime.datetime.strftime(dt_start, "%b-%d")
            
            #if stop date, create date_range variable
            if values["stop_date"]:
                dt_stop = datetime.datetime.strptime(values["stop_date"], "%d-%b-%Y %H:%M")
                formatted_stop_date = datetime.datetime.strftime(dt_stop, "%b-%d")
                date_range = f"{formatted_start_date} to {formatted_stop_date}"
            else:
                date_range = formatted_start_date

            found_similar = False

            #see if that med was prescribed before, and if so, add the date range; if not, create a new key with the date range in it
            for existing_name in med_dates.keys():
                if self.are_similar(base_name, existing_name):
                    med_dates[existing_name].append(date_range)
                    found_similar = True
                    break

            if not found_similar:
                med_dates[base_name] = [date_range]

        #at this point, we have a dictionary "med_dates" of the format with med names as keys, and a list of date ranges


        meds_by_type = {}
        for med_name, dates in med_dates.items():
            med_type = dictionary_to_print[med_name]["type"] #get "type" from the dictionary
            if dictionary_to_print[med_name]["count"] > 1:
                number_times_ordered = dictionary_to_print[med_name]["count"]
                med_name_time = f"{med_name}_{number_times_ordered}"
                dose = dictionary_to_print[med_name_time]["dose"]
            else:
                dose = dictionary_to_print[med_name]["dose"]
            units = dictionary_to_print[med_name]["units"]
            frequency = dictionary_to_print[med_name]["frequency"]
            formulation = dictionary_to_print[med_name]["Formulation"]
            if med_type not in meds_by_type: #if that's the first of that class, create new
                meds_by_type[med_type] = []
            meds_by_type[med_type].append(f"{med_name.title()} {dose} {units} {frequency} {formulation} {'PRN' if dictionary_to_print[med_name]['PRN'] else ''} ({', '.join(dates)})") #otherwise, add it to the list of that type

        for med_type in sorted(meds_by_type.keys()): #print it out by type
            print(f"\n{med_type}:")
            for med in meds_by_type[med_type]:
                print(f"     {med}")


if __name__ == "__main__":
    processor = OrderSheetProcessor()
    processor.create_med_dictionary_from_orders(pyperclip.paste())




