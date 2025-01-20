"""
Python Library for MCP4922 DAC using Raspberry Pi 3 Model B+
2 Channels, 12 Bit
Currently only supports Hardware SPI
Requires: RPi.GPIO & spidev libraries

Wiring:

MCP4922    =======>   Raspberry Pi

CS         ------->   GPIO08 Physical Pin 24 (SPI0 CE0) => Can be changed
SDI        ------->   GPIO10 Physical Pin 19 (SPI0 MOSI) => cannot be changed in hardware SPI MODE
SCK        ------->   GPIO11 Physical Pin 23 (SPI0 SCLK) => cannot be changed in hardware SPI MODE

MIT License

Copyright (c) 2017 mrwunderbar666

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

# import RPi.GPIO as GPIO
# import spidev
from machine import Pin, SPI


class MCP4922(object):
    """ Class for the Microchip MCP4922 digital to analog converter
    """
    def __init__(
        self,
        sck,
        mosi):
        """ Initialize MCP4922 device with hardware SPI
            Chipselect default value is BCM Pin 8 (Physical Pin: 24)
            Select the bus and device number. Default values are:
            Bus = 0 ; Device = 1
            If you're not sure, just leave it default
        """
    
        self.spi = SPI(0,
                  baudrate=1000000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=SPI.MSB,
                  sck=Pin(sck),
                  mosi=Pin(mosi),
                  miso=Pin(0)
                  )


    def setVoltage(self, channel, value, CS):
        """
        Regular setVoltage Function
        Select your channel 0 or 1
        Select Voltage value 0 to 1023
        """
        if channel == 0:
            output = 0x3000
        elif channel == 1:
            output = 0xb000
        else:
            raise ValueError(
                'MCP4922 Says: Wrong Channel Selected! Chose either 0 or 1!')
        if value > 1023:
            value = 1023
        if value < 0:
            value = 0
        value = value << 2
        output |= value
        buf0 = (output >> 8) & 0xff
        buf1 = output & 0xff
        msg = bytearray([buf0, buf1])
        CS.value(0)
        self.spi.write(msg)
        CS.value(1)
        return

    def setVoltage_gain(self, channel, value, CS):
        """
        The MCP4922 has the ability to output the double of the reference Voltage
        Reference Voltage is measured by the MCP4922 at pin 13 (VrefA) for Channel A and pin 11 (VrefB) for Channel B
        Note that the output voltage cannot exceed the supply voltage from pin 1 (VDD)
        """
        if channel == 0:
            output = 0x1000
        elif channel == 1:
            output = 0x9000
        else:
            raise ValueError(
                'MCP4922 Says: Wrong Channel Selected! Chose either 0 or 1!')
        if value > 1023:
            value = 1023
        if value < 0:
            value = 0
        #self.spi.open(self.spibus, self.spidevice)
        output |= value
        buf0 = (output >> 8) & 0xff
        buf1 = output & 0xff
        msg = bytearray([buf0, buf1])
        CS.value(0)
        self.spi.write(msg)
        CS.value(1)
        return

    def setVoltage_buffered(self, channel, value, CS):
        """
        Using the buffer feature of the MCP4922,
        refer to the datasheet for details
        """
        if channel == 0:
            output = 0x7000
        elif channel == 1:
            output = 0xF000
        else:
            raise ValueError(
                'MCP4922 Says: Wrong Channel Selected! Chose either 0 or 1!')
        if value > 1023:
            value = 1023
        if value < 0:
            value = 0
        #self.spi.open(self.spibus, self.spidevice)
        output |= value
        buf0 = (output >> 8) & 0xff
        buf1 = output & 0xff
        msg = bytearray([buf0, buf1])
        CS.value(0)
        self.spi.write(msg)
        CS.value(1)
        #self.spi.close
        return

    def shutdown(self, channel, CS):
        """
        Completely shutdown selected channel for power saving
        Sets the output of selected channel to 0 and 500K Ohms.
        Read Datasheet (SHDN) for details
        """
        if channel == 0:
            output = 0x2000
        elif channel == 1:
            output = 0xA000
        else:
            raise ValueError(
                'MCP4922 Says: Wrong Channel Selected! Chose either 0 or 1!')
        #self.spi.open(self.spibus, self.spidevice)
        buf0 = (output >> 8) & 0xff
        buf1 = output & 0xff
        msg = bytearray([buf0, buf1])
        CS.value(0)
        self.spi.write(msg)
        CS.value(1)
        #self.spi.close
        return
