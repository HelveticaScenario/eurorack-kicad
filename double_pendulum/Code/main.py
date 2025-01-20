from machine import Pin, SPI
from MCP4922 import MCP4922
from utime import sleep, ticks_us, ticks_diff   
import math
from micropython import const
import random
import framebuf
import gc
from array import array

# PIN definitions
SDI_DAC = 19
SCK_DAC = 18
CS_DAC1 = 17
CS_DAC2 = 16
SDA_DISPLAY = 15
SCL_DISPLAY = 14
CS_DISPLAY  = 13
DC_DISPLAY  = 12
BUTTON4     = 10
BUTTON3     = 9
RES_DISPLAY = 21
BUTTON2     = 7
BUTTON1     = 6
MUXCTL2     = 5
MUXCTL1     = 4
MUXCTL0     = 3
IN1         = 26
IN2         = 27
IN3         = 28

CS_DAC1_PIN = Pin(CS_DAC1, Pin.OUT)
CS_DAC2_PIN = Pin(CS_DAC2, Pin.OUT)

# Example usage
dac = MCP4922(
    sck = SCK_DAC,
    mosi = SDI_DAC,
)

dac.setVoltage_gain(0,1, CS_DAC1_PIN)
dac.setVoltage_gain(0,1, CS_DAC2_PIN)

dac.setVoltage(0, int(512), CS_DAC1_PIN)
dac.setVoltage(1, int(256), CS_DAC1_PIN)

dac.setVoltage(0, int(457), CS_DAC2_PIN)
dac.setVoltage(1, int(987), CS_DAC2_PIN)
    # sleep(1)   

# pin = Pin("LED", Pin.OUT)

# print("LED starts flashing...")
# while True:
#     try:
#         pin.toggle()
#         sleep(1) # sleep 1sec
#     except KeyboardInterrupt:
#         break
# pin.off()
# print("Finished.")

# A sine wave generator with phase increment based on the time diff
# between two consecutive calls to the function



def sine_wave():    
    # last_utime = utime.ticks_us() 
    phasex = 0
    phasey = 0
    # last_utime = ticks_us()
    while True:
        phasex += 0.1
        phasey += 0.11
        dac.setVoltage(0, int(512 + 512 * math.sin(phasex)))
        dac.setVoltage(1, int(512 + 512 * math.sin(phasey)))
        # sleep(0.01)
        # current_utime = ticks_us()
        # diff = ticks_diff(current_utime, last_utime)
        # if (diff > 100000000):
        #     break
        
def dp2():
    from double_pendulum import Euler_method_one_step, u_vector_to_x_y_coordinate, scale_x_y_coordinate
    deltaT = 1/30
    
    m_1 = 0.8 # mass of pendulum 1 (kg)
    l_1 = 0.5 # length of pendulum 1 (m)

    m_2 = 0.8 # mass of pendulum 2 (kg)
    l_2 = 0.5 # length of pendulum 2 (m)

    g = 9.8 # gravity (m/s)
    frictionCoefficient = 0.0 # (dimensionless)

    # theta_1_0 = random.randrange(-1,1) #Start angle of pendulum 1
    # theta_2_0 = random.randrange(-1,1) #Start angle of pendulum 2
    # thetaDot_1_0 = random.randrange(-1,1) #Start angular velocity of pendulum 1
    # thetaDot_2_0 = random.randrange(-1,1) #Start angular velocity of pendulum 2
    
    theta_1_0 = 1 #Start angle of pendulum 1
    theta_2_0 = -1 #Start angle of pendulum 2
    thetaDot_1_0 = 1 #Start angular velocity of pendulum 1
    thetaDot_2_0 = -1 #Start angular velocity of pendulum 2 
    
    u_vector = [theta_1_0, theta_2_0, thetaDot_1_0, thetaDot_2_0]
    
    while True:
        u_vector = Euler_method_one_step(u_vector, 1/120)
        # print(u_vector)
        _,_,x,y = u_vector_to_x_y_coordinate(u_vector)
        # print(x,y, l_1, l_2, 1024)
        # p = scale_x_y_coordinate(x, y, l_1, l_2, 1024)
        
        max_dac_code = 1024
        
        shifted_x = x + (l_1 + l_2)
        shifted_y = y + (l_1 + l_2)
        p = int(shifted_x / (2*(l_1 + l_2)) * max_dac_code), int(shifted_y / (2*(l_1 + l_2)) * max_dac_code)
        
        # print(p)
        scaled_x, scaled_y = p
        dac.setVoltage(0, scaled_x)
        dac.setVoltage(1, scaled_y)
        sleep(1/120)


