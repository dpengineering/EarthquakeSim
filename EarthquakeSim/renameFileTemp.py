def home(self, ):
    # reenable just in case
    if stepperObject.getAllMotorsStopped():
        stepperObject.enableMotors(True)

    stepperObject.setSpeedInStepsPerSecond(1, 1600)
    stepperObject.setSpeedInStepsPerSecond(0, 1600)
    # dpiStepper.moveToHomeInSteps(1, 0, 100, 3)

    results, stoppedFlg, __, homeAtHomeSwitchFlg = stepperObject.getStepperStatus(1)
    if results != True:
        return

    # make sure were not already home
    if homeAtHomeSwitchFlg != True:

        # move motors together to avoid collision
        stepperObject.moveToRelativePositionInSteps(0, -3200, False)
        stepperObject.moveToRelativePositionInSteps(1, 3200, False)

        while True:
            results, stoppedFlg, __, homeAtHomeSwitchFlg = stepperObject.getStepperStatus(1)
            if homeAtHomeSwitchFlg:
                break

        stepperObject.emergencyStop(0)
        stepperObject.emergencyStop(1)
        sleep(0.1)

        # move away from sensor
        stepperObject.moveToRelativePositionInSteps(0, 3200, False)
        stepperObject.moveToRelativePositionInSteps(1, -3200, False)

        while True:
            results, stoppedFlg, __, homeAtHomeSwitchFlg = stepperObject.getStepperStatus(1)
            if not homeAtHomeSwitchFlg:
                break

        stepperObject.emergencyStop(0)
        stepperObject.emergencyStop(1)
        sleep(0.1)

        # move back, but slow
        stepperObject.setSpeedInStepsPerSecond(0, 200)
        stepperObject.setSpeedInStepsPerSecond(1, 200)

        stepperObject.moveToRelativePositionInSteps(0, -3200, False)
        stepperObject.moveToRelativePositionInSteps(1, 3200, False)

        while True:
            results, stoppedFlg, __, homeAtHomeSwitchFlg = stepperObject.getStepperStatus(1)
            if homeAtHomeSwitchFlg:
                break

        stepperObject.emergencyStop(0)
        stepperObject.emergencyStop(1)
        sleep(0.1)

        stepperObject.moveToRelativePositionInSteps(0, -100, False)
        stepperObject.moveToRelativePositionInSteps(1, 100, False)

        sleep(1)

        stepperObject.moveToRelativePositionInSteps(1, 1600, False)
        stepperObject.moveToRelativePositionInSteps(0, -1600, False)

        sleep(1)

        while not stepperObject.getAllMotorsStopped():
            sleep(.1)

        # homing spiral motor
        results, stoppedFlg, __, homeAtHomeSwitchFlg = stepperObject.getStepperStatus(0)
        print("start of homing" + str(homeAtHomeSwitchFlg))

        if results != True:
            return

        stepperObject.setSpeedInStepsPerSecond(0, 1600)

        # make sure were not already home
        if homeAtHomeSwitchFlg != True:
            stepperObject.moveToRelativePositionInSteps(0, -3200, False)

            while True:
                results, stoppedFlg, __, homeAtHomeSwitchFlg = stepperObject.getStepperStatus(0)
                if homeAtHomeSwitchFlg:
                    break

            print("broke out of first for loop")

            stepperObject.emergencyStop(0)
            sleep(0.1)

            # move away from sensor
            stepperObject.moveToRelativePositionInSteps(0, 3200, False)

            while True:
                results, stoppedFlg, __, homeAtHomeSwitchFlg = stepperObject.getStepperStatus(0)
                if not homeAtHomeSwitchFlg:
                    break

            stepperObject.emergencyStop(0)
            sleep(0.1)

            # move back, but slow
            stepperObject.setSpeedInStepsPerSecond(0, 200)

            stepperObject.moveToRelativePositionInSteps(0, -3200, False)

            while True:
                results, stoppedFlg, __, homeAtHomeSwitchFlg = stepperObject.getStepperStatus(0)
                if homeAtHomeSwitchFlg:
                    break

            stepperObject.emergencyStop(0)
            sleep(0.1)

            # uncomment in case buffer is needed 100 steps is 3% of a rotation
            # dpiStepper.moveToRelativePositionInSteps(0, -100, False)

            stepperObject.setCurrentPositionInSteps(1, 0)
            stepperObject.setCurrentPositionInSteps(0, 0)