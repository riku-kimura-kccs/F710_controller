# gamepad_drive.pixkit.ai
## 概要
PIXKITをf710ゲームパッドを使って近接操縦するためのPythonコード。
## リンク
- f710ゲームパッドについて  
<https://gaming.logicool.co.jp/ja-jp/products/gamepads/f710-wireless-gamepad.html>
- Unit2用F710仕様書（Notion）  
https://www.notion.so/F710-df261f35cb054bd69f1d79a62369303b
- Unit2 付属リモコンCAN仕様まとめ（Notion）  
https://www.notion.so/Unit2-CAN-973bcac4930b4674aae39eafc00dce5c
- Unit2用F710コントローラーテスト仕様書（Notion）  
https://www.notion.so/Unit2-F710-ef10fca3e9444e038edbfc176904d171
## 起動手順
1. IPCに以下を接続
  - **F710**
  - **USB-CANbusシリアルケーブル**
  - **CANアナライザー**
2. 使用するCANポートを開ける
  - ex) ポート0の場合
    ```shell
    sudo ip link set can0 type can bitrate 500000
    sudo ifconfig 
    ```
3. controller_for_pix_unit2.pyを起動
  - 引数で信号を送るCANポートを指定
  - 指定なしの場合、CAN0に信号送信
    - ex) ```python3 controller_for_pix_unit2.py 1```
4. f710コントローラーを使って、車体を操作する。

2-3の処理はIPC起動時に処理
その他詳細(ゲームパッドの操作方法など)は前述の[手順書](https://www.notion.so/F710-df261f35cb054bd69f1d79a62369303b?d=94fb37a65e7941f99c83db011678c0e2#3916cb04e21f412480c92c40a1290022)を参照

## F710スティック値
axis 0:左スティック_X  
axis 1:左スティック_Y  
axis 2:右スティック_X  
axis 3:右スティック_Y  
 -1 ↑  
-1 ←0→ 1  
  1 ↓  

## F710ボタン対応表
コントローラー上部スイッチで別コントローラーになる  
### Dモード(リモコン操縦)
0:X (4wd)  
1:A  
2:B (emergency stop)  
3:Y (headlight)  
4:LB(D Gear)  
5:RB(epb)  
6:LT(R Gear)  
7:RT  
8:BACK  
9:START  
10:左スティック押し込み  
11:右スティック押し込み  

### Xモード（自動運転）
LTRT操作時にスティック操作のイベントとして感知される  
LT,RTがアナログスティック扱い？  
0:A  
1:B (emergency stop)  
2:X  
3:Y  
4:LB  
5:RB(autoware mode)  
6:BACK  
7:START  
8:左スティック押し込み  
9:右スティック押し込み  
10:不明  

## CAN信号メモ

### CAN 7byte
0000 0000 Speed  
0000 0001 Torque  

0100 0000 Gear D  
1000 0000 Gear N  
1100 0000 Gear R  

0000 0100 FourWheel  
0000 1000 FrontWheel  
0000 1100 wedge wheel  
### CAN 8byte
0000 0001 セルフドライビング  
0000 0010 エマージェンシー On  
0000 0100 Frontlight On  
0000 1000 EPB  
0001 0000 2WD  
0010 0000 Lock ON  
0100 0000 Low Speed  
1000 0000 Disconnect  