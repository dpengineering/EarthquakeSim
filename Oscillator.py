from dpeaDPi.DPiStepper import DPiStepper
from time import sleep
from kivy.clock import Clock

class Oscillator:
    def __init__(self, board_num, dpiComputer):
        # Global vars
        self.LINEAR_OFFSET = 100

        self.dpiComputer = dpiComputer

        # set up DPiStepper
        self.dpiStepper = DPiStepper()
        self.dpiStepper.setBoardNumber(board_num)

        # motor targets (speed in steps/sec and diff in steps)
        self.targetDiff = 0
        self.targetSpeed = 0
        self.offset = 0

        self.homingText = False
        self.doorsText = False
        self.running = False


        # initialize, check for errors
        if not self.dpiStepper.initialize():
            print("Communication with the DPiStepper board failed.")

        # set micro stepping as set on drivers
        self.dpiStepper.setMicrostepping(16)

        # set acceleration 
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(0, 20000)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(1, 20000)

        # set default speed
        self.dpiStepper.setSpeedInStepsPerSecond(0, 2560)
        self.dpiStepper.setSpeedInStepsPerSecond(1, 2560)


    def stop(self):
        """
        Abort all motion, by stopping loop (only if loop has previously been created) 
        and stopping motors
        """
        self.running = False
        if hasattr(self, "interval"):
            Clock.unschedule(self.interval)

        self.dpiStepper.emergencyStop(0)
        self.dpiStepper.emergencyStop(1)

        if self.dpiStepper.getAllMotorsStopped():
            self.dpiStepper.enableMotors(False)
        return
    
    def getDiff(self):
        """
        Calculates the difference between the two motor positions 
        by subtracting the running total of steps (given by dpiStepper) of each motor 
        Used to determine current position of offset shaft
        :return: success, difference (STEPS)
        """
        success, positionLinear = self.dpiStepper.getCurrentPositionInSteps(1)
        if not success:
            return (False, 0)
        
        success, positionSpiral = self.dpiStepper.getCurrentPositionInSteps(0)
        if not success:
            return (False, 0)
        
        return (True, positionLinear + positionSpiral)

    def getDoors(self): 
        """
        Returns door status, only true if both doors are closed
        Note: sensors are inverted, 0 is closed 1 is open
        :return: status
        """
        doorLeft = self.dpiComputer.readDigitalIn(self.dpiComputer.IN_CONNECTOR__IN_0)
        doorRight = self.dpiComputer.readDigitalIn(self.dpiComputer.IN_CONNECTOR__IN_1)

        return (not doorLeft) and (not doorRight)

    def loop(self, log):
        """
        The loop is called periodically and is responsible for updating the system:
        1. The correct frequency (aka speed)
        2. The correct amplitude (aka difference/diff)
        3. Make sure the doors haven't opened
        Passed in is a log function used for debugging
        """
        
        if self.doorsText:
            log("Door Open!")
        elif self.homingText:
            log("Homing")
        elif self.running:
            if not self.getDoors():
                self.stop()

            success, diff = self.getDiff()
            if not success:
                return

            # If difference is within threshold, reset the speed offset
            # See ReadMe for more details
            if abs(self.targetDiff - diff) < 50:
                self.offset = 0

            self.dpiStepper.setSpeedInStepsPerSecond(1, self.targetSpeed)
            self.dpiStepper.setSpeedInStepsPerSecond(0, self.targetSpeed + self.offset)
            
            # Logging used for debugging
            doors = self.getDoors()

            log("Diff: " + str(diff) + " Target: " + str(self.targetDiff) + " Offset: " + str(self.offset) + " Doors: " + str(doors))

    def start(self, log):
        """
        Responsible for homing axis, setting default values, running motors, and starting loop, checks if doors a closed first
        Passed in a log function used for debugging
        """
         # Start loop
        Clock.schedule_interval(lambda dt: self.loop(log), 0.01)

        if not self.getDoors():
            self.doorsText = True
            return
        else:
            self.doorsText = False

        self.home()

        # Set default values
        self.frequencyChange(0)
        self.amplitudeChange(0)

        # Run motors
        self.dpiStepper.moveToRelativePositionInSteps(0, -10000000, False)
        self.dpiStepper.moveToRelativePositionInSteps(1, 10000000, False)

        # Run operation loop
        self.running = True


    def frequencyChange(self, value):
        """
        Changes speed of motors
        Takes slider value, maps it, updates target speed
        Also adjusts offset according to the new speed
        """
        # Map slider value (0 - 100) to 15 - 465 RPM
        RPM = ((value / 100) * 450) + 15
        self.targetSpeed = (RPM / 60) * 200 * 16

        # Recalculate offset, as it based on speed ie. when speed changes offset should change too
        # See readme for more details
        if self.offset == 0:
            return
        elif self.offset > 0:
            self.offset = (self.targetSpeed * 0.15) + 200
        elif self.offset < 0:
            self.offset = (-self.targetSpeed * 0.15) - 200

    def amplitudeChange(self, value):
        """
        Changes amplitude of oscillator
        Takes slider value, maps it, updates target difference and offset
        """
        # Map slider value (0 - 100) to 100 - 2600 STEP OFFSET
        self.targetDiff = ((1 - (value / 100)) * 2500) + 100
        success, diff = self.getDiff()
        
        if not success:
            return
        
        # Adjust speed offset based on difference and current speed
        # See ReadMe for more details
        if self.targetDiff < diff:
            self.offset = (self.targetSpeed * 0.15) + 200
        elif self.targetDiff > diff:
            self.offset = (-self.targetSpeed * 0.15) - 200

    def stopAtHome(self, stepper_num):
        """
        Helper function for homing, moves selected motor until it hits home switch, then stops
        """
        while True:
            __, __, __, homeAtHomeSwitchFlg = self.dpiStepper.getStepperStatus(stepper_num)
            if homeAtHomeSwitchFlg:
                break

        self.dpiStepper.emergencyStop(0)
        self.dpiStepper.emergencyStop(1)
        sleep(0.1)
        return

    def home(self):
        """
        Homing routine, sets oscillator to starting position
        See ReadMe for more details
        """
        self.homingText = True
        self.dpiStepper.enableMotors(True)

        # set to moderate speed for homing
        self.dpiStepper.setSpeedInStepsPerSecond(1, 1600)
        self.dpiStepper.setSpeedInStepsPerSecond(0, 1600)

        results, stoppedFlg, __, homeAtHomeSwitchFlg = self.dpiStepper.getStepperStatus(1)
        if not results:
             return

        # make sure were not already home
        if not homeAtHomeSwitchFlg:

            # move motors together to avoid collision
            self.dpiStepper.moveToRelativePositionInSteps(0, -4000, False)
            self.dpiStepper.moveToRelativePositionInSteps(1, 4000, False)

            self.stopAtHome(1)

            # move away from sensor
            self.dpiStepper.moveToRelativePositionInSteps(0, 4000, False)
            self.dpiStepper.moveToRelativePositionInSteps(1, -4000, False)

            self.stopAtHome(1)

            # move back, but slow
            self.dpiStepper.setSpeedInStepsPerSecond(0, 200)
            self.dpiStepper.setSpeedInStepsPerSecond(1, 200)
            self.dpiStepper.moveToRelativePositionInSteps(0, -4000, False)
            self.dpiStepper.moveToRelativePositionInSteps(1, 4000, False)

            self.stopAtHome(1)

            # Account for minor offset plus 180 degree rotation
            # This should only be used when assembled accordingly
            # self.dpiStepper.setSpeedInStepsPerSecond(0, 1600)
            # self.dpiStepper.setSpeedInStepsPerSecond(1, 1600)
            # self.dpiStepper.moveToRelativePositionInSteps(0, -(self.LINEAR_OFFSET + 1600), False)
            # self.dpiStepper.moveToRelativePositionInSteps(1, (self.LINEAR_OFFSET + 1600), False)
            # while not self.dpiStepper.getAllMotorsStopped():
            #      sleep(.1)

        # homing spiral motor
        results, __, __, homeAtHomeSwitchFlg = self.dpiStepper.getStepperStatus(0)
        if not results:
            return
        
        self.dpiStepper.setSpeedInStepsPerSecond(0, 3200)

        # make sure were not already home
        if not homeAtHomeSwitchFlg:
            self.dpiStepper.moveToRelativePositionInSteps(0, -4000, False)

            self.stopAtHome(0)

            # move away from sensor
            self.dpiStepper.moveToRelativePositionInSteps(0, 4000, False)

            self.stopAtHome(0)

            # move back, but slow
            self.dpiStepper.setSpeedInStepsPerSecond(0, 200)
            self.dpiStepper.moveToRelativePositionInSteps(0, -4000, False)

            self.stopAtHome(0)

        # finally set home for each motor
        self.dpiStepper.setCurrentPositionInSteps(1, 0)
        self.dpiStepper.setCurrentPositionInSteps(0, 0)

        self.homingText = False
