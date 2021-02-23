# gwloader-emulator

Emulates the GWLoader module using OpenOCD. Written in Python, because the OpenOCD team gladly provided example code in it.

## How to run

1) Clone this repository. The directory this repository is in will serve as the emulated SD card.

2) Clone the [bootloader](https://github.com/prochazkaml/game-and-watch-bootloader), compile it as per the instructions, copy the resulting LOADER.BIN file from the bootloader's build directory into this directory. 

3) Run OpenOCD in a separate console. This is usually done like this:
```
openocd -f interface.cfg 2>/dev/null
```

4) Run the emulator. (Requires Python 3.)
```
./gwloader.py
```
