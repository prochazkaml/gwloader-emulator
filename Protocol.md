# Communication protocol

The G&W communicates with the GWLoader through a 16-byte buffer at the beginning of the G&W's RAM (addresses 0x24000000-0x2400000F). The first byte is the command/status byte, through which the G&W tells the GWLoader what operation to do, and the GWLoader puts there its status.

Quick summary of ARM data units:

Unit | Size
-----|-----
Byte|8 bits
Half word|16 bits
Word|32 bits

## Command list

Command | Operation
--------|----------
0x01|Detection check
0x02|Open file for reading
0x03|Open file for writing
0x04|Read data from file
0x05|Write data to file
0x06|Close file
0x07|Delete file
0x08|Seek to start of file
0x09|Seek to end of file
0x0A|Seek by offset
0x0B|Seek to position
0x0C|Enter a directory
0x0D|Read directory
0x7E|Reset G&W, but keep GWLoader running
0x7F|Reset G&W and halt GWLoader

### 0x01: Detection check

No input parameters

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000001|Byte|Protocol version (currently 1)
0x24000008|Word|Total storage space in 512-byte sectors
0x2400000C|Word|Free space in 512-byte sectors

### 0x02: Open file for reading

Input parameters:

Address | Unit | Description
--------|------|------------
0x2400000C|Word|Pointer to null-terminated filename

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|File size (in bytes)

**TODO: Add all of the commands!**

## Status and error code list

Status code | Status meaning
------------|---------------
0x00|Operation successful
0x80|Err: No storage present
0x81|Err: File not found
0x82|Err: Not enough space
0x83|Err: I/O error
0x84|Err: A file is already opened
0xFE|Err: Unknown command
0xFF|Processing command...
