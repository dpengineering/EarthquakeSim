# Earthquake Simulator Programming/Mechanics Guide
*By Gabriel Casselman* 🤓

Welcome future software person 🫡 Your about to have the time of your life delving into the code of this project. This guide is intended to familiarize you with the structure of the code, and the mechanics of the project from a programming perspective. 🥶

    Note: I strive to build a clean perfect project, but at some point you gotta kill the puppies 🔪 🐶 and live with imperfections, keep that in mind

**Table of Contents**
- [Earthquake Simulator Programming/Mechanics Guide](#earthquake-simulator-programmingmechanics-guide)
  - [Concept](#concept)
  - [Mechanics](#mechanics)
    - [Motion](#motion)
    - [Sensors](#sensors)
  - [Homing](#homing)
  - [Manual Operation](#manual-operation)
    - [Overview](#overview)
    - [Control Loop](#control-loop)
    - [Offset Updating](#offset-updating)
  - [Earthquake Simulation](#earthquake-simulation)
    - [My Thoughts](#my-thoughts)
    - [Some notes](#some-notes)

---
## Concept 

💭 Our goal for this project was to allow participants to build structures and then simulate real past earthquakes, and see if they would stand. To accomplish this, we went through a series of designs and arrived on the disk-based `Oscillator` design that could adjust both `Frequency` and `Amplitude` of shakiness. 


`Frequency` = Speed  
`Amplitude` = Distance moving

🦀 (Crab, for fun) 

The concept is by placing an `Offset Disk` constrained by two disks, you can very the position of the shaft by changing the relative position of the two disks, while still being able to get the oscillating effect by rotating the motors together 🔗

Electronics (motors & sensors) for each `Oscillator` are connected to one `dpiStepper` board.

**In short:**
> Motors move together ➡ Oscillating effect  
> One motor moves faster ➡ Oscillating effect is decreasing  
> One motor moves slower ➡ Oscillating effect is increasing

---

## Mechanics 

### Motion
⚙ To go into more detail, each `Oscillator` primarily made with three parts:
1. `Spiral Disk`
2. `Linear Disk`
3. `Offset Disk`

Motors attach to the `Linear Disk` and `Spiral Disk`, with the `Offset Disk` braced between them. The `Linear Disk` constrains the `Offset Disk` to one axis of movement, then the `Spiral Disk` further constrains it to one position along said axis, depending on its orientation.

The `Linkage` is pressed around the `Offset Disk` and attached to a slider. As both disks spin together, the `Offset Disk` acts a as cam and causes the slider to oscillate back and forth.

🥖 (Baguette, for fun)

### Sensors

There are two proximity sensors per oscillator:
1. Positioned normal (perpendicular to tangent) of the `Linear Disk`, interfaces with a screw, when active linear disk is parallel to slider
2. Positioned facing the end of the slider, interfaces with the slider, when active slider is at maximum extension

These sensors are wired to the same `dpiStepper` board the motors are wired to so `dpiStepper` homing function can be used.

Standard switches are placed at the top of the doors and connected directly to the `dpiComputer` ports 0 and 1. **Take note** that when the doors are closed the value is 0 and 1 when open.

    Note: The mechanism was inspired by the mechanism of a three jaw chuck. Technically the spiral disk is called a scroll plate:

![Jaw Chuck Mechanism](https://cdn.dribbble.com/users/280033/screenshots/1129158/scrollchuck_animation.gif)

---

## Homing 
🏠 The homing process originally planned to use the built in `dpiStepper` homing functions, however after further consideration I realized it wouldn't work and so based on the dpiStepper source code, I remade the homing function.

The homing process is a few steps:
1. Position the `Linear Disk` by rotating it until the normal screw triggers the sensor
2. Based on how the `Offset Disk` is placed during assembly, a turn of 180° may be necessary, this would keep the `Linear Disk` parallel, but orient the `Offset Disk` towards the slider
3. Rotate the `Spiral Disk` (extending the slider) until the other sensor is triggered.  
4. Zero both motors

⛄ (Snowman, just because)

`dpiStepper` will measure of the number of steps each motor moves. By subtracting the measurements of the two motors we get the difference in position. 
> The difference in position corresponds with the relative position of the two motors, and thus the offset of the shaft or the `Amplitude` also corresponds, this is key to understand the operation of the `Oscillator` 

---

## Manual Operation 
🛠 In the final exhibit this should be one available screen, currently it is the main screen. In this mode, the shaker can be started and stopped and manual control is given over the `Amplitude` and `Frequency` of a single `Oscillator`.

### Overview

Pressing start first homes the system, then sets the motors to just run. In order to get constant motion with the `dpiStepper` system, repeated "move to" commands can't be used as it pauses between them. Instead we control by: 
1. Setting the motors to move to a very large position in order to get them to spin
2. Adjust a base speed of both motors to change `Frequency`
3. Adjust the a speed of the spiral motor for a **calculated interval**, a bit faster or slower to change `Amplitude`

🐸 (Frog, you guessed it, just for fun)

### Control Loop
In order to constantly update the speed of the motors based on sliders, a Kivy `Clock` interval is called as a **non-blocking** loop.

The sliders update the following variables `targetSpeed` and `targetDiff` asynchronously of the loop. Additionally `offset` is updated as well.

The linear motors speed is simply the `targetSpeed`. While the spiral motor speed is set to `targetSpeed + offset`.

Next we check if the actual `diff` is within an acceptable threshold (50 steps), if so we tell it to stop changing the `diff` by setting `offset` to 0 and making the motors spin in unison again.

Lastly we make sure the doors are closed and if now we stop the motion.

🍪 (Cookie, for the cookie monster)

### Offset Updating
`offset` is updated on slider changes. The direction of the `offset` (positive or negative) is adjusted only on `Amplitude` change. This is done with a simple comparison between the `targetDiff` and actual `diff`.

> Its important not to frequently update the direction, as it can introduce unpredictable results

During both `Frequency` and `Amplitude` changes, the value, but not direction of `offset` is updated. `offset` is updated proportion to `targetSpeed`. This is because at faster speeds `diff` changes faster and will hit its limits before the software could detect it.

    Note: I hate kivy. As someone who is experienced in HTML/CSS/JavaScript UI design, Kivy is painful to work with, especially the sliders
---

## Earthquake Simulation 
🗺 The simulating of real world earthquakes is up to **YOU**. However, I did some initial R&D within the `dataProcessing.ipynb` Jupyter Notebook.

Using the python library [obspy](https://docs.obspy.org/), we can pull real earthquake data and explore events, stations, and waveforms. 

### My Thoughts

1. Pull real data from and earthquake
2. Filter the data into a nice waveform
3. Take the list of samples and find local maximums
4. Find the x-distance between the maximums and use that to calculate the linear motor speed
5. Use the y-value of the second point to determine the spiral motor speed
6. After one rotation, recalculate the speeds based on the next sample

### Some notes

- Small noise and weird peaks may need to be filtered out, this is ok we can't always have perfection
- By updated exactly every revolution, the shaking will be the mostly accurate to the waveform
- Homing has to happen first, and after homing initial adjustments to diff might be necessary before the first sample
- The UI will obviously need be changed to select certain earthquakes
- The units of the data is unscaled, and will need to be mapped from its unknown units to units in steps.
