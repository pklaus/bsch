# bsch

A Python package to support my random collection of Bosch devices.
Most of this code was created by investigating the device communication
and their exported files.

Installation:

This package can be installed or upgraded from the Python Package Index
with the help of the `pip` command:

```sh
pip install --upgrade bsch[plotting]
```

For any plotting, the package relies on matplotlib/numpy.
Those packages are only installed if the "extra" plotting
is specified in square brackets after the package name.

## Bosch GTC 400 C

**IR / Thermography Camera**

Implemented features:

* Open the JPEG files saved by the IR camera and
  extract the embedded binary thermography data,
  I call this data 'thermoblob'.
* Extract metadata and the temperature matrix from
  the thermoblob.
* Export a thermography plot (tool: `gtc400c-thermogram`).
* Interactive plot of the thermography data (tool: `gtc400c-plot`).
* Create a custom blend of thermography data on top
  of the real photo (tool: `gtc400c-blend`).
* Download images via FTP when connected to the device
  via WiFi (tool: `gtc400c-ftp`).

## Planned Support

I own the laser distance measurement tool *Bosch GLM 50-27 CG*.
It has a BLE (Bluetooth Low Energy) interface and I successfully
reverse engineered the protocol. Needs some polishing though.
