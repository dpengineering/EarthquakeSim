from time import sleep
from kivy.clock import Clock

class Oscillator:
    def __init__(self, dpiStepper, dpiComputer, microstepping, accel, speed):
        # Global vars
        self.LINEAR_OFFSET = 100
        self.dpiComputer = dpiComputer
        self.dpiStepper = dpiStepper

        # motor targets (speed in steps/sec and diff in steps)
        self.targetDiff = 0
        self.targetSpeed = 0
        self.offset = 0

        self.homing = False
        self.running = False

        # initialize, check for errors
        if not self.dpiStepper.initialize():
            print("Communication with the DPiStepper board failed.")

        # set micro stepping as set on drivers
        self.dpiStepper.setMicrostepping(microstepping)

        # set acceleration 
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(0, accel * microstepping)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(1, accel * microstepping)

        # set default speed
        self.dpiStepper.setSpeedInStepsPerSecond(0, speed * microstepping)
        self.dpiStepper.setSpeedInStepsPerSecond(1, speed * microstepping)

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
            return False, 0
        
        success, positionSpiral = self.dpiStepper.getCurrentPositionInSteps(0)
        if not success:
            return False, 0
        
        return True, positionLinear + positionSpiral

    def doorsAreClosed(self):
        """
        Returns door status, only true if both doors are closed
        Note: sensors are inverted, 0 is closed 1 is open
        :return: status
        """
        doorLeft = self.dpiComputer.readDigitalIn(self.dpiComputer.IN_CONNECTOR__IN_0)
        doorRight = self.dpiComputer.readDigitalIn(self.dpiComputer.IN_CONNECTOR__IN_1)

        return (not doorLeft) and (not doorRight)

    def loop(self):
        """
        The loop is called periodically and is responsible for updating the system:
        1. The correct frequency (aka speed)
        2. The correct amplitude (aka difference/diff)
        3. Make sure the doors haven't opened
        """
        #doorsOpen = not self.doorsAreClosed
        doorsOpen = False
        if doorsOpen:
            print("Doors open!")
            self.stop()
        elif self.homing:
            print("Homing")
            return
        elif self.running:
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
            doors = self.doorsAreClosed()

            print("Diff: " + str(diff) + " Target: " + str(self.targetDiff) + " Offset: " + str(self.offset) + " Doors: " + str(doors))

    def start(self):
        """
        Responsible for homing axis, setting default values, running motors, and starting loop, checks if doors a closed first
        """
         # Start loop
        Clock.schedule_interval(lambda dt: self.loop(), 0.01)

        self.home()

        # Set default values
        self.frequencyChange(0)
        self.amplitudeChange(0)

        # Run motors
        # self.dpiStepper.moveToRelativePositionInSteps(0, -10000000, False)
        # self.dpiStepper.moveToRelativePositionInSteps(1, 10000000, False)

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

        # Recalculate offset, as it based on speed i.e. when speed changes offset should change too
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
        self.homing = True
        self.dpiStepper.enableMotors(False) #ensures that stepper 1 can be moved freely

        # homing motor, moving together to avoid collision
        self.homeStepper(0, 1,1,3200)
        sleep(5)

        self.dpiStepper.enableMotors(True) #ensures that stepper 1 doesn't move with stepper 0

        # home spiral motor
        self.homeStepper(0, 0, -1,1600)
        sleep(5)

        # finally set home for each motor
        self.dpiStepper.setCurrentPositionInSteps(1, 0)
        self.dpiStepper.setCurrentPositionInSteps(0, 0)

        # Account for minor offset plus 180-degree rotation
        # This should only be used when assembled accordingly
        # self.dpiStepper.setSpeedInStepsPerSecond(0, 1600)
        # self.dpiStepper.setSpeedInStepsPerSecond(1, 1600)
        # self.dpiStepper.moveToRelativePositionInSteps(0, -(self.LINEAR_OFFSET + 1600), False)
        # self.dpiStepper.moveToRelativePositionInSteps(1, (self.LINEAR_OFFSET + 1600), False)
        # while not self.dpiStepper.getAllMotorsStopped():
        #      sleep(.1)

        self.homing = False

    def homeStepper(self, stepper_num, home_num, direction, speed):
        """
        Skeleton logic for homing
        """
        self.dpiStepper.setSpeedInStepsPerSecond(stepper_num, speed)

        results, __, __, homeAtHomeSwitchFlg = self.dpiStepper.getStepperStatus(stepper_num)
        if not results:
            return

        # make sure we're not already home
        if not homeAtHomeSwitchFlg:
            # move towards sensor
            self.dpiStepper.moveToRelativePositionInSteps(stepper_num, direction * 4000, False)
            self.stopAtHome(home_num)

            # move away from sensor
            self.dpiStepper.moveToRelativePositionInSteps(stepper_num, direction * -4000, False)
            self.stopAtHome(home_num)

            # move back, but slow
            self.dpiStepper.setSpeedInStepsPerSecond(stepper_num, 200)
            self.dpiStepper.moveToRelativePositionInSteps(stepper_num, direction * 4000, False)
            self.stopAtHome(home_num)