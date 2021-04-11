# bsch

A Python package to support my random collection of Bosch devices.
Most of this code was created by reverse engineering the device
communication and/or file structures.

## Bosch GTC 400 C

**IR / Thermography Camera**

Implemented features:

* Open the JPEG files saved by the IR camera and
  extract the embedded binary thermography data,
  I call this data 'thermoblob'.
* Extract metadata and the temperature matrix from
  the thermoblob.
* Plot the thermography data (tool: `gtc400c-plot`).
* Create a custom blend of thermography data on top
  of the real photo (tool: `gtc400c-blend`).
* Download images via FTP when connected to the device
  via WiFi (tool: `gtc400c-ftp`).

## Planned Support

I own the laser distance measurement tool *Bosch GLM 50-27 CG*.
It has a BLE (Bluetooth Low Energy) interface and I successfully
reverse engineered the protocol. Needs some polishing though.
