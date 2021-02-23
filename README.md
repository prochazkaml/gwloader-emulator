# gwloader-emulator

Emulates the GWLoader module using OpenOCD. Written in Python, because the OpenOCD team gladly provided example code in it.

## How to run

1) Clone this repository. The directory this repository is in will serve as the emulated SD card.

2) Clone the [bootloader](https://github.com/prochazkaml/game-and-watch-bootloader) and compile it as per the instructions, copy the resulting LOADER.BIN file from the bootloader's build directory into this directory. 

3) Run OpenOCD in a separate console. This is usually done like this:
```
openocd -f interface.cfg 2>/dev/null
```

4) Run the emulator. (Requires Python 3.)
```
./gwloader.py
```

## Command support

- [X] 0x01: Detection check
- [X] 0x02: Open file for reading
- [ ] 0x03: Open file for writing
- [X] 0x04: Read data from file
- [ ] 0x05: Write data to file
- [X] 0x06: Close file
- [ ] 0x07: Delete file
- [ ] 0x08: Seek to start of file
- [ ] 0x09: Seek to end of file
- [ ] 0x0A: Seek by offset
- [ ] 0x0B: Seek to position
- [X] 0x0C: Enter a directory
- [X] 0x0D: Read directory
- [ ] 0x7E: Reset G&W, but keep GWLoader running
- [X] 0x7F: Reset G&W and halt GWLoader

It's just enough for it to be usable with the bootloader to load homebrew. [Here](https://github.com/prochazkaml/gwloader-emulator/blob/main/Protocol.md)'s the full command specification.
