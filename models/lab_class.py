import datetime as dt
import re
import pprint as pp
import pyperclip
from models.lab_help import replacement_dictionary, lab_categories, lab_norms



class Labs:
    """A class to represent and process laboratory test results.
    Attributes:
    -----------
    pt_micro : dict
        A dictionary to store microbiology test results.
    run_datetime : str
        The datetime when the instance is created.
    pt_labs : dict
        A dictionary to store parsed laboratory test results.
    Methods:
    --------
    __init__(self, lab_string):
        Initializes the Labs instance with the provided lab string.
    line_by_line(self, string) -> tuple:
        Parses the lab string line by line and extracts lab values.
    is_date_time(self, string: str) -> str:
        Checks if a string contains a datetime and returns it.
    find_lab_values(self, current_line: str, date: dt.datetime, pt_labs: dict) -> tuple:
        Finds and extracts lab values from a line of text.
    is_decimal(self, string) -> bool:
        Checks if a string can be converted to a decimal number.
    replace_word(self, word: str, reference: dict) -> str:
        Replaces a word with its corresponding value from a reference dictionary.
    get_latest(self, list_of_tuples: list) -> tuple:
        Returns the latest value from a list of tuples.
    print_labs_by_date(self, latest=True, specific_labs=None):
        Prints lab results grouped by date.
    get_lab_stats(self, *lab_names: str) -> dict:
        Calculates statistics for specified lab tests.
    print_basic_labs(self):
        Prints basic lab results categorized by lab type.
    extract_micros(self, lab_report):
        Extracts microbiology test results from the lab report.
    get_culture_type(self, text_chunk):
        Determines the type of culture test from a text chunk.
    exclaimation_chunks(self, lab_report):
        Splits the lab report into chunks based on exclamation marks.
    culture_extractor(self, type, text_chunk, date_stamp):
        Extracts culture test results from a text chunk.
    c_diff_extractor(self, text_chunk, date_stamp):
        Extracts C. diff test results from a text chunk.
    cov_extractor(self, text_chunk, date_stamp):
        Extracts COVID-19, Influenza, and RSV test results from a text chunk."""
    def __init__(self, lab_string):

        self.pt_micro = {
            "Cultures": {},
            "Toxin": {
                "C diff": [],
            },
            "Virology": {}
            }
        
        self.pt_labs = self.line_by_line(lab_string)

        self.extract_micros(lab_string)

        self.imaging = self.extract_imaging(lab_string)

        self.echo = []
        self.echo.append(self.extract_echo(lab_string))

    def update_labs(self, lab_string): #for if labs already exist
        self.pt_labs.update(self.line_by_line(lab_string))
        if self.extract_micros(lab_string):
            self.pt_micro.update(self.extract_micros(lab_string))
        if self.extract_imaging(lab_string):
            self.imaging.update(self.extract_imaging(lab_string))
        if not hasattr(self, 'echo'):
            self.echo = []
        self.echo = []
        self.echo.append(self.extract_echo(lab_string))

    def line_by_line(self, string) -> tuple:
        list_of_text = string.strip().split("\n")
        current_date, pt_labs = "", {}

        for line in list_of_text:
            if self.is_date_time(line):
                current_date = self.is_date_time(line)
            else:
                pt_labs = self.find_lab_values(line, current_date, pt_labs)
        return pt_labs

    def is_date_time(self, string: str) -> str:
        words = string.split(" ")
        try:
            datetime_str = f"{words[0]} {words[1]}"
            datetime_object = dt.datetime.strptime(datetime_str, "%d-%b-%Y %H:%M") #?excludes BDs because no time stamp?
            return datetime_object
        except (ValueError, IndexError):
            return False

    def find_lab_values(self, current_line: str, date: dt.datetime, pt_labs: dict) -> tuple:
        words = current_line.split(" ")

        for word in words:
            if (word.isnumeric() or self.is_decimal(word)) and not words[0][0:2].isnumeric():
                index_of_value = words.index(word)
                value = words[index_of_value]
                lab_name = " ".join(words[0:index_of_value])

                if lab_name not in pt_labs:
                    pt_labs[lab_name] = []
                    pt_labs[lab_name].append((value, date))
                else:
                    pt_labs[lab_name].append((value, date))

        return pt_labs

    def is_decimal(self, string) -> bool:
        try:
            float(string)
            return True
        except ValueError:
            return False

    def replace_word(self, word: str, reference: dict) -> str:
        if word in reference.keys():
            return reference[word]
        return word

    def get_latest(self, list_of_tuples: list) -> tuple:
        try:
            return list_of_tuples[-1]
        except IndexError:
            print(f"Couldn't return for {list_of_tuples}")

    def print_labs_by_date(self, latest=True, specific_labs=None):
        temp_dict = self.pt_labs.copy()

        if latest:
            for lab, values in self.pt_labs.items():
                temp_dict[lab] = [self.get_latest(values)]

        if specific_labs:
            temp_dict = {lab: values for lab, values in temp_dict.items() if lab in specific_labs}

        labs_by_date = {}
        for lab, values in temp_dict.items():
            for value, date in values:
                date_key = date.date()
                if date_key not in labs_by_date:
                    labs_by_date[date_key] = {}
                if date not in labs_by_date[date_key]:
                    labs_by_date[date_key][date] = []
                labs_by_date[date_key][date].append((lab, value))

        sorted_dates = sorted(labs_by_date.keys(), reverse=True)

        for date_key in sorted_dates:
            print('\n')
            print(date_key.strftime("%B %d"))
            for time_key in sorted(labs_by_date[date_key].keys()):
                time_str = time_key.strftime("%H:%M")
                print(f"   ({time_str})", end=" ")
                for lab, value in labs_by_date[date_key][time_key]:
                    print(f"{self.replace_word(lab, replacement_dictionary)}: {value}", end="  ")
    def get_lab_stats(self, *lab_names: str) -> dict:
        """
        Calculate statistics for specified lab tests.
        Args:
            lab_names (str): Variable length argument list of lab test names.
        Returns:
            dict: A dictionary where each key is a lab test name and the value is another dictionary 
                  containing the following statistics:
                  - "min": The minimum value of the lab test (or None if the lab test is not found).
                  - "max": The maximum value of the lab test (or None if the lab test is not found).
                  - "average": The average value of the lab test (or None if the lab test is not found).
                  - "latest": The latest value of the lab test (or None if the lab test is not found).
        """

        stats = {}

        for lab_name in lab_names:
            if lab_name not in self.pt_labs:
                stats[lab_name] = {"min": None, "max": None, "average": None, "latest": None}
                continue

            values = [float(value) for value, date in self.pt_labs[lab_name]]
            min_value = min(values)
            max_value = max(values)
            average_value = sum(values) / len(values)
            latest_value = values[-1]  # Assuming the latest value is the last one in the list

            stats[lab_name] = {
                "min": min_value,
                "max": max_value,
                "average": average_value,
                "latest": latest_value
            }
        return stats

    def print_basic_labs(self):
        for key, values in lab_categories.items():
            self.print_labs_by_date(True, values)

    def lab_value_checker(self, lab):
        if lab in self.pt_labs:
            return LabAnalysis(lab, self.pt_labs[lab])
        else:
            return None
        
    def add_lab(self, lab_name, value, date):
        if lab_name not in self.pt_labs:
            self.pt_labs[lab_name] = []
        self.pt_labs[lab_name].append((value, date))

