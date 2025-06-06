class Issue:
    def __init__(self, name, diagnosis_date=None, etiology=None, severity=None):
        self.name = name
        self.diagnosis_date = diagnosis_date
        self.etiology = etiology
        self.severity = severity

    def refresh(self, vitals, medications):
        """
        Refresh the issue based on the latest patient data.
        This method can be overridden by subclasses for issue-specific logic.
        """
        pass

    def to_dict(self):
        """Convert the issue to a dictionary for storage."""
        return {
            "name": self.name,
            "diagnosis_date": self.diagnosis_date,
            "etiology": self.etiology,
            "severity": self.severity,
        }

    @classmethod
    def from_dict(cls, data):
        """Create an Issue object from a dictionary."""
        return cls(
            name=data.get("name"),
            diagnosis_date=data.get("diagnosis_date"),
            etiology=data.get("etiology"),
            severity=data.get("severity"),
        )

    def get_summary(self):
        """Provide a default summary for generic issues."""
        return f"Issue: {self.name}. Diagnosis date: {self.diagnosis_date or 'N/A'}."
    
class Hypoxia(Issue):
    def __init__(self, name="Hypoxia", diagnosis_date=None, etiology=None, severity=None, treatments=None, max_o2=None, considerations=None):
        super().__init__(name, diagnosis_date, etiology, severity)
        self.treatments = treatments or []
        self.max_o2 = max_o2  # Maximal oxygen support
        self.considerations = considerations  # What is being considered if etiology is unclear
        self.o2sat = None  # Current oxygen saturation (dynamically updated)
        self.o2support = None  # Current oxygen support (dynamically updated)

    def refresh(self, vitals, medications):
        """
        Refresh the hypoxia issue based on the latest vitals and medications.
        """
        # Call the base class refresh method (if needed)
        super().refresh(vitals, medications)

        # Recalculate max O2 based on the latest vitals
        self.calculate_max_o2(vitals)

        # Update current oxygen saturation and support from the latest vitals
        self.update_current_o2(vitals)

        # Update treatments based on medications
        self.treatments = []
        if "Diuresis" in medications:
            self.treatments.append("Diuresis")
        if "Antibiotics" in medications:
            self.treatments.append("Antibiotics")
        if "Anticoagulation" in medications:
            self.treatments.append("Anticoagulation")

    def update_current_o2(self, vitals):
        """Update the current oxygen saturation and support from the latest vitals."""
        if not vitals:
            self.o2sat = None
            self.o2support = None
            return

        # Get the latest vitals entry
        latest_vitals = vitals[-1]  # Assuming vitals is a list of dictionaries
        for date, values in latest_vitals.items():
            self.o2sat = values.get("o2sat")  # Oxygen saturation
            self.o2support = values.get("o2modality")  # Oxygen support modality

    def calculate_max_o2(self, vitals):
        """Determine the maximum oxygen support based on patient vitals."""
        # Define precedence for oxygen modalities
        modality_precedence = {"Optiflow": 3, "Mask": 2, "Nasal Prongs": 1}
        max_o2 = None
        max_precedence = 0
        max_flow = 0

        for vital in vitals:
            # Skip empty or invalid dictionaries
            if not isinstance(vital, dict) or not vital:
                continue

            # Each 'vital' is a dictionary with a single key-value pair
            for date, values in vital.items():
                # Skip if 'values' is not a dictionary
                if not isinstance(values, dict):
                    continue

                # Extract modality and flow
                modality_data = values.get("o2modality")
                if isinstance(modality_data, (tuple, list)):
                    modality = modality_data[0]  # Extract the modality (e.g., "Nasal Prongs")
                    flow = modality_data[1] if len(modality_data) > 1 else 0  # Extract flow if available
                else:
                    modality = modality_data
                    flow = values.get("o2flow", 0)  # Assume flow is stored as "o2flow" in liters

                # Check if the modality has a higher precedence or the same modality with higher flow
                if modality in modality_precedence:
                    precedence = modality_precedence[modality]
                    if precedence > max_precedence or (precedence == max_precedence and flow > max_flow):
                        max_precedence = precedence
                        max_flow = flow
                        max_o2 = f"{modality} ({flow})"

        self.max_o2 = max_o2 or "Room Air"  # Default to "Room Air" if no oxygen support is found
        return self.max_o2

    def get_summary(self):
        """Generate a detailed summary for hypoxia."""
        # Format the current oxygen support
        current_o2support = None
        if isinstance(self.o2support, list) and len(self.o2support) == 2:
            current_o2support = f"{self.o2support[0]} ({self.o2support[1]})"  # Match format with max_o2
        elif self.o2support:
            current_o2support = self.o2support

        # Determine if the current O2 is the highest
        if self.max_o2 and current_o2support and self.max_o2 == current_o2support:
            max_o2_sentence = "This is the most O2 they have been on this admission."
        else:
            max_o2_sentence = f"The most O2 they have been on is {self.max_o2 or 'N/A'}."

        # Build the summary
        summary = f"Symptoms started {self.diagnosis_date or 'N/A'}. "
        summary += f"Currently, the patient is saturating {self.o2sat or 'N/A'}% {current_o2support or 'Room Air'}. "
        summary += f"{max_o2_sentence} "

        if self.etiology:
            summary += f"We suspect the etiology is {self.etiology}."
        else:
            summary += f"Unclear what exact etiology is, but we are considering {self.considerations or 'N/A'}. "

        if self.treatments:
            summary += f"Treatment so far has included {', '.join(self.treatments)}."
        else:
            summary += "No treatments have been initiated yet."

        return summary

class Infection(Issue):
    def __init__(self, name="Infection", diagnosis_date=None, site=None):
        super().__init__(name, diagnosis_date)
        self.site = site  # Infection site (e.g., lung, blood, urine)
        self.positive_cultures = []  # Store positive culture data

    def refresh(self, vitals, medications, micro_data):
        """
        Refresh the infection issue based on the latest patient data.
        """
        super().refresh(vitals, medications)

        # Update culture data for the selected site
        self.update_culture_data(micro_data)

    def update_culture_data(self, micro_data):
        """
        Extract positive culture data for the selected site from the patient's microbiology data.
        """
        if not micro_data or not self.site:
            self.positive_cultures = []
            return

        self.positive_cultures = [
            {"date": entry.get("date"), "bacteria": entry.get("bacteria")}
            for entry in micro_data
            if entry.get("culture_type") == self.site.lower() and entry.get("bacteria")
        ]

    def get_summary(self):
        """Generate a detailed summary for infection."""
        summary = f"Symptoms started {self.diagnosis_date or 'N/A'}. "
        summary += f"The suspected site of infection is {self.site or 'N/A'}. "

        if self.positive_cultures:
            summary += f"Positive {self.site.lower()} cultures found:\n"
            for culture in self.positive_cultures:
                summary += f"- Date: {culture['date']}, Bacteria: {', '.join(culture['bacteria'])}\n"
        else:
            summary += f"No positive {self.site.lower()} cultures found.\n"

        return summary

    @classmethod
    def from_dict(cls, data):
        """Create an Infection object from a dictionary."""
        obj = cls(
            name=data.get("name"),
            diagnosis_date=data.get("diagnosis_date"),
            site=data.get("site"),
        )
        obj.positive_cultures = data.get("positive_cultures", [])
        return obj

    def to_dict(self):
        """Convert the infection issue to a dictionary for storage."""
        data = super().to_dict()
        data.update({
            "site": self.site,
            "positive_cultures": self.positive_cultures
        })
        return data