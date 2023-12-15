# フロー図

## 全体概要
```mermaid
%%{init:{'theme':'default'}}%%
flowchart TB
  Start([Start])-->B{ジョイスティック\nが接続されている}
subgraph loop1[ループ:50Hz]
joy_wait_s[[ジョイスティック接続待ち処理]]
  
end
  B-->|False| joy_wait_s[[ジョイスティック接続待ち処理]]

joy_wait_s-->joy_init["ジョイスティック初期設定\n 各フラグ初期化"]
  B-->|True| joy_init
joy_init-->main_loop[/"ジョイスティック\n 操作ループ"\]
subgraph loop2[操作ループ:50Hz]
main_loop-->can_send[["CAN処理"]]
can_send --> node_1
node_1[\"ジョイスティック\n 操作ループ"/]
end
```
**備考**

- 各フラグ初期化について
    - 各ボタンのデフォルト値をセット
    - can情報を初期化
    - デフォルトcanメッセージ：`00000000000085C9`
        - コントローラー未接続
        - LowSpeedモード
        - セルフドライビングモード
        - パーキングブレーキON
    
    ```python
    self.epb_flag = True
    self.emergency_stop_flag = False
    self.flontlight_flag = False
    self.autoware_mode_flag = False
    self.four_wheel_flag = True
    self.gear = 'N'
    self.stick_threshold = 50 # Ignore stick slopes below the threshold
            
    self.can_id = 283
    self.can_port = 'can0'
    self.can_bitrate = 500000
    self.can_message = '00000000000085C9'
    ```
## サブルーチン

### ジョイスティック接続待ち処理
```mermaid
%%{init:{'theme':'default'}}%%
flowchart TB
Start([ジョイスティック再接続処理])-->接続断時用CAN作成
接続断時用CAN作成-->joy_wait_s
subgraph loop1[接続待ちループ:50Hz]
joy_wait_s[/ジョイスティック\n 接続待ち\]-->joy_connect
default_can_send["CAN送信"]
default_can_send-->joy_connect{接続を検知した}
joy_connect-->|False|default_can_send
joy_connect-->|True|ジョイスティック判別{ジョイスティック名判別}
ジョイスティック判別-->|F710_Dモード|ドライブフラグセット
ジョイスティック判別-->|F710_Xモード|自動運転フラグセット
ジョイスティック判別-->|else|default_can_send2["デフォルトcan送信"]
default_can_send2-->joy_connect
自動運転フラグセット-->joy_wait_e
ドライブフラグセット-->joy_wait_e[\ジョイスティック\n 接続待ち/]
end
joy_wait_e --> End([End])
```
**備考**

- 接続断時CAN作成
    - 接続断時はコントローラー接続情報を変更し、それ以外は前回のCANを再送し続ける
        - Unit2付属リモコンと同一の仕様
    - クラスが保持しているCANメッセージをもとに接続切れ情報などを付与する
    - 初回接続時はデフォルトのCANメッセージが元になるため変化なし
    - CANメッセージの編集箇所
        - アクセル情報にあたる1~4byteを0で上書き
        - ジョイスティック接続情報が含まれる15byte目を編集

### can処理
```mermaid
%%{init:{'theme':'default'}}%%
flowchart TB
Start([CAN処理])-->joy_event{"ジョイスティック\n イベント検知"}
    joy_event-->|ボタンが押された|joy_event_button[[ボタン押下処理]]
    joy_event --"ボタンが離された"--> joy_event_button_up[[ボタン引上処理]]
    joy_event-->|ジョイスティックが外れた|joy_event_wait
    joy_event_button --> node_1
    joy_event_button_up --> node_1
    joy_event_wait --> node_1
    node_1 --> node_2
    joy_event_wait[["ジョイスティック再接続処理"]]
    node_1[["CANメッセージ作成"]]
    node_2["CANメッセージ送信"]

node_2 --> End([End])
```
**備考**

ジョイスティックが外れた というイベントは、基本的に上部スイッチ切り替えによるF710コントローラーの再認識を指す

つまりは自動運転モード⇔ドライブモードの切り替え

### ボタン押下処理
```mermaid
%%{init:{'theme':'default'}}%%
flowchart TB
Start([ボタン押下処理])-->joy_event{"ボタン番号判別"}
    joy_event-->|"ボタンX"|joy_event_button{"モード判別"}
    joy_event_button --"ドライブモード"--> node_1
    joy_event_button --"自動運転モード"--> node_2
    node_1["ドライブモード処理"]--> End
    node_2["自動運転モード処理"]--> End
End([End])
```