##MICROBIOLOGY
    def extract_micros(self, lab_report):
        list_of_micros = self.exclaimation_chunks(lab_report)

        for item in list_of_micros:
            date_stamp = item[0:17]
            if "Culture" in item:
                culture_type = self.get_culture_type(item)
                self.culture_extractor(culture_type, item, date_stamp)
            if "Stool for C" in item:
                self.c_diff_extractor(item, date_stamp)
            if "SARS-CoV-2, Influenza, RSV Panel" in item:
                self.cov_extractor(item, date_stamp)

    def get_culture_type(self, text_chunk):
        split_lines = text_chunk.split("\n")
        for line in split_lines:
            if "=" in line:
                test_type = line.replace("=", "").strip()
                return test_type

    def exclaimation_chunks(self, lab_report):
        line_by_line = (lab_report).split("\n")
        new_string = ""
        for line in line_by_line:
            if self.is_date_time(line):
                new_string += "!!!" + line + "\n"
            else:
                new_string += line + "\n"
        return new_string.split("!!!")

    def culture_extractor(self, type, text_chunk, date_stamp):
        things_to_add = []
        self.pt_micro["Cultures"].setdefault(type, [])

        number_bact_match = r'\d\).+'
        sens_pattern = r'\([1-9]\)\n(?:[^\n]+\n)+\([1-9]\)\n'

        number_find = re.search(number_bact_match, text_chunk)
        sens_find = re.search(sens_pattern, text_chunk)
        things_to_add.append(date_stamp)
        if number_find:
            things_to_add.append(number_find.group(0))
        else:
            things_to_add.append("No bacteria found.")
        if sens_find:
            sens_lines = sens_find.group(0).split("\n")
            list_of_sensitivities = [line[:-2] for line in sens_lines if line.endswith('S')]
            things_to_add.append(list_of_sensitivities)
        else:
            things_to_add.append("No sensitivites.")

        self.pt_micro["Cultures"][type].append(things_to_add)

    def c_diff_extractor(self, text_chunk, date_stamp):
        try:
            if "toxin NEGATIVE" in text_chunk:
                thing_to_add = (date_stamp, "Negative")
            if "toxin POSITIVE" in text_chunk:
                thing_to_add = (date_stamp, "Positive")

            self.pt_micro["Toxin"]["C diff"].append(thing_to_add)
        except UnboundLocalError:
            print("Couldn't extract C diff test")

    def cov_extractor(self, text_chunk, date_stamp):
        self.pt_micro["Virology"]["Influenza A"] = []
        self.pt_micro["Virology"]["Influenza B"] = []
        self.pt_micro["Virology"]["RSV RNA"] = []
        self.pt_micro["Virology"]["COVID"] = []

        split_lines = text_chunk.split("\n")
        for line in split_lines:
            if "Influenza A RNA" in line:
                result = line.replace("Influenza A RNA", "")
                self.pt_micro["Virology"]["Influenza A"].append((result.strip(), date_stamp))
            if "Influenza B RNA" in line:
                result = line.replace("Influenza B RNA", "")
                self.pt_micro["Virology"]["Influenza B"].append((result.strip(), date_stamp))
            if "RSV RNA" in line:
                result = line.replace("RSV RNA", "")
                self.pt_micro["Virology"]["RSV RNA"].append((result.strip(), date_stamp))
            if "COVID-19 Virus RNA" in line:
                result = line.replace("COVID-19 Virus RNA", "")
                self.pt_micro["Virology"]["COVID"].append((result.strip(), date_stamp))
            

