# Earthquake Simulator Programming/Mechanism Guide
*By Gabriel Casselman* 🤓

Welcome future software person 🫡 Your about to have the time of your life delving into the code of this project. This guide is intended to familarize you with the structure of the code, and the mechanics of the project from a programming perspective. 🥶

    Note: I strive to build a clean perfect project, but at some point you gotta kill the puppies 🔪 🐶 and live with imperfections
---

## The Concept 💭

Our goal for this project was to allow participants to build strucutes and then simulate real past earthquakes, and see if they would stand. To accomplish this, we went through a series of designs and arrived on the disk-based `Oscillator` design. 🦂 The concept is by placing an `Offset Disk` contrained by two disks, you can very the position of the shaft by changing the relative position of the two disks, while still being able to get the oscillating effect by rotating the motors together 🔗

**In short:**
> Motors move together ➡ Oscillating effect  
> One motor moves faster ➡ Oscillating effect decreases  
> One motor moves slower ➡ Oscillating effect increases


---

## The Mechanism ⚙

To go into more detail, each `Oscillator` primarly made with three parts:
1. `Spiral Disk`
2. `Linear Disk`
3. `Offset Disk`

Motors attach to the `Linear Disk` and `Spiral Disk`, with the `Offset Disk` braced between them. The `Linear Disk` constrains the `Offset Disk` to one axis of movement, then the `Spiral Disk` further contrains it to one position along said axis, depending on its orientation.

    Note: This mechanism was inspired by the mechanism of a three jaw chuck. Technically the spiral disk is called a scroll plate:

![Image](https://cdn.dribbble.com/users/280033/screenshots/1129158/scrollchuck_animation.gif)

---

## Homing 🏠

---

## Manual Operation 🛠

---

## Earthquake Simulation 🗺
