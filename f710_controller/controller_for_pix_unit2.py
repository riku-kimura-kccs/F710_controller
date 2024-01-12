import os
import sys
import time
import pygame
import argparse
import can
from F710 import PixUnitController , hex_2byte_invert, dec_to_signed_hex

class KccsPixUnitController(PixUnitController):


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
                #time.sleep(0.015)
                
        elif pygame.joystick.get_count() == 1:
            print('@@@ Joystick connected !')
            self.joystick = pygame.joystick.Joystick(0)
        else :
            print('@@@ More 2 Joystick connecting')
            self.joystick = pygame.joystick.Joystick(0)
        
        
        if 'Logicool Cordless RumblePad 2' in self.joystick.get_name():
            print('@@@ Drive Mode @@@')
            self.drive_mode = True
            self.drive_mode_init = True
            self.reset_drive_can_message()
        else:
            print('@@@ SelfDriving Mode @@@')
            self.drive_mode = False
        
        self.connect = True
        self.autoware_mode_flag = False
        # pygame.joystick init
        self.joystick.init()
        
        #self.left_stick_axis_y = 0
       # print(self.left_stick_axis_y)
        
        print('Joystick Name :', self.joystick.get_name())
        print('Number of buttons :', self.joystick.get_numbuttons())

    def reset_drive_can_message(self):
        print("reset")
        self.message_0th_byte = '00000000' 
        self.message_4th_byte = self.make_steering_message()
        self.message_48th_bit = '1000'
        # Steering mode.
        self.message_52th_bit = '0101'
        # Connect status. Always On
        self.message_56th_bit = '0'
        # Low speed mode. Always On
        self.message_57th_bit = '1'
        # Accel lock. Always Off
        self.message_58th_bit = '0'
        # 4WD Mode. Always On
        self.message_59th_bit = '0'
        # EPB
        self.message_60th_bit = '0' 
        # Front light
        self.message_61th_bit = '0' 
        # Emergency Stop
        self.message_62th_bit = '0' 
        # Drive mode
        self.message_63th_bit = '0'
        message = self.message_48th_bit + self.message_52th_bit + self.message_56th_bit + self.message_57th_bit + self.message_58th_bit + self.message_59th_bit + self.message_60th_bit + self.message_61th_bit + self.message_62th_bit + self.message_63th_bit

        self.message_6th_byte = format(int(message, 2), '04X')


        self.can_message = self.message_0th_byte + self.message_4th_byte + self.message_6th_byte
        self.epb_flag = "0"
        self.flontlight_flag = "0"
        self.emergency_stop_flag = "0"
        self.joystick
        print(self.joystick)

    def make_can_message(self):
        if self.drive_mode:
            # gear state reload
            # self.set_gear_state()
            # make throttle and break message
            self.message_0th_byte = self.make_throttle_and_break_message()
            # make steer message
            self.message_4th_byte = self.make_steering_message()
            # make other control signal
            self.message_6th_byte = self.make_other_control_signal_message()
            
            self.can_message = self.message_0th_byte + self.message_4th_byte + self.message_6th_byte
        else :
            # make other control signal
            self.message_6th_byte = self.make_other_control_signal_message()
            
            self.can_message = '000000000000' + self.message_6th_byte


    def make_throttle_and_break_message(self):
        self.left_stick_axis_y = int(self.joystick.get_axis(1) * 1000 )
        # check stick slopes
        if abs(self.left_stick_axis_y) > self.stick_threshold :
            if self.left_stick_axis_y > 0:
                # make throttle message
                message_0th_byte = '0000'
                # make break message
                message_2th_byte = hex_2byte_invert(dec_to_signed_hex(self.left_stick_axis_y))
            else :
                # make throttle message
                message_0th_byte = hex_2byte_invert(dec_to_signed_hex(abs(self.left_stick_axis_y)))
                # make break message
                message_2th_byte = '0000'
        else :
            # Ignore stick slopes below the threshold
            message_0th_byte = '0000'
            message_2th_byte = '0000'
        if self.drive_mode_init: 
            message_0th_byte = '0000'
            message_2th_byte = '0000'
            while self.drive_mode_init:
                print("Press any button")
                check_num = int(self.joystick.get_axis(1))
                print(check_num)
                print(pygame.event.get())
                if check_num  != -1:
                    print(int(self.joystick.get_axis(1)))
                    break
            self.drive_mode_init = False
        print("throttle="+message_0th_byte + message_2th_byte)
        print(int(self.joystick.get_axis(1) * 1000))
        return message_0th_byte + message_2th_byte
    
    def can_send(self):
        os_str = 'cansend '+ self.can_port +' '+ str(self.can_id) +'#' + self.can_message
        data_bytes = bytes.fromhex(self.can_message)
        if self.print_flag:

            bus = can.interface.Bus(bustype='virtual', channel=self.can_port, bitrate=self.can_bitrate)
            message = can.Message(arbitration_id=self.can_id, data=data_bytes)
            print(message)
            print(os_str)
        else:

            bus = can.interface.Bus(bustype='socketcan', channel=self.can_port, bitrate=self.can_bitrate)
            message = can.Message(arbitration_id=self.can_id, data=data_bytes)
            bus.send(message)

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
        print(e)
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


        #os.system(os_str)

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
    controller = KccsPixUnitController(can_port_num)
    #controller = KccsPixUnitController(can_port_num, True)
    # can接続無しでデバッグしたい場合はこっち
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
            #time.sleep(0.015)
            #schedule.every(1).seconds.do(loop,controler=controler)
    
    except( KeyboardInterrupt, SystemExit): # Exit with Ctrl-C
        print("Exit")
    except Exception as e:
        print('Unknown Error')
        print(e)

if __name__ == "__main__":
    main()
    
