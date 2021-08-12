#!/usr/bin/env python3

import time
import serial
import sys, getopt
import os.path

from os import path

import binascii


# Currently only single block programming possible. Use Renesas Flash Programmer V2 to flash multiple blocks.


StatusList = {
    0x00: "No data",
    0x04: "Command number error",
    0x05: "Parameter error",
    0x06: "Normal acknowledgment (ACK)",
    0x07: "Checksum error",
    0x0F: "Verify error",
    0x10: "Protect error", 
    0x15: "Negative acknowledgment (NACK)", 
    0x1A: "MRG10 error",
    0x1B: "MRG11 error",
    0x1C: "Write error",
    0x20: "Read error",
    0xFF: "Processing in progress (BUSY)",
}


def add_crc(b, size):
        crc = 0x00 # initial value

        for x in range(size + 1):
            crc = (crc - b[x+1]) % 256
        return crc

class Programmer(object):

    def __init__(self):
        print("NEC Programmer v1.0")
        print("written by Martin Jansson\n\n")

    def SerialInit(self, serial_port):
        print("Requesting serial port and resetting chip...")
        self.ser = serial.Serial(
            port=serial_port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)

        self.ser.isOpen()

        # Reset microcontroller with RTS line
        self.ser.setRTS(True)
        time.sleep(11/1000)
        self.ser.setRTS(False)
        time.sleep(11/1000)
        self.ser.setRTS(True)

        time.sleep(400/1000)

        self.ser.write(bytearray([0x00]))
        time.sleep(11/1000)
        self.ser.write(bytearray([0x00]))
        time.sleep(11/1000)

        return       
    
    def Receive(self):
        b = bytearray()

        b = self.ser.read(2) # read 2 bytes to determine length

        if len(b) < 2:
            print("error: Length less than 2")
            return
        b += self.ser.read(b[1]+1+1)
        # TODO: ADD CRC CHECK
        print("Status: ", StatusList[b[2]])
        print(b)
        return b[2]
    
    def Reset(self):
        b = bytearray()

        b.append(0x01)      # Start byte
        b.append(0x01)      # Length
        b.append(0x00)      # Command
        b.append(add_crc(b, b[1])) # crc
        b.append(0x03)      # Stop byte

        self.ser.write(b)
        self.Receive()

        return
    
    def BlankCheckBlock(self, block):

        start_address = block * 1024
        end_address = ((block + 1) * 1024) -1
        b = bytearray()
        print("block address from: " + str(hex(start_address)) + " to: " + str(hex(end_address)))

        b.append(0x01)   # Start byte
        b.append(0x07)   # Length
        b.append(0x32)   # Command

        b.append(start_address >> 16 & 0xFF)
        b.append(start_address >> 8 & 0xFF)
        b.append(start_address & 0xFF)
        b.append(end_address >> 16 & 0xFF)
        b.append(end_address >> 8 & 0xFF)
        b.append(end_address & 0xFF)

        b.append(add_crc(b, b[1])) # crc
        b.append(0x03) # stop byte
        self.ser.write(b)

        self.Receive()
        return
    
    def Program(self, block, file):
        if block == None:
            block = 1
        self.ProgramBlock(block,file)

        return
    
    def ProgramBlock(self, block, file):
        start_address = block * 1024
        end_address = ((block + 1) * 1024) -1
        b = bytearray()

        b.append(0x01)   # Start byte
        b.append(0x07)   # Length
        b.append(0x40)   # Command (programming)

        b.append(start_address >> 16 & 0xFF)
        b.append(start_address >> 8 & 0xFF)
        b.append(start_address & 0xFF)
        b.append(end_address >> 16 & 0xFF)
        b.append(end_address >> 8 & 0xFF)
        b.append(end_address & 0xFF)

        b.append(add_crc(b, b[1])) # crc
        b.append(0x03) # stop byte

        #print(b.hex())
        print("Sending programming command...")
        self.ser.write(b)

        status = self.Receive()
        if status != 0x06:
            print("error: Did not receive ACK, returning...")
            return

        b = bytearray()

        b.append(0x02)   # Start byte
        b.append(0x00)   # Length (00h = 256 bytes)

        with open(file, 'rb') as f:
            # read file as hex.
            hexdata = f.read().hex()
        b.extend(bytearray.fromhex(hexdata))

            
        b.append(add_crc(b, 256)) # crc
        b.append(0x03) # stop byte

        print("Sending data..")
        #print(b)
        self.ser.write(b)

        status = self.Receive()
        if status != 0x06:
            print("error: Programming failed!")
            return False
        print("Programming succeeded!")    
        return True

    def BlockErase(self, block):
        start_address = block * 1024
        end_address = ((block + 1) * 1024) -1
        b = bytearray()

        b.append(0x01)   # Start byte
        b.append(0x07)   # Length
        b.append(0x22)   # Command (block erase)

        b.append(start_address >> 16 & 0xFF)
        b.append(start_address >> 8 & 0xFF)
        b.append(start_address & 0xFF)
        b.append(end_address >> 16 & 0xFF)
        b.append(end_address >> 8 & 0xFF)
        b.append(end_address & 0xFF)

        b.append(add_crc(b, b[1])) # crc
        b.append(0x03) # stop byte

        print("Sending erase block command..")
        self.ser.write(b)

        status = self.Receive()
        if status != 0x06:
            print("error: Did not receive ACK, returning...")
            return
        print("Block erased.") 
        return


    def ChipErase(self):
        b = bytearray()

        b.append(0x01)   # Start byte
        b.append(0x01)   # Length
        b.append(0x20)   # Command (chip erase)

        b.append(add_crc(b, b[1])) # crc
        b.append(0x03) # stop byte

        print("Sending erase chip command..")
        self.ser.write(b)

        status = self.Receive()
        if status != 0x06:
            print("error: Did not receive ACK, returning...")
            return
        print("Chip erased.") 
        return
    
    def Verify(self, block, file):
        if block == None:
            block = 1
        self.VerifyBlock(block,file)

        return

    def VerifyBlock(self, block, file):
        start_address = block * 1024
        end_address = ((block + 1) * 1024) -1
        b = bytearray()

        b.append(0x01)   # Start byte
        b.append(0x07)   # Length
        b.append(0x13)   # Command (verify)

        b.append(start_address >> 16 & 0xFF)
        b.append(start_address >> 8 & 0xFF)
        b.append(start_address & 0xFF)
        b.append(end_address >> 16 & 0xFF)
        b.append(end_address >> 8 & 0xFF)
        b.append(end_address & 0xFF)

        b.append(add_crc(b, b[1])) # crc
        b.append(0x03) # stop byte

        #print(b.hex())
        print("Sending verify command..")
        self.ser.write(b)

        status = self.Receive()
        if status != 0x06:
            print("error: Did not receive ACK, returning...")
            return

        b = bytearray()

        b.append(0x02)   # Start byte
        b.append(0x00)   # Length (00h = 256 bytes)

        with open(file, 'rb') as f:
            # read file as hex.
            hexdata = f.read().hex()
        b.extend(bytearray.fromhex(hexdata))

            
        b.append(add_crc(b, 256)) # crc
        b.append(0x03) # stop byte

        print("Sending data..")
        #print(b)
        self.ser.write(b)

        status = self.Receive()
        if status != 0x06:
            print("error: Verification failed! (mismatch?)")
            return
        print("Verification OK!")    
        return


