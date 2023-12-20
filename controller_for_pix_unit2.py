import os
import sys
import time
import pygame
import argparse
from F710 import PixUnitControler 


def loop(controler = PixUnitControler):
    # イベントの取得
    for e in pygame.event.get():
        # ジョイスティックのボタンの入力
        # if e.type == pygame.locals.:
        #     print('',e)
        if e.type == pygame.locals.JOYDEVICEREMOVED:
            print('@@@ Joystick Removed',e)
            controler.waiting_joystick_connection()
        elif e.type == pygame.locals.JOYBUTTONDOWN:
            controler.button_down_action(e.button)
        elif e.type == pygame.locals.JOYBUTTONUP:
            controler.button_up_action(e.button)
        elif e.type == pygame.locals.JOYAXISMOTION:
            controler.axismotion_flag = True
            # controler.steering_action()
            # print('左スティック:', joystick.get_axis(0), joystick.get_axis(1))
            # print('右スティック:', joystick.get_axis(2), joystick.get_axis(3))
    controler.make_can_message()
    controler.can_send()
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
    controler = PixUnitControler(can_port_num,True)
    # controler = PixUnitControler(can_port_num)

    # can setup
    # pythonからリンク開始するよりスタートアップで起動させたほうが良さそう
    # controler.can_init()
    
    # ループ
    active = True
    try:
        while active:
            # loop
            loop(controler)
            time.sleep(0.015)
            #schedule.every(1).seconds.do(loop,controler=controler)
    
    except( KeyboardInterrupt, SystemExit): # Exit with Ctrl-C
        print("Exit")
    except Exception as e:
        print('Unknown Error')
        print(e)

if __name__ == "__main__":
    main()
    
