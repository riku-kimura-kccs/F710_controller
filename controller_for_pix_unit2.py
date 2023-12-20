import os
import sys
import time
import pygame
import argparse
from F710 import PixUnitControler 

class KccsPixUnitController(PixUnitController):


    def reset_drive_can_message(self):
        message_0th_byte = '00000000' 
        message_4th_byte = self.make_steering_message()
        message_48th_bit = '1000'
        # Steering mode.
        message_52th_bit = '0101'
        # Connect status. Always On
        message_56th_bit = '0'
        # Low speed mode. Always On
        message_57th_bit = '1'
        # Accel lock. Always Off
        message_58th_bit = '0'
        # 4WD Mode. Always On
        message_59th_bit = '0'
        # EPB
        message_60th_bit = '0' 
        # Front light
        message_61th_bit = '0' 
        # Emergency Stop
        message_62th_bit = '0' 
        # Drive mode
        message_63th_bit = '0'
        message = message_48th_bit + message_52th_bit + message_56th_bit + message_57th_bit + message_58th_bit + message_59th_bit + message_60th_bit + message_61th_bit + message_62th_bit + message_63th_bit

        message_6th_byte = format(int(message, 2), '04X')


        self.can_message = message_0th_byte + message_4th_byte + message_6th_byte


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

    def autoware_button_action(self):
        """if self.autoware_mode_flag:
            print('Autoware Mode OFF')
            self.autoware_mode_flag = False
        else:
            print('Autoware Mode ON')
            self.autoware_mode_flag = True"""
        self.autoware_mode_flag = not self.autoware_mode_flag
        reset_drive_can_message()

        
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

def loop(controller = KccsPixUnitController):
    # イベントの取得
    for e in pygame.event.get():
        # ジョイスティックのボタンの入力
        # if e.type == pygame.locals.:
        #     print('',e)
        if e.type == pygame.locals.JOYDEVICEREMOVED:
            print('@@@ Joystick Removed',e)
            controller.waiting_joystick_connection()
        elif e.type == pygame.locals.JOYBUTTONDOWN:
            controller.button_down_action(e.button)
        elif e.type == pygame.locals.JOYBUTTONUP:
            controller.button_up_action(e.button)
        elif e.type == pygame.locals.JOYAXISMOTION:
            controller.axismotion_flag = True
            # controller.steering_action()
            # print('左スティック:', joystick.get_axis(0), joystick.get_axis(1))
            # print('右スティック:', joystick.get_axis(2), joystick.get_axis(3))
    
    
    controller.make_can_message()
    controller.can_send()
    # print(controler.can_message)
    
def get_args():
    # 準備
    parser = argparse.ArgumentParser()

    # 標準入力以外の場合
    if sys.stdin.isatty():
        parser.add_argument("can port num", help="set can port", type=int)

    parser.add_argument("--type", type=int)
    parser.add_argument("--alert", help="optional", action="store_true")

    # 結果を受ける
    args = parser.parse_args()

    return(args)


def main():
    # CLI引数受け取り
    args = sys.argv
    if 2 <= len(args):
        can_port_num = args[0]
    else:
        can_port_num = 0
    # pygameの初期化
    pygame.init()
    # ジョイスティックの初期化
    pygame.joystick.init()
    
    # ジョイスティック接続
    controller = PixUnitController(can_port_num,True)
    # controler = PixUnitControler(can_port_num)

    # can setup
    # pythonからリンク開始するよりスタートアップで起動させたほうが良さそう
    # controler.can_init()
    
    # ループ
    active = True
    try:
        while active:
            # loop
            loop(controller)
            time.sleep(0.015)
            #schedule.every(1).seconds.do(loop,controler=controler)
    
    except( KeyboardInterrupt, SystemExit): # Exit with Ctrl-C
        print("Exit")
    except Exception as e:
        print('Unknown Error')
        print(e)

if __name__ == "__main__":
    main()
    
