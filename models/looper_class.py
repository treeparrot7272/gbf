import os
from utils.gb_ai import print_in_columns

class Looper():
    """
    A class used to represent a looping menu system.

    Attributes
    ----------
    active : bool
        A flag to control the loop's activity.
    header_text : str
        The text to be displayed as the header.
    options : list
        A list of options to be displayed.
    show_options : bool
        A flag to control the display of options.

    Methods
    -------
    run():
        Starts the loop and processes user input.
    show_header():
        Clears the screen and displays the header and options.
    stop():
        Stops the loop by setting the active flag to False.
    toggle_options():
        Toggles the display of options.
    handle_choice(choice):
        Handles invalid user choices.
    """
    def __init__(self):
        self.active = True
        self.header_text = ""
        self.options = ['There are no options']
        self.show_options = True  # Add a flag to control the display of options

    def run(self):
        while self.active:
            self.show_header()
            choice = input("\n\nPlease select a command>>> ")
            if choice == "x":
                self.stop()
            elif choice == "help":
                self.toggle_options()
            else:
                self.handle_choice(choice)

    def show_header(self):
        os.system('clear')
        print(self.header_text)
        if self.show_options:
            print_in_columns(self.options)

    def stop(self):
        self.active = False

    def toggle_options(self):
        self.show_options = not self.show_options

    def handle_choice(self, choice):
        print(f"Invalid choice: {choice}")

