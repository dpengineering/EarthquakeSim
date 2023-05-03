"""
@file PassCodeScreen.py
File that contains the PassCodeScreen Class to interact with the PassCodeScreen.
There is no need to copy the .kv file into your project simply import this class and set the main screen name as well as transition back screen
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.app import App
import os.path

PASSWORD = '7266'
USERPW = ''

passcode_screen_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "", "PassCodeScreen.kv")

Builder.load_file(passcode_screen_path)

ADMIN_EVENTS_SCREEN = None
TRANSITION_BACK_SCREEN = 'main'

"""
Class to display a passcode on screen to advance to admin screen
"""


class PassCodeScreen(Screen):
    """
    Class used to enter the PassCodeScreen to enter the admin screen
    """

    def __init__(self, **kw):
        super(PassCodeScreen, self).__init__(**kw)

    def add_num(self, num):
        """
        Add a number to the current password entry
        :param num: Number to add
        :return: None
        """
        global USERPW

        self.ids.pw.text += '* '
        USERPW += str(num)

    def remove_num(self):
        """
        Remove a number from the current password entry
        :return: None
        """
        global USERPW
        self.ids.pw.text = self.ids.pw.text[:len(self.ids.pw.text) - 2]
        USERPW = USERPW[:len(USERPW) - 1]

    def check_pass(self):
        """
        Check to see if the password was entered correctly
        :return: None
        """
        global USERPW
        if PASSWORD == USERPW:
            self.ids.pw.text = ' '
            USERPW = ''

            if ADMIN_EVENTS_SCREEN is None:
                print("Specify the admin screen name by calling PassCodeScreen.set_admin_events_screen")
                return

            self.parent.current = ADMIN_EVENTS_SCREEN

    def transition_back(self):
        """
        Transition back to given transition back scren
        :return: None
        """
        global USERPW
        self.ids.pw.text = ""
        USERPW = ''
        self.parent.current = TRANSITION_BACK_SCREEN

    @staticmethod
    def set_admin_events_screen(screen):
        """
        Set the name of the screen to transition to when the password is correct
        :param screen: Name of the screen to transition to
        :return: None
        """
        global ADMIN_EVENTS_SCREEN
        ADMIN_EVENTS_SCREEN = screen

    @staticmethod
    def set_transition_back_screen(screen):
        """
        Set the screen to transition back to when the "Back to Game" button is pressed
        :param screen: Name of the screen to transition back to
        :return: None
        """
        global TRANSITION_BACK_SCREEN
        TRANSITION_BACK_SCREEN = screen

    @staticmethod
    def set_password(pswd):
        """
        Change the default password
        :param pswd: New password
        :return: None
        """
        global PASSWORD
        PASSWORD = pswd

    @staticmethod
    def change_main_screen_name(name):
        """
        Change the name of the screen to add the hidden button to go to the admin screen

        NOTE: This only needs to be run ONCE, once it is called with the new name you can remove the call from your code
        :param name: Name of the main screen of the UI
        :return: None
        """
        if name == '':
            return

        with open(passcode_screen_path) as file:
            data = file.readlines()

        # This needs to be updated every time there are line changes in the PassCodeScreen.kv
        # TODO implement a better way to dynamically change the main screen name
        data[134] = '<' + name + '>\n'

        with open(passcode_screen_path, 'w') as file:
            file.writelines(data)

