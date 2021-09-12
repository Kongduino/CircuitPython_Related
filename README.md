# CircuitPython Code

I am playing with a 01Studio nRF52840 pyBoard, and writing code for myself – LoRa, sensors, etc. I am stashing all the code here.

## adafruit_rfm9x.py

This is [Adafruit's CircuitPython RFM9x library](https://github.com/adafruit/Adafruit_CircuitPython_RFM9x), for which I pushed [a PR request](https://github.com/adafruit/Adafruit_CircuitPython_RFM9x/pull/64), adding TRNG. Since the approval is pending, I am saving my version here.

## myUtils.py

Random (hopefully) helpful code: for now only `hexDump`.

## Seeed_HM330X.py

A short library for SeeedStudio's PM2.5 Laser Sensor. Basic demo code is in `test_hm330x.py`.

![pyBoard and HM3301](assets/pyBoard%20and%20HM3301.jpg)

## Minimal_LoRa.py

Work in progress. [Minimal_LoRa](https://github.com/Kongduino/BastWAN_Minimal_LoRa)-compatible basic LoRa functions for a Semtech SX1276 chip connected to pins:

  * Y3 : NSS
  * Y4 : RST
  * Y5 : SCK
  * Y7 : MISO
  * X11: MOSI
  * X12: DIO0 [unused] [for now] [we'll see about that]

## lights_control.py

Playing with LEDs and the Neopixel.