### ボタン引上処理

```mermaid
%%{init:{'theme':'default'}}%%
flowchart TB
Start([ボタン引上処理])-->joy_event{"ボタン番号判別"}
    joy_event-->|"ボタンX"|joy_event_button{"モード判別"}
    joy_event_button --"ドライブモード"--> node_1
    joy_event_button --"自動運転モード"--> node_2
    node_1["ドライブモード処理"]--> End
    node_2["自動運転モード処理"]--> End
End([End])
```


### CANメッセージ作成処理
```mermaid
%%{init:{'theme':'default'}}%%
flowchart TB
Start([CANメッセージ作成処理])
  node_1["1～4byte 速度情報CAN作成"]
  node_2["5～6byte ステア情報CAN作成"]
  node_3["7～8byte 制御情報CAN作成"]
  Start --> node_1
  node_1 --> node_2
  node_2 --> node_3
  node_3 --> End([End])
```

```mermaid
%%{init:{'theme':'default'}}%%
flowchart TB
Start([CANメッセージ作成処理])
  node_1["1～4byte 速度情報CAN作成"]
  node_2["5～6byte ステア情報CAN作成"]
  node_3["7～8byte 制御情報CAN作成"]
  Start --> node_1
  node_1 --> node_2
  node_2 --> node_3
  node_3 --> End([End])
```

**備考**

- CAN信号（[Unit2 付属リモコンCAN仕様まとめ](https://www.notion.so/Unit2-CAN-973bcac4930b4674aae39eafc00dce5c) ）
    - 1~4byte：速度情報
    - 5~6byte：ステアリング情報
    - 7~8byte：その他制御情報
    - 信号例
        - ドライブモードで1回Aボタンを押した後、左スティックを左に最大
            - `0000000018FC854E`
        - ドライブモードで1回Bボタンを押した後、右スティックを上に最大
            - `E803000000008544`
- 速度情報作成
    - ドライブモード
        - F710の右アナログスティックの上下傾きを16bit変換
        - `E8030000` ～`0000E703`
            - スティック値をint切り捨てによる丸めを行っているため、上下で最大値が1ずれる
    - 自動運転モード
        - 常に`00000000`
- ステアリング情報作成
    - ドライブモード
        - F710の左アナログスティックの左右傾き（－1000～1000）を符号付き16bit変換
        - `18FC` ～`E703`
    - 自動運転モード
        - 常に`0000`
- 制御情報作成
    - ボタン操作によってON・OFFが切り替わる各フラグ情報を参照して信号作成
    - トルクや低速モードなどはリモコンで操作しないため固定値で信号作成
    - ドライブモード・自動運転モードで参照するフラグが異なる
        - 緊急停止フラグのみ両モード共通
        - ドライブモード
            - ギア
            - ステアリングモード
            - EPB
            - フロントライト
        - 自動運転モード
            - 運転モード
    - 以下参照箇所とCAN信号の対応表
    
    | 機能名 | 対象bit | 2進数 | 信号値説明 | 備考 |
    | --- | --- | --- | --- | --- |
    | ギア | 48・49 | 0100 0101 0100 0000 | 01:D\n 10:N
    11:R | デフォルト：N |
    | ステアリングモード | 52・53 | 0100 0101 0100 0000 | 01:Four Wheel
    10:Front Wheel  | デフォルト：FourWheel |
    | トルクモード | 55 | 0100 0101 0100 0000 | 0:Speed
    1:Torque | Torque固定 |
    | 接続状態 | 56 | 0100 0101 0100 0000 | 0:Connect
    1:Disconnect | デフォルト：Disconnect |
    | 低速モード | 57 | 0100 0101 0100 0000 | 0:Normal Speed
    1:Low Speed | LowSpeed固定 |
    | アクセルロック | 58 | 0100 0101 0100 0000 | 0:Unlock
    1:Lock | Unlock固定 |
    | 駆動系 | 59 | 0100 0101 0100 0000 | 0:4WD
    1:2WD | 4WD固定 |
    | EPB | 60 | 0100 0101 0100 0000 | 0:Break
    1:Release | デフォルト：Break |
    | フロントライト | 61 | 0100 0101 0100 0000 | 0:Headlight On
    1:Headlight Off | デフォルト：Off |
    | 緊急停止 | 62 | 0100 0101 0100 0000 | 0:Emergency Stop
    1:Normal | デフォルト：Normal |
    | 運転モード | 63 | 0100 0101 0100 0000 | 0:Remote Mode
    1:Self Driving | デフォルト：SelfDriving |



