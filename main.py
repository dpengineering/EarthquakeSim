import os

os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty


from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
from pidev.kivy.selfupdatinglabel import SelfUpdatingLabel

from datetime import datetime
time = datetime

from dpeaDPi.DPiComputer import DPiComputer
from Oscillator import Oscillator

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Earthquake Sim", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'

class EarthquakeSimGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER

Window.clearcolor = (0.2, 0.2, 0.2, 1)

# DPI Network Setup
dpiComputer = DPiComputer()
dpiComputer.initialize()

"""
Main Screen 
"""

class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    # Create instance of Oscillator class using DPIStepper board 1, passes dpiComputer for sensor reading
    HorizontalAxis = Oscillator(1, dpiComputer)

    # Init properties referenced in Kivi UI for debug text
    debugText = StringProperty()
    amplitudeValue = 0
    frequencyValue = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debugText = "Door Closed!"

    # Provide a function for setting the debug text
    # Later passed down into oscillator instance for logging from there
    def log(self, text):
        self.debugText = text

    # On slider changes, call Oscillator instance functions, pass in new values
    def frequencyChange(self, value):
        self.frequencyValue = value
        self.HorizontalAxis.frequencyChange(value)

    def amplitudeChange(self, value):
        self.amplitudeValue = value
        self.HorizontalAxis.amplitudeChange(value)

    # On button presses, call Oscillator instance functions as well
    def stop(self):
        self.HorizontalAxis.stop()

    def start(self):
        # pass log function into start method for debug text during operation
        if self.amplitudeValue == 0 and self.frequencyValue == 0:
            self.HorizontalAxis.start(self.log)
            return
        else:
            self.log("Please Reset Sliders")
    
    # Screen changes
    def main_screen(self):
        SCREEN_MANAGER.current = 'main'

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'

"""
Admin Screen 
"""

class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    def manual_screen_change(self):
        SCREEN_MANAGER.current = 'Manual'

    def exit_program(self):
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""

def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    EarthquakeSimGUI().run()