def go():
    phase = 0
    while True:
        for i in range(0, 1023, 10):
            dac.setVoltage(0, i)
            sleep(0.01)
        for i in range(1023, 0, -10):
            dac.setVoltage(0, i)
            sleep(0.01)
        phase += 1
        if phase == 3:
            break
    

def rgb888_to_rgb565(R: int, G: int, B: int):  # Convert RGB888 to RGB565
    return const((((G & 0b00011100) << 3) + ((B & 0b11111000) >> 3) << 8) + (R & 0b11111000)+((G & 0b11100000) >> 5))

class RoundLCD(framebuf.FrameBuffer):
    def __init__(self):
        self.dc = Pin(DC_DISPLAY, Pin.OUT)
        self.cs = Pin(CS_DISPLAY, Pin.OUT)
        self.sck = Pin(SCL_DISPLAY, Pin.OUT)
        self.mosi = Pin(SDA_DISPLAY, Pin.OUT)
        self.rst = Pin(RES_DISPLAY, Pin.OUT)
        self.cs(1)
        self.spi = SPI(1, baudrate=200_000_000, polarity=0, phase=0, sck=self.sck, mosi=self.mosi,miso=None)
        self.dc(1)
        self.width = 240
        self.height = 240
        self.buffer = bytearray(self.width * self.height * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        gc.collect()
        self.init_display()
        gc.collect()
        self.blue = const(0xf800)
        self.green = const(0x001f)
        self.red = const(0x07E0)
        self.white = const(0xffff)
        self.black = const(0x0000)
        self.grey = rgb888_to_rgb565(85, 85, 85)
        self.light_grey = rgb888_to_rgb565(120, 120, 120)
        self.fill(self.white)
        self.show()
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)
        
    def write_cmd_data(self, cmd, datas):
        self.write_cmd(cmd)
        for data in datas:
            self.write_data(data)

        
    def init_display(self):
        """Initialize dispaly"""
        self.rst(1)
        sleep(0.01)
        self.rst(0)
        sleep(0.01)
        self.rst(1)
        sleep(0.05)

        self.write_cmd(0xEF)
        self.write_cmd_data(0xEB, [0x14])

        self.write_cmd(0xFE)
        self.write_cmd(0xEF)

        self.write_cmd_data(0xEB, [0x14])

        self.write_cmd_data(0x84, [0x40])

        self.write_cmd_data(0x85, [0xFF])

        self.write_cmd_data(0x86, [0xFF])

        self.write_cmd_data(0x87, [0xFF])

        self.write_cmd_data(0x88, [0x0A])

        self.write_cmd_data(0x89, [0x21])

        self.write_cmd_data(0x8A, [0x00])

        self.write_cmd_data(0x8B, [0x80])

        self.write_cmd_data(0x8C, [0x01])

        self.write_cmd_data(0x8D, [0x01])

        self.write_cmd_data(0x8E, [0xFF])

        self.write_cmd_data(0x8F, [0xFF])

        self.write_cmd_data(0xB6, [0x00, 0x20])

        # 0x08 normal config 0x58 flipped config
        self.write_cmd_data(0x36, [0x08])

        self.write_cmd_data(0x3A, [0x05])

        self.write_cmd_data(0x90, [0x08, 0x08, 0x08, 0x08])

        self.write_cmd_data(0xBD, [0x06])

        self.write_cmd_data(0xBC, [0x00])

        self.write_cmd_data(0xFF, [0x60, 0x01, 0x04])

        self.write_cmd_data(0xC3, [0x13])

        self.write_cmd_data(0xC4, [0x13])

        self.write_cmd_data(0xC9, [0x22])

        self.write_cmd_data(0xBE, [0x11])

        self.write_cmd_data(0xE1, [0x10, 0x0E])

        self.write_cmd_data(0xDF, [0x21, 0x0c, 0x02])

        self.write_cmd_data(0xF0, [0x45, 0x09, 0x08, 0x08, 0x26, 0x2A])

        self.write_cmd_data(0xF1, [0x43, 0x70, 0x72, 0x36, 0x37, 0x6F])

        self.write_cmd_data(0xF2, [0x45, 0x09, 0x08, 0x08, 0x26, 0x2A])

        self.write_cmd_data(0xF3, [0x43, 0x70, 0x72, 0x36, 0x37, 0x6F])

        self.write_cmd_data(0xED, [0x1B, 0x0B])

        self.write_cmd_data(0xAE, [0x77])

        self.write_cmd_data(0xCD, [0x63])

        self.write_cmd_data(
            0x70, [0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03])

        self.write_cmd_data(0xE8, [0x34])

        self.write_cmd_data(
            0x62, [0x18, 0x0D, 0x71, 0xED, 0x70, 0x70, 0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70])

        self.write_cmd_data(
            0x63, [0x18, 0x11, 0x71, 0xF1, 0x70, 0x70, 0x18, 0x13, 0x71, 0xF3, 0x70, 0x70])

        self.write_cmd_data(0x64, [0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07])

        self.write_cmd_data(
            0x66, [0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00])

        self.write_cmd_data(
            0x67, [0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98])

        self.write_cmd_data(0x74, [0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00])

        self.write_cmd_data(0x98, [0x3e, 0x07])

        self.write_cmd(0x35)
        self.write_cmd(0x21)

        self.write_cmd(0x11)
        sleep(0.12)
        self.write_cmd(0x29)
        sleep(0.02)

        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd_data(0x2A, [0x00, 0x00, 0x00, 0xef])

        self.write_cmd_data(0x2B, [0x00, 0x00, 0x00, 0xEF])

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
        
    def display_error(self, error_message):
        self.fill(self.white)
        error_message = error_message.split("\n")
        i = 0
        for error_line in error_message:
            self.text(error_line, 50, 120+i*10, self.grey)
            i += 1
        self.show()
        sleep(1.5)
        
        