#imaging
    def extract_imaging(self, lab_report):
        imaging_dictionary = {}
        chunks = self.exclaimation_chunks(lab_report)
        for chunk in chunks:
            index = chunk.find("Interpreting Radiologist:")
            if index != -1:
                report = chunk[:index]
                chunky_split = chunk.split("\n")
                date = chunky_split[0][:17]
                study_type = chunky_split[1].replace("Final", "")
                imaging_dictionary.setdefault(study_type, [])
                imaging_dictionary[study_type].append([date, report, ""])
        return imaging_dictionary

#echo
    def extract_echo(self, lab_report):
        echo_dictionary = {}
        chunks = self.exclaimation_chunks(lab_report)
        if "Echocardio" in chunks[1]:
            echo_report = chunks[1].split('\n')
            echo_date = echo_report[0][:17]
            index = 0
            items_of_interest = ["Left Ventricle", "Right Ventricle", "Left Atrium", "Right Atrium", "Aortic Valve", "Mitral Valve", "Tricuspid Valve", "Pulmonic Valve", "Conclusions",  "Farts"]
            for line in echo_report:
                if "Reading Physician" in line:
                    echo_dictionary["Reading Physician"] = line[19:]
                if any(item in line for item in items_of_interest):
                    matched_item = next(item for item in items_of_interest if item in line)
                    matched_index = items_of_interest.index(matched_item)
                    short_hop = echo_report[index+1]
                    subdex = index + 1
                    text = ""
                    while subdex < len(echo_report) and items_of_interest[matched_index+1] not in short_hop:
                        text += short_hop
                        subdex += 1
                        if subdex < len(echo_report):
                            short_hop = echo_report[subdex]
                    echo_dictionary[matched_item] = text
                    
                index += 1
                if "Conclusions" in echo_dictionary.keys():
                    line_string = "____"
                    underscore_index = echo_dictionary["Conclusions"].find(line_string)
                    echo_dictionary["Conclusions"] = echo_dictionary["Conclusions"][:underscore_index]

            return [echo_dictionary, {}, echo_date]

class LabAnalysis:
    def __init__(self, lab_name, lab_results):   
        self.lab_name = lab_name
        self.lab_results = lab_results   

        if self.lab_results == None:
            self.lab_results = "No Value found for this instance of LabAnalysis"
        
        self.lab_trend = self.compare_lab_trend(self.lab_results)
        self.latest_lab_range = self.assess_lab_range(self.lab_results[-1][0])
        self.print_lab_assessment()
  
    def compare_lab_trend(self, lab_results):
        """
        Compares the latest lab value to the previous one and returns whether
        it increased, decreased, or is unchanged.
        
        Args:
            lab_results (list): List of (lab_value, date) tuples.

        Returns:
            str: 'increased', 'decreased', 'unchanged', or None.
        """
        # Optional: ensure results are sorted by date.
        # lab_results.sort(key=lambda x: x[1])

        if len(lab_results) < 2:
            return None

        prev_value = lab_results[-2][0]
        latest_value = lab_results[-1][0]

        if latest_value > prev_value:
            return "increasing"
        elif latest_value < prev_value:
            return "decreasing"
        else:
            return "stable"

    def assess_lab_range(self, lab_value):
        """
        Determines if the given lab_value is within, below, or above the normal range.

        Args:
            lab_name (str): The key used to look up the min and max normal values in lab_norms.
            lab_value (float): The lab result to interpret.

        Returns:
            str: 'Low', 'High', 'Normal', or 'Unknown' if no range is found.
        """
        if self.lab_name not in lab_norms:
            return "Lab high/low range not found"
        
        min_val, max_val = lab_norms[self.lab_name]
        
        lab_value = int(lab_value)
        if lab_value < min_val:
            return "Low"
        elif lab_value > max_val:
            return "High"
        else:
            return "Normal"
        
    def print_lab_assessment(self):
        text = f"    The latest lab value is {self.latest_lab_range} and the overall trend is {self.lab_trend}.\n"
        return text

