from dpeaDPi.DPiStepper import DPiStepper
from time import sleep
from kivy.clock import Clock

class Oscillator:
    def __init__(self, board_num):
        # Global vars
        self.LINEAR_OFFSET = 100

        self.stopped = True
        self.nextRevSent = False

        # set up DPiStepper
        self.dpiStepper = DPiStepper()
        self.dpiStepper.setBoardNumber(board_num)

        # initialize, check for errors
        if not self.dpiStepper.initialize():
            print("Communication with the DPiStepper board failed.")

        # set micro stepping as set on drivers
        self.dpiStepper.setMicrostepping(16)

        # set acceleration
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(0, 10000)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(1, 10000)

        # set default speed
        self.dpiStepper.setSpeedInStepsPerSecond(0, 2560)
        self.dpiStepper.setSpeedInStepsPerSecond(1, 2560)

    def stop(self):
        self.stopped = True

        self.dpiStepper.emergencyStop(0)
        self.dpiStepper.emergencyStop(1)

        if self.dpiStepper.getAllMotorsStopped():
            self.dpiStepper.enableMotors(False)
        return

    def loop(self, dt):
        results, stoppedFlg, __, homeAtHomeSwitchFlg = self.dpiStepper.getStepperStatus(1)
        if not results:
            return

        # if the motor has completed one revolution, do another
        if homeAtHomeSwitchFlg:
            self.dpiStepper.moveToRelativePositionInSteps(0, -200 * 16, False)
            self.dpiStepper.moveToRelativePositionInSteps(1, 200 * 16, False)

    def start(self):
        self.home()

        RPM = 60
        self.dpiStepper.setSpeedInStepsPerSecond(0, (RPM / 60) * 200 * 16)
        self.dpiStepper.setSpeedInStepsPerSecond(1, (RPM / 60) * 200 * 16)

        self.dpiStepper.moveToRelativePositionInSteps(0, -200 * 16, False)
        self.dpiStepper.moveToRelativePositionInSteps(1, 200 * 16, False)

        Clock.schedule_interval(self.loop, 1)


    # def amplitude_control_four_point_five(self):
    #
    #     if self.dpiStepper.getAllMotorsStopped():
    #         self.dpiStepper.enableMotors(True)
    #
    #     #moves halfway
    #     self.dpiStepper.setSpeedInStepsPerSecond(0, 2000)
    #     self.dpiStepper.setSpeedInStepsPerSecond(1, 2000)
    #     sleep(5)
    #     self.dpiStepper.setSpeedInStepsPerSecond(1, 1520)
    #     sleep(4.5)
    #     self.dpiStepper.setSpeedInStepsPerSecond(0, 2000)
    #     self.dpiStepper.setSpeedInStepsPerSecond(1, 2000)
    #
    # def amplitude_control_MATH(self, amplitude):
    #
    #     if self.dpiStepper.getAllMotorsStopped():
    #         self.dpiStepper.enableMotors(True)
    #
    #     # spiral position in fraction of the whole
    #
    #     # replace this to show current amplitude
    #     current_amplitude = 0
    #
    #     amount_to_move = amplitude - current_amplitude
    #
    #     # calculate amount of revolutions to get to current amplitude
    #     amount_of_revolutions = amount_to_move * .35
    #
    #     # get the amount of time to speed up or slowdown to get the correct revolutions
    #     wait_time = amount_of_revolutions / (
    #                 (self.freqency_to_motor_speed / 400) - (self.freqency_to_motor_speed - 4000))
    #
    #     if amount_of_revolutions > 0:
    #         print("slowing")
    #         # update speed with dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
    #         dpiStepper.setSpeedInStepsPerSecond(0, self.freqency_to_motor_speed - 2000)
    #         sleep(wait_time)
    #
    # def speed_change(self, speed):
    #     self.dpiStepper.setSpeedInStepsPerSecond(0, speed)
    #     self.dpiStepper.setSpeedInStepsPerSecond(1, speed)

    def stopAtHome(self, stepper_num):
        while True:
            results, stoppedFlg, __, homeAtHomeSwitchFlg = self.dpiStepper.getStepperStatus(stepper_num)
            if homeAtHomeSwitchFlg:
                break

        self.dpiStepper.emergencyStop(0)
        self.dpiStepper.emergencyStop(1)
        sleep(0.1)
        return

    def home(self):
        # check if stopped, and then enable motors
        if self.dpiStepper.getAllMotorsStopped():
            self.dpiStepper.enableMotors(True)
        else:
            print("motor not stopped")
            return

        # set to moderate speed for homing
        self.dpiStepper.setSpeedInStepsPerSecond(1, 1600)
        self.dpiStepper.setSpeedInStepsPerSecond(0, 1600)

        results, stoppedFlg, __, homeAtHomeSwitchFlg = self.dpiStepper.getStepperStatus(1)
        if not results:
             return

        # make sure were not already home
        if not homeAtHomeSwitchFlg:

            # move motors together to avoid collision
            self.dpiStepper.moveToRelativePositionInSteps(0, -3200, False)
            self.dpiStepper.moveToRelativePositionInSteps(1, 3200, False)

            self.stopAtHome(1)

            # move away from sensor
            self.dpiStepper.moveToRelativePositionInSteps(0, 3200, False)
            self.dpiStepper.moveToRelativePositionInSteps(1, -3200, False)

            self.stopAtHome(1)

            # move back, but slow
            self.dpiStepper.setSpeedInStepsPerSecond(0, 200)
            self.dpiStepper.setSpeedInStepsPerSecond(1, 200)
            self.dpiStepper.moveToRelativePositionInSteps(0, -3200, False)
            self.dpiStepper.moveToRelativePositionInSteps(1, 3200, False)

            self.stopAtHome(1)

            # Account for minor offset plus 180 degree rotation
            self.dpiStepper.moveToRelativePositionInSteps(0, -(self.LINEAR_OFFSET + 1600), False)
            self.dpiStepper.moveToRelativePositionInSteps(1, (self.LINEAR_OFFSET + 1600), False)

            # wait for everything to finish
            while not self.dpiStepper.getAllMotorsStopped():
                 sleep(.1)

        # homing spiral motor
        results, stoppedFlg, __, homeAtHomeSwitchFlg = self.dpiStepper.getStepperStatus(0)
        if not results:
            return
        self.dpiStepper.setSpeedInStepsPerSecond(0, 1600)

        # make sure were not already home
        if not homeAtHomeSwitchFlg:
            self.dpiStepper.moveToRelativePositionInSteps(0, -3200, False)

            self.stopAtHome(0)

            # move away from sensor
            self.dpiStepper.moveToRelativePositionInSteps(0, 3200, False)

            self.stopAtHome(0)

            # move back, but slow
            self.dpiStepper.setSpeedInStepsPerSecond(0, 200)
            self.dpiStepper.moveToRelativePositionInSteps(0, -3200, False)

            self.stopAtHome(0)

            # uncomment in case buffer is needed 100 steps is 3% of a rotation
            #dpiStepper.moveToRelativePositionInSteps(0, -100, False)

        # finally set home for each motor
        self.dpiStepper.setCurrentPositionInSteps(1, 0)
        self.dpiStepper.setCurrentPositionInSteps(0, 0)