def draw_line(lcd, x_center, y_center, length, angle, color):
    x_end = x_center + int(length * math.cos(angle))
    y_end = y_center + int(length * math.sin(angle))
    lcd.line(x_center, y_center, x_end, y_end, color)
    
def get_center_from_angle(lcd, x_center, y_center, length, angle):
    x_end = x_center + int(length * math.cos(angle))
    y_end = y_center + int(length * math.sin(angle))
    return x_end, y_end

# Get coordintes of points on a polygon that trace a line between two points with a given thickness
def get_line_points(x1, y1, x2, y2, thickness):
    # Get the angle of the line
    angle = math.atan2(y2 - y1, x2 - x1)
    # Get the length of the line
    length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    # Get the coordinates of the points
    x3 = x1 + (thickness/2) * math.sin(angle)
    y3 = y1 - (thickness/2) * math.cos(angle)
    x4 = x1 - (thickness/2) * math.sin(angle)
    y4 = y1 + (thickness/2) * math.cos(angle)
    x5 = x2 + (thickness/2) * math.sin(angle)
    y5 = y2 - (thickness/2) * math.cos(angle)
    x6 = x2 - (thickness/2) * math.sin(angle)
    y6 = y2 + (thickness/2) * math.cos(angle)
    return int(x3), int(y3), array('h', [int(x4), int(y4), int(x5), int(y5), int(x6), int(y6)])

def draw_polygon(lcd, x1, y1, x2, y2, thickness, color):
    x, y, points = get_line_points(x1, y1, x2, y2, thickness)
    lcd.poly(x, y, points, color)
    
def draw_polyline(lcd, x_center, y_center, length, angle, thickness, color):
    x_end = x_center + int(length * math.cos(angle))
    y_end = y_center + int(length * math.sin(angle))
    draw_polygon(lcd, x_center, y_center, x_end, y_end, thickness, color)

lcd = RoundLCD()

r= 0
while r < 10:
    # sine_wave()
    # go()
    # dp2()
    lcd.fill(lcd.white)
    lcd.ellipse(120, 120, 10, 10, lcd.red, True)
    draw_polyline(lcd, 120, 120, 60, r, 5, lcd.black)
    x_arm, y_arm = get_center_from_angle(lcd, 120, 120, 60, r)
    draw_polyline(lcd, x_arm, y_arm, 60, r*2, 5, lcd.black)
    lcd.show()
    sleep(0.01)
    r += 0.1