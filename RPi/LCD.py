import smbus
from RPi import GPIO
from time import sleep

class LCD:
    def __init__(self) -> None:
        self.__i2c = smbus.SMBus(1)
        self.__I2C_ADDR = 0x27

        self.__LCD_WIDTH = 16
        self.__LCD_CHR = 1 # mode sending data
        self.__LCD_CMD = 0 # mode sending command

        self.__LCD_LINE_1 = 0x80|0x00
        self.__LCD_LINE_2 = 0x80|0x40

        self.__LCD_BACKLIGHT = 0b1000

        self.__E_PULSE = 0.0002
        self.__E_DELAY = 0.0002

    #making lines accessible through other classes:
    # ********** property LCD_LINE_1 - (getter only) ***********
    @property
    def LCD_LINE_1(self) -> int:
        """ The LCD_LINE_1 property. """
        return self.__LCD_LINE_1
    
    # ********** property LCD_LINE_2 - (getter only) ***********
    @property
    def LCD_LINE_2(self) -> int:
        """ The LCD_LINE_2 property. """
        return self.__LCD_LINE_2
    

    def setup(self):
        # forcing the LCD into 4bit mode to use less pins
        self.send_byte_with_e_toggle(0b0011_0000) # putting in 8-bit mode 
        self.send_byte_with_e_toggle(0b0011_0000) # putting in 8-bit mode again in case previously the application was in 4-bit mode

        #now we are sure it is in 8-bit mode
        self.send_byte_with_e_toggle(0b0010_0000) # finally turning it into the 4-bit mode

        # DISPLAY ON
        self.send_instruction(0b0000_1100)
        # FUNCTION SET
        self.send_instruction(0b00101000)
        # CLEAR DISPLAY IN HOME CURSOR
        self.send_instruction(0b0000_0001)
        sleep(self.__E_DELAY)

    def send_instruction(self, value):
        ## DDRAM address: look up the document 1604a on LEHO
        self.set_data_bits(value, self.__LCD_CMD)
        sleep(0.01)

    def send_character(self, value):
        self.set_data_bits(value, self.__LCD_CHR)
        sleep(0.01)

    def set_data_bits(self, value, mode):
        MSNibble = value&0xF0
        LSNibble = (value&0x0F)<<4
        
        for nibble in (MSNibble, LSNibble):
            byte = nibble|self.__LCD_BACKLIGHT|mode
            self.send_byte_with_e_toggle(byte)
            sleep(0.001)
    
    
    def send_byte_with_e_toggle(self, bits):
        # Toggle enable
        sleep(self.__E_DELAY)
        self.__i2c.write_byte(self.__I2C_ADDR, (bits|0x4))
        sleep(self.__E_PULSE)
        self.__i2c.write_byte(self.__I2C_ADDR, (bits&0b1111_1011))
        sleep(self.__E_DELAY)

    def send_string(self, message: str):
        for character in message[:(self.__LCD_WIDTH)]:
                self.send_character(ord(character))
   

    def display_message(self, message: str, line = 0x80|0x00, align_right = False):
        if len(message)<=self.__LCD_WIDTH:
            if line == self.LCD_LINE_1 and align_right == True:
                self.send_instruction(self.align_right(message))
            elif line == self.LCD_LINE_2 and align_right == True:
                self.send_instruction(0x40|self.align_right(message))
            else:
                self.send_instruction(line)
            self.send_string(message)

        elif (len(message)>self.__LCD_WIDTH) and (len(message)<32):
            self.send_instruction(self.__LCD_LINE_1)
            self.send_string(message[:16])
            if align_right == True:
                self.send_instruction(0x40|self.align_right(message[16:]))
            else:
                self.send_instruction(self.__LCD_LINE_2)
            self.send_string(message[16:])
        
        elif len(message) > 32:
            self.display_long_message()
    
    def align_right(self, message: str):
        position = 16 - len(message)
        instruction = 0x80|position
        return instruction

    def display_long_message(self, message, line = 0x80|0x00, align_right = False):
        iterations = (len(message)//32)+1
        start = 0
        for i in range(iterations):
            stop = (i+1)*32
            self.display_message(message[start:stop-1], line, align_right)
            sleep(2)
            self.clear()
            start = stop

    def clear(self):
        self.send_instruction(0x01)

    def clear_one_line(self, line = 0x80):
        self.send_instruction(line)
        for _ in range(16):
            self.send_character(ord(' '))
