import os
import time
import pygame
from pygame.locals import *


class PixUnitController:
    """Operating Unit2 of PIX with F710"""
    def __init__(self,can_port_num=0,print_flag = False):
        # set various flags
        # print_flag is use to debug. If True, do not send can signal and print
        self.print_flag = print_flag
        self.epb_flag = True
        self.emergency_stop_flag = False
        self.flontlight_flag = False
        self.autoware_mode_flag = False
        self.four_wheel_flag = True
        self.gear = 'N'
        self.stick_threshold = 50 # Ignore stick slopes below the threshold
        
        self.can_id = 283
        self.can_port = 'can' + str(can_port_num)
        self.can_bitrate = 500000
        # Default CAN message
        self.can_message = '00000000000085C6'
        # connect to joystick
        self.waiting_joystick_connection()
        self.left_stick_axis_y = 0


    def waiting_joystick_connection(self):
        self.connect = False
        self.axismotion_flag = False
        # can message edit
        self.make_disconnect_can_message()
        
        """connect to joystick"""
        if pygame.joystick.get_count() == 0:
            print('@@@ Waiting joystick connect @@@')
            # 接続待ちループ
            active = True
            while active:
                # Send previus can signal.
                self.can_send()
                # print(self.can_message)
                # イベントの取得
                for e in pygame.event.get():
                    if e.type == pygame.locals.JOYDEVICEADDED:
                        print('@@@ Joystick connected !')
                        self.joystick = pygame.joystick.Joystick(0)
                        active = False
                time.sleep(0.015)
                
        elif pygame.joystick.get_count() == 1:
            print('@@@ Joystick connected !')
            self.joystick = pygame.joystick.Joystick(0)
        else :
            print('@@@ More 2 Joystick connecting')
            self.joystick = pygame.joystick.Joystick(0)
        
        
        if 'Logicool Cordless RumblePad 2' in self.joystick.get_name():
            print('@@@ Drive Mode @@@')
            self.drive_mode = True
        else:
            print('@@@ SelfDriving Mode @@@')
            self.drive_mode = False
        
        self.connect = True
        self.autoware_mode_flag = False
        # pygame.joystick init
        self.joystick.init()
        
        print('Joystick Name :', self.joystick.get_name())
        print('Number of buttons :', self.joystick.get_numbuttons())
    
    def four_wheel_process(self):
        """Set four_wheel flag.
        """
        # if self.four_wheel_flag:
        #     print('four_wheel OFF')
        #     self.four_wheel_flag = False
        # else:
        #     print('four_wheel ON')
        #     self.four_wheel_flag = True
        self.four_wheel_flag = not self.four_wheel_flag
    
    def flontlight_process(self):
        """Set flontlight flag.
        """
        # if self.flontlight_flag :
        #     print('flontlight OFF')
        #     self.flontlight_flag = False
        # else:
        #     print('flontlight ON')
        #     self.flontlight_flag = True
        self.flontlight_flag = not self.flontlight_flag
        
        
    def emergency_stop_process(self):
        """Set emergency stop flag.
        """
        """if self.emergency_stop_flag:
            print('ES OFF')
            self.emergency_stop_flag = False
        else:
            print('ES ON')
            self.emergency_stop_flag = True"""
        self.emergency_stop_flag = not self.emergency_stop_flag
    
    def epb_process(self):
        """Set epb flag.
        """
        # if self.epb_flag:
        #     print('EPB OFF')
        #     self.epb_flag = False
        # else:
        #     print('EPB ON')
        #     self.epb_flag = True
        self.epb_flag = not self.epb_flag

    def drive_gear(self):
        print('drive_gear ON')
        self.gear = 'D'
        
    def reverse_gear(self):
        print('reverse_gear ON')
        self.gear = 'R'

    def neutral_gear(self):
        print('neutral_gear ON')
        self.gear = 'N'
        
    def set_gear_state(self):
        if self.drive_mode:
            if self.joystick.get_button(4):
                self.gear = 'D'
            elif self.joystick.get_button(6):
                self.gear = 'R'
            else:
                self.gear = 'N'
        else:
            self.gear = 'N'

    def autoware_button_action(self):
        """if self.autoware_mode_flag:
            print('Autoware Mode OFF')
            self.autoware_mode_flag = False
        else:
            print('Autoware Mode ON')
            self.autoware_mode_flag = True"""
        self.autoware_mode_flag = not self.autoware_mode_flag
        
    def button_down_action(self,button_num):
        # print('ボタン'+str(button_num)+'を押した')
        if self.drive_mode:
            if button_num == 2:
                self.emergency_stop_process()
            elif button_num == 0:
                self.four_wheel_process()
            elif button_num == 3:
                self.flontlight_process()
            elif button_num == 4:
                self.drive_gear()
            elif button_num == 5:
                self.epb_flag = False
            elif button_num == 6:
                self.reverse_gear()
        else:
            if button_num == 1:
                self.emergency_stop_process()
            elif button_num == 5:
                self.autoware_button_action()
                

    def button_up_action(self,button_num):
        # print('ボタン'+str(button_num)+'を離した')
        if self.drive_mode:
            if button_num == 4:
                self.neutral_gear()
            elif button_num == 6:
                self.neutral_gear()
            elif button_num == 5:
                self.epb_flag = True

    def steering_action(self):
        if self.drive_mode:
            print('ステアリング操作:', self.joystick.get_axis(0), self.joystick.get_axis(1))
            print('アクセル操作:', self.joystick.get_axis(2), self.joystick.get_axis(3))
            # print('右スティック:', joystick.get_axis(2), joystick.get_axis(3))
    
    def make_can_message(self):
        if self.drive_mode:
            # gear state reload
            # self.set_gear_state()
            # make throttle and break message
            message_0th_byte = self.make_throttle_and_break_message()
            # make steer message
            message_4th_byte = self.make_steering_message()
            # make other control signal
            message_6th_byte = self.make_other_control_signal_message()
            
            self.can_message = message_0th_byte + message_4th_byte + message_6th_byte
        else :
            # make other control signal
            message_6th_byte = self.make_other_control_signal_message()
            
            self.can_message = '000000000000' + message_6th_byte
        
    
    def make_throttle_and_break_message(self):
        left_stick_axis_y = int(self.joystick.get_axis(1) * 1000 )
        # check stick slopes
        if abs(left_stick_axis_y) > self.stick_threshold :
            if left_stick_axis_y > 0:
                # make throttle message
                message_0th_byte = '0000'
                # make break message
                message_2th_byte = hex_2byte_invert(dec_to_signed_hex(left_stick_axis_y))
            else :
                # make throttle message
                message_0th_byte = hex_2byte_invert(dec_to_signed_hex(abs(left_stick_axis_y)))
                # make break message
                message_2th_byte = '0000'
        else :
            # Ignore stick slopes below the threshold
            message_0th_byte = '0000'
            message_2th_byte = '0000'
        return message_0th_byte + message_2th_byte

    def make_steering_message(self):
        if self.axismotion_flag:
            right_stick_axis_x = int(self.joystick.get_axis(2) * 1000 )
        else:
            right_stick_axis_x = 0
        # check stick slopes and convert to hex
        return hex_2byte_invert(dec_to_signed_hex(right_stick_axis_x if abs(right_stick_axis_x) > self.stick_threshold else 0))
    
    def make_other_control_signal_message(self):
        if self.drive_mode:
            # Gear
            if self.gear == 'D':
                message_48th_bit = '0100'
            elif self.gear == 'R':
                message_48th_bit = '1100'
            else:
                message_48th_bit = '1000'
            # Steering mode.
            message_52th_bit = '0101' if self.four_wheel_flag else '1001'
            # Connect status. Always On
            message_56th_bit = '0'
            # Low speed mode. Always On
            message_57th_bit = '1'
            # Accel lock. Always Off
            message_58th_bit = '0'
            # 4WD Mode. Always On
            message_59th_bit = '0'
            # EPB
            message_60th_bit = '0' if self.epb_flag else '1'
            # Front light
            message_61th_bit = '0' if self.flontlight_flag else '1'
            # Emergency Stop
            message_62th_bit = '0' if self.emergency_stop_flag else '1'
            # Drive mode
            message_63th_bit = '0'
            message = message_48th_bit + message_52th_bit + message_56th_bit + message_57th_bit + message_58th_bit + message_59th_bit + message_60th_bit + message_61th_bit + message_62th_bit + message_63th_bit
        else :
            message_48th_bit = '10000101010000'
            # Emergency Stop
            message_62th_bit = '0' if self.emergency_stop_flag else '1'
            # Drive mode
            message_63th_bit = '1'if self.autoware_mode_flag else '0'
            message = message_48th_bit + message_62th_bit + message_63th_bit
        
        return format(int(message, 2), '04X')
    
    def can_init(self):
        # pythonからリンク開始するよりスタートアップで起動させたほうが良さそう
        os_str = 'sudo ip link set '+ self.can_port +' type can bitrate ' + str(self.can_bitrate)
        os.system(os_str)
        os_str = 'sudo ip link '+ self.can_port +' up'
        os.system(os_str)
    
    def can_send(self):
        os_str = 'cansend '+ self.can_port +' '+ str(self.can_id) +'#' + self.can_message
        if self.print_flag:
            print(os_str)
        else:
            os.system(os_str)
    
    def make_disconnect_can_message(self):
        if not self.connect:
            if int(self.can_message[14],16) < 8:
                self.can_message = '0000' + self.can_message[4:14] + dec_to_signed_hex(int(self.can_message[14],16) + 8,1) + self.can_message[15]
            else :
                self.can_message = '0000' + self.can_message[4:]
        
def dec_to_signed_hex(dec: int,size = 4) -> str:
    """Convert decimal number to signed hexadecimal number. 
    
    Args:
        dec (int): Decimal number.
        size (int, optional): Bit length. Defaults to 4.

    Returns:
        str: Signed hexadecimal number.
    """
    if dec >= 0:
        return format(dec, "0{0}X".format(size))
    else:
        return format(int("F" * size, 16) + dec + 1, "X")

def hex_2byte_invert(hex: str) -> str:
    """Invert the byte of hex.

    Args:
        hex (str): Hexadecimal number. Ex)03E8

    Returns:
        str: Hexadecimal number with bytes inverted. Ex)E803
    """
    return hex[2:] + hex[:2]
