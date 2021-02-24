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
0x07|Get current position in file
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

### 0x03: Open file for writing

Input parameters:

Address | Unit | Description
--------|------|------------
0x2400000C|Word|Pointer to null-terminated filename

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Current file size (in bytes)

### 0x04: Read data from file

Input parameters:

Address | Unit | Description
--------|------|------------
0x24000008|Word|Number of bytes to read
0x2400000C|Word|Pointer to data buffer

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Actual number of bytes read

### 0x05: Write data to file

Input parameters:

Address | Unit | Description
--------|------|------------
0x24000008|Word|Number of bytes to write
0x2400000C|Word|Pointer to data buffer

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Actual number of bytes written

### 0x06: Close file

No input parameters

No output parameters

### 0x07: Get current position in file

No input parameters

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Current position in file

### 0x08: Seek to start of file

No input parameters

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Current position in file


### 0x09: Seek to end of file

No input parameters

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Current position in file

### 0x0A: Seek by offset

Input parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Signed word|Offset (in bytes)

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Current position in file

### 0x0B: Seek to position

Input parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Position (in bytes)

Output parameters:

Address | Unit | Description
--------|------|------------
0x24000004|Word|Current position in file

### 0x0C: Enter a directory

Input parameters:

Address | Unit | Description
--------|------|------------
0x2400000C|Word|Pointer to null-terminated directory name

No output parameters

### 0x0D: Read directory

Input parameters:

Address | Unit | Description
--------|------|------------
0x2400000C|Word|Pointer to data buffer

No output parameters

#### Directory format

```
0x02 "0RIGINAL"
0x02 "DOOM"
0x01 "LOADER.BIN"
0x02 "RetroGo"
0x00
```

The directory list is one large null-terminated string containing multiple file names, as shown above. Note that the file names themselves are _not_ null-terminated!

Before each file name is a byte, which indicates whether the name is for a file (0x01) or a directory (0x02).

### 0x7E: Reset G&W, but keep GWLoader running

No input parameters

No output parameters

Useful for launching homebrew which can communicate with the GWLoader for file access.

### 0x7F: Reset G&W and halt GWLoader

No input parameters

No output parameters

Useful for launching homebrew which do not use the GWLoader. The module then shuts down, consuming almost no power.

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
