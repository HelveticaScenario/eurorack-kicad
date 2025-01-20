from machine import Pin, SPI

class MCP_DAC:
    def __init__(self, cs_pin, sck_pin=None, mosi_pin=None, hw_spi=True, max_value=255):
        self.cs = Pin(cs_pin, Pin.OUT)
        self.max_value = max_value
        self.gain = 1
        self.channel_values = [0, 0]  # For dual-channel DACs
        self.hw_spi = hw_spi

        if hw_spi:
            self.spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
        else:
            self.sck = Pin(sck_pin, Pin.OUT)
            self.mosi = Pin(mosi_pin, Pin.OUT)

    def begin(self):
        self.cs.value(1)

    def write(self, value, channel=0):
        if channel > 1:
            return False

        # Constrain value to max DAC value
        value = min(value, self.max_value)
        self.channel_values[channel] = value

        # Prepare data to send to DAC
        data = (0x1000 if channel == 0 else 0x9000)
        data |= (0x2000 if self.gain == 1 else 0)
        data |= (value << 4)

        # Send the data
        self.transfer(data)
        return True

    def set_gain(self, gain):
        if gain < 1 or gain > 2:
            return False
        self.gain = gain
        return True

    def get_gain(self):
        return self.gain

    def increment(self, channel=0):
        if self.channel_values[channel] < self.max_value:
            return self.write(self.channel_values[channel] + 1, channel)
        return False

    def decrement(self, channel=0):
        if self.channel_values[channel] > 0:
            return self.write(self.channel_values[channel] - 1, channel)
        return False

    def transfer(self, data):
        self.cs.value(0)  # Select the device (active low)
        if self.hw_spi:
            self.spi.write(bytearray([data >> 8, data & 0xFF]))
        else:
            self.software_spi_transfer(data)
        self.cs.value(1)  # Deselect the device

    def software_spi_transfer(self, data):
        # Emulate SPI with GPIOs for software SPI
        for i in range(16):
            self.mosi.value((data >> (15 - i)) & 1)
            self.sck.value(1)
            self.sck.value(0)

