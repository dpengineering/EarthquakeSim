import os
import spidev
import RPi.GPIO as GPIO

#import time
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

from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
from pidev.stepper import stepper
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

#initalize values for the stepper motor
from dpeaDPi.DPiStepper import DPiStepper

dpiStepper.setBoardNumber(0)

# Enable the stepper motors, when disabled the motors are turned off and spin freely.
#
dpiStepper.enableMotors(True)

if dpiStepper.initialize() != True:
        print("Communication with the DPiStepper board failed.")
        return

# original steeper motor values s1 = stepper(port=1, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
#              steps_per_unit=200, speed=2)
#probably 32 or 200
microstepping = 32

dpiStepper.setMicrostepping(microstepping)

#setting up speed and acceleration
dpiStepper.setAccelerationInStepsPerSecondPerSecond(1, accel_steps_per_second_per_second)

#setting the speed I think 200 is the number fo steps per rotation
dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)

#use to check if stepper motor with stright disk is in line
currentPosition = dpiStepper.getCurrentPositionInSteps(0)[1]
print(f"Pos = {currentPosition}")


stop_motors = False

#might be useful later to stop motors
def stop_all():
    #
    # now wait for both motors to stop
    #
    while dpiStepper.getAllMotorsStopped() == False:
        sleep(0.02)

"""
def moving_thread(MotorNumber):
    while not stop_motors:
        dpiStepper.moveToRelativePositionInSteps(MotorNumber, 200, wait_to_finish_moving_flg=False)
"""


class MainScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.motor_0_speed = 0
        self.current_spiral_position = 0
        self.freqency_to_motor_speed = 0
        self.freqency = 0

        """Things that are actually happening when the MainScreen class is called
        These variables are only defined here so they can be altered later.
        s0_rotation_dierction controls the rotation direction and stays between 1 and 0.
        clock_control helps control the clock, as if the_dance() has been called the variable should update
        and cancel the clock until the value is returned to 0, which the_dance function does when it is finished running"""

    def move(self, MotorNumber, rotation_direction):
        stop_motors = False

        if dpiStepper.getAllMotorsStopped(self):
            dpiStepper.moveToRelativePositionInSteps(MotorNumber, 200, wait_to_finish_moving_flg=False)
            print("moving!")

        else:
            stop_motors = True
            dpiStepper.decelerateToAStop(MotorNumber)
            print("s0: I'm softStopped!")

    def move_both(self):
        # moves both motors and turns them off.

        #have a thread with a while True loop running this dpiStepper.moveToRelativePositionInSteps(Motor Number,  1 * steps_per_rotation, wait_to_finish_moving_flg)
        #set it up so that if an another button is pressed it stopps the thread
        if dpiStepper.getAllMotorsStopped(self):
            stop_motors = False
            for i in motors:
                dpiStepper.moveToRelativePositionInSteps(MotorNumber, 200, wait_to_finish_moving_flg=False)




    def rayne_test_thing(self):

        dpiStepper.setSpeedInStepsPerSecond(0, 10000)
        dpiStepper.setSpeedInStepsPerSecond(1, 10000)

        # have a thread with a while True loop running this dpiStepper.moveToRelativePositionInSteps(Motor Number,  1 * steps_per_rotation, wait_to_finish_moving_flg)

        sleep(5)
        #update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)

        print("slowing")
        dpiStepper.setSpeedInStepsPerSecond(0, 76000)
        sleep(4.5)


        print("speeding up")

        sleep(5)
        # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)

        dpiStepper.setSpeedInStepsPerSecond(0, 10000)
        self.current_spiral_position = 1

    def specific_control(self):
        # goes halway on spiral
        print("slowing")
        dpiStepper.setSpeedInStepsPerSecond(0, 7600)
        sleep(2.25)
        print("speeding up")
        dpiStepper.setSpeedInStepsPerSecond(0, 7600)
        self.current_spiral_position = .5

    def spiral_position_control(self, spiral_pos):
        # spiral position in fraction of the whole
        wait_time = 4.5 * (spiral_pos - self.current_spiral_position)
        if wait_time > 0:
            print("slowing")
            # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
            dpiStepper.setSpeedInStepsPerSecond(0, 7600)

            sleep(wait_time)
        else:
            print("speeding up")
            # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
            dpiStepper.setSpeedInStepsPerSecond(s0_rotation_direction, 10000 + (10000 - 7600))
            sleep(wait_time * -1)
        print("balancing speed")
        # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
        dpiStepper.setSpeedInStepsPerSecond(0, 10000)

    def amplitude_control(self, amplitude):
        # spiral position in fraction of the whole

        # replace this to show current amplitude
        current_amplitude = 0

        amount_to_move = amplitude - current_amplitude

        # calculate amount of revolutions to get to current amplitude
        amount_of_revolutions = amount_to_move * .35

        # get the amount of time to speed up or slowdown to get the correct revolutions
        wait_time = amount_of_revolutions / (
                    (self.freqency_to_motor_speed / 200) - (self.freqency_to_motor_speed - 2000))

        if amount_of_revolutions > 0:
            print("slowing")
            # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
            dpiStepper.setSpeedInStepsPerSecond(0, self.freqency_to_motor_speed - 2000)
            sleep(wait_time)


        else:
            print("speeding up")
            # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
            dpiStepper.setSpeedInStepsPerSecond(0, self.freqency_to_motor_speed + 2000)
            sleep(wait_time * -1)

        print("balancing speed")
        # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
        dpiStepper.setSpeedInStepsPerSecond(0, self.freqency_to_motor_speed)

    def freqency_increase(self, freqency):
        #sets the frequency value and adjusts to to stepper motor speed value
        self.freqency = freqency
        self.freqency_to_motor_speed = freqency * 200
        #sets the covnerted frequency value to steper motor speed to stepper motor speed
        dpiStepper.setSpeedInStepsPerSecond(0, self.freqency_to_motor_speed)

    def live_earth_quake_data(self):
        # https://manual.raspberryshake.org/udp.html use UDP on raspberry shake 1D

        print("does the thing")

    def historical_earth_quake_simulation(self):

        print("does the thing")

    def speed_change(self):

        #gets slider value
        self.motor_0_speed = self.ids.speed_slider_1.value

        #makes slider value motor speed if motor is not stopped
        if not dpiStepper.getAllMotorsStopped(self):
            # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
            dpiStepper.setSpeedInStepsPerSecond(0, self.ids.speed_slider_1.value)
            dpiStepper.setSpeedInStepsPerSecond(1, self.ids.speed_slider_1.value)

    def add_10(self):
        #math to decrease speed by 10%
        self.motor_0_speed = self.motor_0_speed + self.motor_0_speed * .1

        # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
        dpiStepper.setSpeedInStepsPerSecond(0, int(self.motor_0_speed))


    def subtract_10(self):
        #math to decrease speed by 10%
        self.motor_0_speed = self.motor_0_speed - self.motor_0_speed * .1

        # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
        dpiStepper.setSpeedInStepsPerSecond(0, int(self.motor_0_speed))

    def soft_stop(self):
        #
        # now wait for both motors to stop
        #
        #goes through motors and decelerates them to a stop
        for i in motors:
            dpiStepper.decelerateToAStop(i)

        stop_motors = True

    @staticmethod
    def exit_program():
        s0.free_all()
        cyprus.close()
        GPIO.cleanup()
        print("freedom!")
        quit()

    """
        # Adjust spiral rotating disk posistion to control amplitude
        # adjust disk rotate speed in sync to adjust freqency
        # equation for amplitude can be calculated by manually applying a gradient along the sprial
        # using that as the variable value and multiplying that by the change constant which is the
        # amount the spiral shrinks in radius with each loop with max diameter of the spiral and the
        # calibration to get the posistion we can use that to caculate the amplitude
        def update_current_position():
            # make the color gradient corespond to apmpited then convert amplitude to poition on the spiral
            self.current_position = self.color_gradient_color * self.sclar_that_realtes_color_gradient_to_position
            on
            spiral
        def sekiton_function_amplitude_control(amplitude):
            # convert desired ampliude to position on spiral and use position control to move the spiral to desired position
            self.current_amplitude = self.max_radius - (
                        self.current_position * self.radius_decrease_per_position_change)
        # increase or decrease speed to adjust the position of the disk on the spiral
        def position_control(position):
        # calculate the distance traveled during the aceleration set the aceleration value constant with the stepper motor
        # set a value that increases or decreases speed by x value befre hand and increases or decreases speed when adjusting disk position
        # using the calculated distance traveled during aceleration/deceleration and convert that to am amplitude change then set that as a minimum change in amplitudeto make a change
        # set up a y = m*(x-(a+b)) function
        # where y is time, m is the distance traveled after reaching speed, x is desired distance to position on spiral,
        # a is distance change when accelerating, and b is distance change when decelerating
        def frequency_control():
    # increase or decrease speed to increase freqency 
    """


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name='main'))

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
