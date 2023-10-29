<div align=center>

![banner](./img/banner.png)

</div>

***

**Official GitHub repository for WRO USA Future Engineers team SPARK 2023. All code, documentation, and files are located here.**

***

# Contents
* [**Hardware Design**](#hardware-design)
    * [Chassis](#chassis)
    * [Power & Control](#power--control)
    * [Motors](#motors)
    * [Sensors](#sensors)
* [**Software Design**](#software-design)
* [**Photos**](#photos)
* [**In-depth Algorithm Documentation**](ALGORITHM.md)
* [**Build & Setup**](#build--setup)
    * [Parts List](#parts-list)
    * [Important Assembly Notes](#important-assembly-notes)
    * [Jetson Nano Setup](#jetson-nano-setup)
        * [ohno]
* [**SPARK Utilities**](#spark-utilities)
    * [SPARK Control Panel](#spark-control-panel)
        * [Map View](#map-view)
        * [Changing Parameters](#changing-parameters)
    * [SPARK Randomizer](#spark-randomizer)
    * [Setup](#spark-utility-setup)
* [**Team Photos**](#team-photos)
* [**Demonstration Videos**](#demonstration-videos)
* [**LiPo Battery Safety Notice**](#lipo-battery-safety-notice)

***

# Hardware Design

SPARK G2 consists of a 3D-printed chassis with off-the-shelf components mounted to it, like the motors, cameras, and controller boards. For a full component list, see [SETUP.md](./SETUP.md#parts-list). CAD models can be found in `/dist/3d-models/`, and have all been [modeled in Onshape here](https://cad.onshape.com/documents/82dd14d30b814e8846567203/w/34e1b6a4058ed5fbde8ef66a/e/47aa4028e09ec17a24a63590).

![SPARK G2 chassis with electronics in CAD software](./img/docs/cad-car.png)

***

## Chassis

The chassis consists of a lower base with vertical walls to mount the rear axle and upper platforms. It has space for the battery and an ESC (electronic speed controller) bay in the rear, and a compartment in the front for the steering mechanism. The rear axle is sourced from the Atom 2 GT12 pan car kit by Schumacher, and is mounted vertically to save space.

The electronics platforms sit on top of the chassis base, and the main platform is also a structural component that provides rigidity to the chassis. Because the electronics are on top, they are easily accessible and wiring is fairly simple. The only exceptions are the ESC, which is in the rear, and the IMU (inertial measurement unit, used for measuring angles and velocity).

| Chassis base with rear axle and steering           | Chassis base and platforms, without camera tower            |
| -------------------------------------------------- | ----------------------------------------------------------- |
| ![Lower chassis base](./img/docs/chassis-base.png) | ![Chassis with platforms](./img/docs/chassis-platforms.png) |


## Power & Control

<!-- battery to regulator -->

<!-- use what electronics to control motors? -->


## Motors

<!-- servo and drive motor -->

<!-- picked motor and servo for speed -->

## Sensors

One major physical change is the addition of a second IMX219 wide-angle camera to the front of the car. Both cameras are angled 30 degrees to either side, with a field of view of 150 degrees for each camera. The cameras are mounted on a slider to ensure the accuracy of the [distance calculations in the algorithm](./ALGORITHM.md#merge-contours--wall-lines).

![Cameras top-down](./img/docs/camera-angles.png)

SPARK G2 does not use any other sensors to percieve its environment - no LiDAR here!

<!-- cameras used for the thing -->

<!-- IMU section i guess -->

<!-- FIX IFX FIX -->

![Wiring schematic](./img/docs/wiring-schematic.png)

***

# Software Design

<!-- high-level overview - what architecture is used, part of SETUP.md i guess -->

<!-- explain the sections of the codebase because its very confusing -->

***

# Photos

|                                |                                  |
| ------------------------------ | -------------------------------- |
| ![front](./img/docs/front.jpg) | ![back](./img/docs/back.jpg)     |
| ![left](./img/docs/left.jpg)   | ![right](./img/docs/right.jpg)   |
| ![top](./img/docs/top.jpg)     | ![bottom](./img/docs/bottom.jpg) |

***

# Build & Setup

**This section is a walkthrough of the build process and setup of the controller, a Jetson Nano.**

***

## Parts List

<!-- parts list from setup.md -->

## Important Assembly Notes

<!-- mostly pulled from setup.md, clear up any misconceptions about the build process -->

## Jetson Nano Setup

<!-- again mostly from setup.md, include calibration and uploading section from old readme -->

***

# SPARK Utilities

We (team SPARK) have created our own utilities to remotely command and monitor our robot from our own computers. 

**This section covers installing and using these utilities.**

***

## SPARK Control Panel

SPARK Control Panel is our own testing and debugging software. It allows us to log detailed information about the program's internal workings and present it in a graphical format. SPARK Utilities work wirelessly, so as long as the network is configured correctly ([setup instructions](#spark-utility-setup)) SPARK Control Panel can communicate with the robot.

<div align=center>

![SPARK Control Panel](./img/docs/spark-control.png)

</div>

***

### Map View

<!-- overview of what the control panel shows in a typical monitoring session -->

***

### Changing Parameters

<!-- pull from odl readme, shorten a bit and make more concise -->

***

## SPARK Randomizer

SPARK Randomizer is a tool to use when the card-drawing, coin-flipping, headache-inducing randomizing system is too slow. SPARK Randomizer generates valid cases (as long as the right button is clicked) according to the 2023 rules.

<div align=center>

![SPARK Randomizer](./img/docs/spark-randomizer.png)

</div>

## SPARK Utility Setup

<!-- from old readme, sort of also from setup -->

***

# Team Photos

|                                     |                                 |
| ----------------------------------- | ------------------------------- |
| ![Team photo](./img/team-photo.jpg) | ![Rickroll](./img/rickroll.jpg) |

***

# Demonstration Videos

|                                                                                                                                      |                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| [![WRO 2023 Future Engineers Internationals - Demonstration Run - No Traffic Signals](./img/docs/thumbnail0.jpg)](https://youtu.be/) | [![WRO 2023 Future Engineers Internationals - Demonstration Run - Traffic Signals](./img/docs/thumbnail1.jpg)](https://youtu.be/) |

***

# LiPo Battery Safety Notice

While LiPo batteries are the safest form of portable, affordable, high density energy storage, there are still precautions to be taken when working with them. Lithium is a highly volatile element, and will react with the water vapor in the air if exposed to it.

1. **Do not** puncture, deform, short, or heat LiPo batteries above 26° C (80° F) (299.15 K)
2. Store and charge LiPos in a *fireproof container* **away** from flammable materials and water
3. **NEVER** charge a swollen or damaged battery (e.g. damaged leads, swelling of cells, puncture in wrapping)
4. **NEVER** leave a charging battery unattended
5. Only charge LiPo batteries with chargers *designed for LiPo batteries*
6. Dropping a battery can cause sufficient damage to rupture a cell and cause shorts
7. Overdischarging a LiPo battery can cause **permanent damage**

If a LiPo battery goes below its minimum voltage (stated in the manual included or 3.3v multiplied by the amount of cells connected in series) it can cause **permanent internal damage**. This damage is not visible until after further use, when it can swell, or potentially burst and **cause a FIRE**.

**Read all safety notes and instructions included with LiPo batteries before use.**

### For a more detailed LiPo safety manual there is one on [Tenergy Power](https://power.tenergy.com/lipo-safety-warnings/)