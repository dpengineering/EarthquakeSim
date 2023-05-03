import os
import spidev
import RPi.GPIO as GPIO

# import time
from datetime import datetime
from time import sleep
from threading import Thread

# os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

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

# initalize values for the stepper motor
from dpeaDPi.DPiStepper import DPiStepper
from dpeaDPi.DPiComputer import DPiComputer

# setting up kivy stuff

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


dpiComputer = DPiComputer()
dpiComputer.initialize()

dpiStepperHorizontal = DPiStepper()
dpiStepperHorizontal.setBoardNumber(1)

dpiStepperVertical= DPiStepper()
dpiStepperVertical.setBoardNumber(0)

# Enable the stepper motors, when disabled the motors are turned off and spin freely.
#

if not dpiStepperHorizontal.initialize():
    print("Communication with the DPiStepper board failed.")

dpiStepperHorizontal.enableMotors(True)
# original steeper motor values s1 = stepper(port=1, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
#              steps_per_unit=200, speed=2)
# probably 32 or 200
microstepping = 16

dpiStepperHorizontal.setMicrostepping(microstepping)

# setting up speed and acceleration
dpiStepperHorizontal.setAccelerationInStepsPerSecondPerSecond(0, 1000)
dpiStepperHorizontal.setAccelerationInStepsPerSecondPerSecond(1, 1000)

dpiStepperVertical.setAccelerationInStepsPerSecondPerSecond(0, 1000)
dpiStepperVertical.setAccelerationInStepsPerSecondPerSecond(1, 1000)

# setting the speed I think 200 is the number fo steps per rotation
dpiStepperHorizontal.setSpeedInStepsPerSecond(0, 25600)
dpiStepperHorizontal.setSpeedInStepsPerSecond(1, 25600)

dpiStepperVertical.setSpeedInStepsPerSecond(0, 25600)
dpiStepperHorizontal.setSpeedInStepsPerSecond(1, 25600)

motors = [0, 1]
linear_offset = 10

Window.clearcolor = (1, 1, 1, 1)


class MainScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.motor_speed = 0

        """

        self.motor_0_speed = 0
        self.current_spiral_position = 0
        self.freqency_to_motor_speed = 0
        self.freqency = 0

        """

        """Things that are actually happening when the MainScreen class is called
        These variables are only defined here so they can be altered later.
        s0_rotation_dierction controls the rotation direction and stays between 1 and 0.
        clock_control helps control the clock, as if the_dance() has been called the variable should update
        and cancel the clock until the value is returned to 0, which the_dance function does when it is finished running"""

    # def home(self):
    #
    #     for i in motors:
    #         dpiStepper.decelerateToAStop(i)
    #         dpiStepper.waitUntilMotorStops(i)
    #
    #     # Move linear disk to a vertical position
    #     dpiStepper.moveToHomeInSteps(0, 0, 100, 800)
    #     dpiStepper.moveToAbsolutePositionInSteps(0, linear_offset, True)
    #     dpiStepper.setCurrentPositionInSteps(0, 0)

    def move_syncro(self):
        stop_motors = False

        if dpiStepperHorizontal.getAllMotorsStopped():
            # dpiStepper.enableMotors(True)
            dpiStepperHorizontal.moveToRelativePositionInSteps(0, -2000000, False)
            dpiStepperHorizontal.moveToRelativePositionInSteps(1, 2000000, False)
            print("moving!")

        else:
            stop_motors = True
            for i in motors:
                dpiStepperHorizontal.decelerateToAStop(i)
            print("s0: I'm softStopped!")
            sleep(5)
        # dpiStepper.enableMotors(False)

    def dual_move_syncro(self):
        stop_motors = False

        if dpiStepperHorizontal.getAllMotorsStopped() and dpiStepperVertical.getAllMotorsStopped():
            # dpiStepper.enableMotors(True)
            dpiStepperHorizontal.moveToRelativePositionInSteps(0, -2000000, False)
            dpiStepperHorizontal.moveToRelativePositionInSteps(1, 2000000, False)

            dpiStepperVertical.moveToRelativePositionInSteps(0, -2000000, False)
            dpiStepperVertical.moveToRelativePositionInSteps(1, 2000000, False)

            print("moving!")

        else:
            stop_motors = True
            for i in motors:
                dpiStepperHorizontal.decelerateToAStop(i)
                dpiStepperVertical.decelerateToAStop(i)
            print("s0: I'm softStopped!")
            sleep(5)
        # dpiStepper.enableMotors(False)

    def speed_change(self):

        self.motor_speed = self.ids.speed_slider_1.value * 1000

        dpiStepperHorizontal.setSpeedInStepsPerSecond(0, self.motor_speed * -1)
        dpiStepperHorizontal.setSpeedInStepsPerSecond(1, self.motor_speed)

        dpiStepperVertical.setSpeedInStepsPerSecond(0, self.motor_speed * -1)
        dpiStepperVertical.setSpeedInStepsPerSecond(1, self.motor_speed)

    def enable_motors(self):
        stop_motors = False

        if dpiStepperHorizontal.getAllMotorsStopped():
            dpiStepperHorizontal.enableMotors(True)

    def disable_horizontal_motors(self):
        stop_motors = False

        if dpiStepperHorizontal.getAllMotorsStopped():
            dpiStepperHorizontal.enableMotors(False)

        if dpiStepperVertical.getAllMotorsStopped():
            dpiStepperVertical.enableMotors(False)

    def home(self):

        #home horizontal set first
        if dpiStepperVertical.getAllMotorsStopped():

            dpiStepperVertical.enableMotors(False)

            # reenable  Horizontal just in case
            if dpiStepperHorizontal.getAllMotorsStopped():
                dpiStepperHorizontal.enableMotors(True)

            dpiStepperHorizontal.setSpeedInStepsPerSecond(1, 1600)
            dpiStepperHorizontal.setSpeedInStepsPerSecond(0, 1600)
            # dpiStepper.moveToHomeInSteps(1, 0, 100, 3)

            results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperHorizontal.getStepperStatus(1)
            if results != True:
                return

            # make sure were not already home
            if homeAtHomeSwitchFlg != True:

                # move motors together to avoid collision
                dpiStepperHorizontal.moveToRelativePositionInSteps(0, -3200, False)
                dpiStepperHorizontal.moveToRelativePositionInSteps(1, 3200, False)

                while True:
                    results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperHorizontal.getStepperStatus(1)
                    if homeAtHomeSwitchFlg:
                        break

                dpiStepperHorizontal.emergencyStop(0)
                dpiStepperHorizontal.emergencyStop(1)
                sleep(0.1)

                # move away from sensor
                dpiStepperHorizontal.moveToRelativePositionInSteps(0, 3200, False)
                dpiStepperHorizontal.moveToRelativePositionInSteps(1, -3200, False)

                while True:
                    results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperHorizontal.getStepperStatus(1)
                    if not homeAtHomeSwitchFlg:
                        break

                dpiStepperHorizontal.emergencyStop(0)
                dpiStepperHorizontal.emergencyStop(1)
                sleep(0.1)

                # move back, but slow
                dpiStepperHorizontal.setSpeedInStepsPerSecond(0, 200)
                dpiStepperHorizontal.setSpeedInStepsPerSecond(1, 200)

                dpiStepperHorizontal.moveToRelativePositionInSteps(0, -3200, False)
                dpiStepperHorizontal.moveToRelativePositionInSteps(1, 3200, False)

                while True:
                    results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperHorizontal.getStepperStatus(1)
                    if homeAtHomeSwitchFlg:
                        break

                dpiStepperHorizontal.emergencyStop(0)
                dpiStepperHorizontal.emergencyStop(1)
                sleep(0.1)

                dpiStepperHorizontal.moveToRelativePositionInSteps(0, -100, False)
                dpiStepperHorizontal.moveToRelativePositionInSteps(1, 100, False)

                sleep(1)

                dpiStepperHorizontal.moveToRelativePositionInSteps(1, 1600, False)
                dpiStepperHorizontal.moveToRelativePositionInSteps(0, -1600, False)

                sleep(1)

                while not dpiStepperHorizontal.getAllMotorsStopped():
                    sleep(.1)

                # homing spiral motor
                results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperHorizontal.getStepperStatus(0)
                print("start of homing" + str(homeAtHomeSwitchFlg))

                if results != True:
                    return

                dpiStepperHorizontal.setSpeedInStepsPerSecond(0, 1600)

                # make sure were not already home
                if homeAtHomeSwitchFlg != True:
                    dpiStepperHorizontal.moveToRelativePositionInSteps(0, -3200, False)

                    while True:
                        results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperHorizontal.getStepperStatus(0)
                        if homeAtHomeSwitchFlg:
                            break

                    print("broke out of first for loop")

                    dpiStepperHorizontal.emergencyStop(0)
                    sleep(0.1)

                    # move away from sensor
                    dpiStepperHorizontal.moveToRelativePositionInSteps(0, 3200, False)

                    while True:
                        results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperHorizontal.getStepperStatus(0)
                        if not homeAtHomeSwitchFlg:
                            break

                    dpiStepperHorizontal.emergencyStop(0)
                    sleep(0.1)

                    # move back, but slow
                    dpiStepperHorizontal.setSpeedInStepsPerSecond(0, 200)

                    dpiStepperHorizontal.moveToRelativePositionInSteps(0, -3200, False)

                    while True:
                        results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperHorizontal.getStepperStatus(0)
                        if homeAtHomeSwitchFlg:
                            break

                    dpiStepperHorizontal.emergencyStop(0)
                    sleep(0.1)

                    # uncomment in case buffer is needed 100 steps is 3% of a rotation
                    # dpiStepper.moveToRelativePositionInSteps(0, -100, False)

                    dpiStepperHorizontal.setCurrentPositionInSteps(1, 0)
                    dpiStepperHorizontal.setCurrentPositionInSteps(0, 0)

            #home Vertical

                # home horizontal set first
                if dpiStepperHorizontal.getAllMotorsStopped():

                    dpiStepperHorizontal.enableMotors(False)

                    # reenable  Horizontal just in case
                    dpiStepperVertical = dpiStepperHorizontal
                    if dpiStepperVertical.getAllMotorsStopped():
                        dpiStepperVertical.enableMotors(True)

                    dpiStepperVertical.setSpeedInStepsPerSecond(1, 1600)
                    dpiStepperVertical.setSpeedInStepsPerSecond(0, 1600)
                    # dpiStepper.moveToHomeInSteps(1, 0, 100, 3)

                    results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperVertical.getStepperStatus(1)
                    if results != True:
                        return

                    # make sure were not already home
                    if homeAtHomeSwitchFlg != True:

                        # move motors together to avoid collision
                        dpiStepperVertical.moveToRelativePositionInSteps(0, -3200, False)
                        dpiStepperVertical.moveToRelativePositionInSteps(1, 3200, False)

                        while True:
                            results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperVertical.getStepperStatus(1)
                            if homeAtHomeSwitchFlg:
                                break

                        dpiStepperVertical.emergencyStop(0)
                        dpiStepperVertical.emergencyStop(1)
                        sleep(0.1)

                        # move away from sensor
                        dpiStepperVertical.moveToRelativePositionInSteps(0, 3200, False)
                        dpiStepperVertical.moveToRelativePositionInSteps(1, -3200, False)

                        while True:
                            results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperVertical.getStepperStatus(1)
                            if not homeAtHomeSwitchFlg:
                                break

                        dpiStepperVertical.emergencyStop(0)
                        dpiStepperVertical.emergencyStop(1)
                        sleep(0.1)

                        # move back, but slow
                        dpiStepperVertical.setSpeedInStepsPerSecond(0, 200)
                        dpiStepperVertical.setSpeedInStepsPerSecond(1, 200)

                        dpiStepperVertical.moveToRelativePositionInSteps(0, -3200, False)
                        dpiStepperVertical.moveToRelativePositionInSteps(1, 3200, False)

                        while True:
                            results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperVertical.getStepperStatus(1)
                            if homeAtHomeSwitchFlg:
                                break

                        dpiStepperVertical.emergencyStop(0)
                        dpiStepperVertical.emergencyStop(1)
                        sleep(0.1)

                        dpiStepperVertical.moveToRelativePositionInSteps(0, -100, False)
                        dpiStepperVertical.moveToRelativePositionInSteps(1, 100, False)

                        sleep(1)

                        dpiStepperVertical.moveToRelativePositionInSteps(1, 1600, False)
                        dpiStepperVertical.moveToRelativePositionInSteps(0, -1600, False)

                        sleep(1)

                        while not dpiStepperVertical.getAllMotorsStopped():
                            sleep(.1)

                        # homing spiral motor
                        results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperVertical.getStepperStatus(0)
                        print("start of homing" + str(homeAtHomeSwitchFlg))

                        if results != True:
                            return

                        dpiStepperVertical.setSpeedInStepsPerSecond(0, 1600)

                        # make sure were not already home
                        if homeAtHomeSwitchFlg != True:
                            dpiStepperVertical.moveToRelativePositionInSteps(0, -3200, False)

                            while True:
                                results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperVertical.getStepperStatus(0)
                                if homeAtHomeSwitchFlg:
                                    break

                            print("broke out of first for loop")

                            dpiStepperVertical.emergencyStop(0)
                            sleep(0.1)

                            # move away from sensor
                            dpiStepperVertical.moveToRelativePositionInSteps(0, 3200, False)

                            while True:
                                results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperVertical.getStepperStatus(0)
                                if not homeAtHomeSwitchFlg:
                                    break

                            dpiStepperVertical.emergencyStop(0)
                            sleep(0.1)

                            # move back, but slow
                            dpiStepperVertical.setSpeedInStepsPerSecond(0, 200)

                            dpiStepperVertical.moveToRelativePositionInSteps(0, -3200, False)

                            while True:
                                results, stoppedFlg, __, homeAtHomeSwitchFlg = dpiStepperVertical.getStepperStatus(0)
                                if homeAtHomeSwitchFlg:
                                    break

                            dpiStepperVertical.emergencyStop(0)
                            sleep(0.1)

                            # uncomment in case buffer is needed 100 steps is 3% of a rotation
                            # dpiStepper.moveToRelativePositionInSteps(0, -100, False)

                            dpiStepperVertical.setCurrentPositionInSteps(1, 0)
                            dpiStepperVertical.setCurrentPositionInSteps(0, 0)



    def stop(self):
        dpiStepperHorizontal.emergencyStop(0)
        dpiStepperHorizontal.emergencyStop(1)

        if dpiStepperHorizontal.getAllMotorsStopped():
            dpiStepperHorizontal.enableMotors(False)

    def throw_error(self):
        print("string" + int(among_us))


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

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

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

    @staticmethod
    def exit_program():
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
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
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
    ProjectNameGUI().run()