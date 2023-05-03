from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.clock import Clock


from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

class Manual(Screen, Oscillator):
    def __init__(self):
        self.horizontal_frequency = 0
        self.horizontal_amplitude = 0

    def frequency_change(self):
        Oscillator.frequency_change()

    def amplutide_change(self):
        Oscillator.amplitude_change()

    def main_screen(self):
        SCREEN_MANAGER.current = 'main'

    def stop(self):
        Oscillator.stop()

    def start(self):
        Oscillator.start()

    def disable(self):
        Oscillator.disableMotors()

    def exit(self):
        quit()