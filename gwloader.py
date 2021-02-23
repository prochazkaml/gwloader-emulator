#!/usr/bin/env python3

import os
import socket
import itertools

api_version = 1

def printf(fmt, *args):
    print(fmt % (args))

def strToHex(data):
    return map(strToHex, data) if isinstance(data, list) else int(data, 16)

class OpenOcd:
    COMMAND_TOKEN = '\x1a'
    def __init__(self):
        self.tclRpcIp       = "127.0.0.1"
        self.tclRpcPort     = 6666
        self.bufferSize     = 4096

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()

    def connect(self):
        self.sock.connect((self.tclRpcIp, self.tclRpcPort))

    def disconnect(self):
        try:
            self.send("exit")
        finally:
            self.sock.close()

    def send(self, cmd):
        """Send a command string to TCL RPC. Return the result that was read."""
        data = (cmd + OpenOcd.COMMAND_TOKEN).encode("utf-8")

        self.sock.send(data)
        return self._recv()

    def _recv(self):
        """Read from the stream until the token (\x1a) was received."""
        data = bytes()
        while True:
            chunk = self.sock.recv(self.bufferSize)
            data += chunk
            if bytes(OpenOcd.COMMAND_TOKEN, encoding="utf-8") in chunk:
                break

        data = data.decode("utf-8").strip()
        data = data[:-1] # strip trailing \x1a

        return data

    def readWord(self, address):
        raw = self.send("mdw 0x%x" % address).split(": ")
        return None if (len(raw) < 2) else strToHex(raw[1])

    def readHalfWord(self, address):
        raw = self.send("mdh 0x%x" % address).split(": ")
        return None if (len(raw) < 2) else strToHex(raw[1])

    def readByte(self, address):
        raw = self.send("mdb 0x%x" % address).split(": ")
        return None if (len(raw) < 2) else strToHex(raw[1])

    def readMemory(self, wordLen, address, n):
        self.send("array unset output") # better to clear the array before
        self.send("mem2array output %d 0x%x %d" % (wordLen, address, n))

        output = [*map(int, self.send("return $output").split(" "))]
        d = dict([tuple(output[i:i + 2]) for i in range(0, len(output), 2)])

        return [d[k] for k in sorted(d.keys())]

    def readString(self, address):
        output = ""

        while 1:
            char = self.readByte(address)

            if char == 0:
                break

            output += chr(char)
            address += 1
        
        return output

    def writeWord(self, address, value):
        assert value is not None
        self.send("mww 0x%x 0x%x" % (address, value))

    def writeHalfWord(self, address, value):
        assert value is not None
        self.send("mwh 0x%x 0x%x" % (address, value))

    def writeByte(self, address, value):
        assert value is not None
        self.send("mwb 0x%x 0x%x" % (address, value))

    def writeMemory(self, wordLen, address, n, data):
        array = " ".join(["%d 0x%x" % (a, b) for a, b in enumerate(data)])

        self.send("array unset tmp") # better to clear the array before
        self.send("array set tmp { %s }" % array)
        self.send("array2mem tmp 0x%x %s %d" % (wordLen, address, n))

    def writeString(self, address, string):
        for char in string:
            self.writeByte(address, ord(char))
            address += 1
            
        self.writeByte(address, 0)
        
if __name__ == "__main__":
    with OpenOcd() as ocd:
        def ack(status):
            ocd.writeByte(0x24000000, status)
            printf("  Acknowleging with 0x%02X.", status)
        
        printf("HBLoader emulator v0.1\nWritten by Michal Prochazka, 2021.\nImplements API version %d.\n", api_version)
        
        printf("Initializing GWLoader...")
        ocd.send("init;")
        ocd.send("reset halt;")
        ocd.send("mww 0x24000000 0 4;")
        ocd.send("load_image LOADER.BIN 0x24000010 bin;")
        ocd.send("reg pc 0x24000010;")
        ocd.send("resume;")
        
        printf("Done!")
        
        while 1:
            printf("\nWaiting for command...")
        
            while 1:
                command = ocd.readByte(0x24000000);

                if command >= 0x80 or command == 0x00:
                    pass
                    
                elif command == 0x01:
                    printf("Got command: Detection check")
                    ack(0xFF)
                    
                    disk = os.statvfs('/')
                    ocd.writeByte(0x24000001, api_version)
                    ocd.writeWord(0x24000008, int(disk.f_blocks * disk.f_bsize / 512))
                    ocd.writeWord(0x2400000C, int(disk.f_bavail * disk.f_bsize / 512))
                    
                    ack(0x00)
                    break
                    
                elif command == 0x02:
                    printf("Got command: Open file")
                    ack(0xFF)

                    name = ocd.readString(ocd.readWord(0x2400000C))

                    if os.path.exists(name):
                        printf("  Opening file \"%s\".", name)
                        file = open(name, "rb")
                        
                        size = os.path.getsize(name)
                        printf("  File is %d bytes long.", size)
                        ocd.writeWord(0x24000004, size)
                        ack(0x00)
                        
                    else:
                        printf("  Error: File \"%s\" not found.", name)
                        ack(0x81)
                        
                    break                    
                
                elif command == 0x04:
                    printf("Got command: Read from file")
                    ack(0xFF)

                    reqsize = ocd.readWord(0x24000008)
                    address = ocd.readWord(0x2400000C)
                    printf("  Reading %d bytes to address 0x%08X.", reqsize, address)

                    bytesread = 0

                    output = []

                    for i in range(reqsize):
                        byte = file.read(1)

                        if not byte:
                            break

                        output += [ ord(byte) ]

                        bytesread += 1

                    ocd.writeMemory(8, address, bytesread, output)
                    printf("  Read %d bytes.", bytesread)

                    ack(0x00)
                    break
            
                elif command == 0x06:
                    printf("Got command: Close file")
                    ack(0xFF)
                    
                    file.close();
                    
                    ack(0x00)
                    break
                        
                elif command == 0x0D:
                    printf("Got command: Read current directory")
                    ack(0xFF)
                    
                    output = ""
                    files = 0
                    dirs = 0
                    
                    dirlist = os.listdir()
                    for entry in dirlist:
                        if os.path.isfile(entry):
                            output += "\x01" + entry
                            files += 1
                        else:
                            output += "\x02" + entry
                            dirs += 1
                    
                    output += "\x00"
                    
                    address = ocd.readWord(0x2400000C);
                    printf("  %d files, %d dirs.", files, dirs)
                    printf("  Writing directory list to address 0x%08X.", address)
                    
                    ocd.writeString(address, output);
                    
                    ack(0x00)
                    break
                           
                elif command == 0x0C:
                    printf("Got command: Enter directory")
                    ack(0xFF)

                    name = ocd.readString(ocd.readWord(0x2400000C))

                    printf("  Entering \"%s\".", name)
                    os.chdir(name)
                    
                    printf("  Now in \"%s\".", os.getcwd())

                    ack(0x00)
                    break
                     
                elif command == 0x7F:
                    printf("Got command: Reboot device")
                    ocd.send("reset")
                    ocd.send("exit")
                    quit()
                    
                else:
                    printf("Unknown command: %s", str(command))
                    ack(0xFE)
                    break
                    