def usage():
    print("usage: -h, --help                    Print this help")
    print("       -p, --port        <port>      Specify serial port")
    print("       -b, --block       <block>     Specify specified block")
    print("       -f, --flash       <file>      Specify file to flash")
    print("       -e, --erase                   Erase chip/block")
    print("       -v, --verify      <file>      Specify file to verify")
    print("       -c, --checkempty              Check if chip/block is empty")
    return

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:f:ecb:vi:", ["help", "port=", "file=", "erase", "checkempty", "block=", "verify", "input="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    port = "COM1"
    file = None
    block = None

    flash = False
    erase = False
    verify = False
    checkEmpty = False
    for o, a in opts:
        if o in ("-v", "--verify"):
            verify = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-p", "--port"):
            port = a
            print("setting port to: ", port)
        elif o in ("-i", "--input"):
            file = a
            if not path.exists(file):
                print("missing input file.\n")
                usage()
                sys.exit(2)
        elif o in ("-b", "--block"):
            block = a
            print("specified block: ", block)
        elif o in ("-f", "--flash"):
            flash = True
        elif o in ("-e", "--erase"):
            erase = True
        elif o in ("-c", "--checkempty"):
            checkEmpty = True
        else:
            assert False, "unhandled option"
    
    if flash or erase or verify:
        if file == None and not erase:
            print("No file supplied")
            sys.exit(2)

        foo = Programmer()
        foo.SerialInit(port)
        time.sleep(500/1000) # 500 ms sleep
        foo.Reset()
        time.sleep(500/1000) # 500 ms sleep

        if erase:
            if block == None:
                print("Erasing chip...\n")
                if not foo.ChipErase():
                    foo.ser.close()
                    sys.exit(2)
            else:
                print("Erasing block", block, "...\n")
                if not foo.ChipErase():
                    foo.ser.close()
                    sys.exit(2) 
        if flash:
            print("Flashing chip...\n")
            if not foo.Program(block, file):
                foo.ser.close()
                sys.exit(2)

        if verify:
            print("Verifying chip...\n")
            if not foo.VerifyBlock(block, file):
                foo.ser.close()
                sys.exit(2)
        foo.ser.close()

    
    

if __name__ == "__main__":
   main()

