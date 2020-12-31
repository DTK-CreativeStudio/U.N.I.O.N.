# 入退室管理システム(複数地点対応)  
これは複数地点での入退室管理に対応したシステムです。  

## 機能一覧  
入退室システムを置いている部屋をそれぞれROOM A、ROOM Bとおきます。
- 関大の学生証と交通系ICカードで入退室管理ができます。もちろんApple PayやGoogle PayのSuicaやPasmoにも対応しています。入退室した際はslackに通知がきます。
- 学生証や交通系IC登録の際にスマートフォンのブラウザが使用できます。
- BのPCがAのPCのデータベースにアクセスすることで実現しています。これにより、たとえばAで入室し、退室手続きを行わずにBの部屋に入室手続きを行った場合、Aの入退室状況を自動的に退室扱いにしてくれます。逆も同様です。
- 退室手続きを行わずに部屋を出てしまった時、強制退室モードにより一斉に退室扱いとすることができます。
- スマートフォンで登録する場合、ダークモードとライトモードが選択できます。
- 学生証を登録すると、交通系ICが登録できます。  

## 使い方  
PC(linux)にPasoriを接続し、下の[プログラムの実行方法](#HUBのプログラム実行方法)のコードを入力し、起動するだけです。  
## 入退室  
登録した学生証or交通系ICをPasoriにかざしてください。  
slackに通知が送られます。  

## 登録  
### 学生証  
スマホで、ブラウザを開き"ホストのIPアドレス:5000"にアクセスしてください。テキストボックスにお好きなニックネームを入力してください。そして、登録に使用している部屋のボタンを押してください。すると、データベースにあなたと学生証、ニックネームが登録されます。  

### 交通系IC  
テキストボックスに登録したニックネームを入力し、登録に使用している部屋のボタンを押してください。すると、その交通系ICがデータベースに登録されているあなたのデータと紐付けられます。  

## 変更  
ニックネームの変更の際は、新しいニックネームをテキストボックスに入力し、登録に使用している部屋のボタンを押してください。そこでこれまでに登録した事のある学生証か交通系ICをかざしてください。  

## システム体系  
システムは以下のようにHUBとSUBから成立しています。  

|ベース|処理内容|
|:----|:--------|
|**HUB**|入退室のデータベースサーバ<br>入退室の処理を行うPythonスクリプト<br>入退室システムをユーザがGUIで操作するためのウェブサーバ|
|**SUB**|入退室の処理を行うPythonスクリプト|    

## HUBのプログラム実行方法  
`docker-compose -f ./docker-compose-hub.yaml up --build`

## SUBのプログラム実行方法  
`docker-compose -f ./docker-compose-sub.yaml up --build`

## 使用しているもの  
- Docker  
- MySQL  
- Python  
- Flask  
- Slack
- NFC技術
　(Pasori(RC-S380)、関大の学生証、交通系IC(Apple Pay、Google Pay含む))  

※ここではDockerやMySQLについて、操作方法などはあまり解説していません。  

以下でこのプログラムの仕組みを説明します。  
## 根本的な仕組み   
ディレクトリ構造は以下のようになっています。    
```
.   
├── LICENSE     
├── README.md      
├── docker-compose-hub.yaml     
├── docker-compose-sub.yaml     
├── code        
│   ├── main.py   
│   ├── tools.py     
│   ├── ui.py       
│   ├── static      
│   │   ├── Regist.css      
│   │   └── Result.css      
│   └── templates       
│       ├── Regist.html     
│       └── Result.html     
├── env     
│   ├── mysql.env       
│   └── python.env      
├── mysql       
│   └── 省略        
├── python      
│   ├── Dockerfile      
│   └── requirements.txt        
├── others       
│   ├── Flowchart    
│   │   └── 省略  
│   └── ubuntu_setup.sh         
└── sql     
``` 

以下が各ディレクトリの解説です。    
|ディレクトリ名|内容|
|:----|:--------|
|`docker-compose-hub.yaml`<br>`docker-compose-sub.yaml`|Dockerで動かす際に用いる仮想環境定義ファイル。|
|`code/main.py`|入退室管理システムにおいて、カードのスキャンやデータベースの操作をするプログラム。|
|`code/ui.py`<br>`code/static/`<br>`code/templates/`|入退室システムの登録を行うためのGUIを実現するプログラム。|
|`env`|dockerのそれぞれの仮装環境の環境変数を記述するファイル。|
|`mysql/`<br>`sql/`|データベース用のファイル。|
|`python`|dockerのPython環境における定義ファイル。|
|`others`|PC自体の環境を整えるためのファイルやフローチャートの入ったディレクトリがある。|   

## データベースの内容について  
データベースは`io`を使用しています。  
### student_tb  
+--+---------+-----------------------+------------------------+-------+-----------+------------+-----------+  
| ID | UNIV_ID          | TRANSPORTATION_ID1 | TRANSPORTATION_ID2 | NAME             | NICKNAME         | STATUS_A | STATUS_B |  
+--+---------+-----------------------+------------------------+-------+-----------+------------+-----------+  

|カラム名|内容|
|:----|:--------|
|ID|これは主キーで、一意性かつ不変性のある番号が個人に割り振られます。|
|UNIV_ID|学生証に保存されている16桁のIDです。|
|TRANSPORTATION_ID1|交通系ICに登録されている16桁のIDです。|
|TRANSPORTATION_ID2|交通系ICに登録されている16桁のIDです。|
|NAME|学生証に保存されている本名です。|
|NICKNAME|登録の際に設定したニックネームが保存される。|
|STATUS_A|ROOM Aの入室状況です。|
|STATUS_B|ROOM Bの入室状況です。|  


### utila_tb / utilb_tb  
+----+------+----------+  
| flag | result | nickname |  
+----+------+----------+  

|カラム名|内容|
|:----|:--------|
|flag|カード登録の際に使うフラグ変数です。|
|result|カードとニックネームの登録ができたかどうかの結果を格納します。|
|nickname|ニックネームの登録の際に一時的に入力されたニックネームを格納します。|

## PCでこのプログラムを動かすまで   
1. linux(ubuntu)PCを用意してください。
2. `sudo apt install git`と入力してください。gitが入ります。
3. `sudo git clone https://github.com/DTK-CreativeStudio/DTK_IO`と入力してください。ここでユーザ名。パスワードが求められるので、それぞれ入力してください。
4. `cd DTK_IO/others`でディレクトリに移動してください。
5. `./ubuntu_setup.sh`と実行してください。そうすればdocker、docker compose、vs code、MySQL clientなどが入ります。終了し次第自動的に再起動が始まるので、ログインしてください・
6. vs codeが入っていると思うので、それを起動し、recommended extenstionsをインストールしてください。
7. 上のプログラム実行方法のコマンドを実行してください。そうすれば自動的に環境が構築され、プログラムが走ります。

## 大まかな全体の仕組み  
### 入退室モードの時  
初めにpasoriを通して学生証か交通系ICがかざされたことを検出します。そこからデータベースに登録されているIDを検出し、そのIDに紐づけられたSTATUS_AもしくはSTATUS_Bを変更することで、実現しています。その際にslackに通知も行います。  

### 登録モードの時  
初めにブラウザでニックネームを登録してもらいます。入力後学生証か交通系ICをかざしてもらうことで、それらに紐づけられたニックネームを登録、更新します。その際にslackに通知を行います。

## ちょっぴり具体的な全体の仕組み  
### 入退室モード   
<div align="center">  
<img src="https://github.com/DTK-CreativeStudio/U.N.I.O.N./blob/master/others/Flowchart/process.png" alt="process" title="process">  
<br>  
関数process  
<br>  
</div>  
初めに関数processについて解説します。これは入退室管理においてベースになっている仕組みで、基本的にはカードが正しく読み取られると、入退室の手続きを行うIO関数を発動します。ですが、もしそれが直近7秒以内に検出されたことのあるIDだったら、読み取りを無効にします。  

<div align="center">  
<img src="https://github.com/DTK-CreativeStudio/U.N.I.O.N./blob/master/others/Flowchart/io.png" alt="io" title="io">  
<br>  
関数IO
<br>    
</div>  

この関数はその人がデータベース上で割り当てられているIDと部屋(room aかroom b)が引数になります。<br>初めにそのIDに関する情報を取得します。そこからその人の部屋の入室状況を確認します、そこでデータベースの入退室状況を反転(IN→OUT、OUT→IN)させます。それからslack通知のための下準備としてニックネームの取得などを行い、入退室の状況に合わせて送るメッセージを変えます。<br>もしその部屋の入退室状況が0人から1人になったら「HI Bestie」、入退室状況が0人になったら「BYE Bestie」とslackに送ります。<br>ここで重要なのが、入退室状況を反転させる時、もう一方の部屋のSTATUSがINであれば、それを反転させるためにIO関数を内部で再帰的に発動させます。この時の引数はそのIDともう一方の部屋です。  

<div align="center">  
<img src="https://github.com/DTK-CreativeStudio/U.N.I.O.N./blob/master/others/Flowchart/read.png" alt="read" title="read">  
<br>  
関数read  
<br>  
</div>  

ここでは学生証、もしくは交通系ICカードの同時読み取りを実現しています。とは言っても初めに学生証を読み取り、次に交通系ICモードに読み取り方式を変更することで、そう見せかけています。
<br>学生証が読み取れたら次のステップにいきます。もし`utila_tb`、もしくは`utilb_tb`の`flag`が1であれば関数processに移り、0であればその学生証の登録モードに移ります。登録モードについては後述します。
<br>交通系ICについても同様です。
</div>  

### 登録モード  

<div align="center">  
<!-- <img src="https://github.com/DTK-CreativeStudio/DTK_IO/blob/master/others/Flowchart/register.png" alt="register" title="register">   -->
<img src="https://github.com/DTK-CreativeStudio/U.N.I.O.N./blob/master/others/Flowchart/register.png" alt="register" title="register">  
<br>  
登録モード全体  
<br>  
</div>  

#### 学生証  

初めにブラウザで登録したいニックネームと、登録に使用している部屋がどこかを(ボタンを押してもらうことで)取得します。pasoriから読み取られた学生証のデータをデータベースと照合してこれまでに登録されてことがあるか否かを判別します。  
もし登録されたことがない学生証であれば、その入力されたニックネームと共にデータベースに登録します。一方でもう登録されたことのある学生証であれば、その学生証に紐付けられたニックネームを入力されたニックネームに変更します。  

#### 交通系IC   
学生証と同様に初めにブラウザで登録したいニックネームと登録に使用している部屋がどこかを(ボタンを押してもらうことで)取得します。pasoriから読み取られた交通系ICのidmをデータベースと照合してこれまでに登録されてことがあるか否かを判別します。  
もし登録されたことがない交通系ICであれば、その入力されたニックネーム(に紐づけられているID)に紐付けてデータベースに登録します。一方でもう登録されたことのある交通系ICであれば、その交通系ICに紐付けられたニックネームを入力されたニックネームに変更します。  


## その他   
### envディレクトリについて  
#### mysql.env  
|環境変数名|内容|
|:----|:--------|
|MYSQL_ROOT_PASSWORD|データベースにアクセスするためのパスワード|  

#### python.env  
|環境変数名|内容|
|:----|:--------|
|IP_ADDRESS1|データベースのコンテナIPアドレス|
|IP_ADDRESS2|データベースのコンテナIPアドレス(予備)|
|IP_ADDRESS3|HUBのホストPCのIPアドレス。SUBからHUBに接続する為に必要です|
|MYSQL_ROOT_PASSWORD|データベースにアクセスするためのパスワード|
|MAIN1|ROOM Aのincoming webhook(メイン用)|
|MAIN2|ROOM Bのincoming webhook(メイン用)|
|TEST1|ROOM Aのincoming webhook(テスト用)|
|TEST2|ROOM Bのincoming webhook(テスト用)|  

### mysqlへのアクセスの方法  
複数方法があります。  
パスワードは`Tatooine`です。`env`ディレクトリにデータベースのパスワードを定義しているので、パスワードを変更する場合はそこを変更してください。  
#### dockerコンテナに入ってからアクセス(そのホストPC限定)  
`docker exec -it io_database /bin/bash`  
`mysql -u root`  
#### ホストPCのターミナルから直接アクセス(そのホストPC限定)  
`mysql -u root -h dockerコンテナのIPアドレス -p`

### 命名の由来  
このシステムの名前はU.N.I.O.N.です。これは複数カ所の入退室システムを一つにするシステムであり、今よりもこのサークルが融和し、団結してほしいという想いからこの名前にしました。  
また、このシステムの正式名称は「i know U eNter It Or Not system (私はあなたが部屋に入ってるか入ってないか知ってるゾ システム)」  

### 交通系ICについて  
このシステムは交通系ICで認証する際にidmを使用していますが、これは調査したところ、ソニーが発行されたNFCカードに一意的に付けているナンバーらしいです。これは偽造可能なので、ドアのロック解除などのセキュリティーの求められるところでは使用しない方が良いのですが、今回は入退室状況をslackに通知するだけなので、セキュリティは大丈夫です。なお、改札などの決済の際にはidmのような静的認証ではなく、動的認証を使っているので安全とのことです。  

### 謝辞    
入退室管理システムを発案、構築して下さった先輩方    
入退室管理システムをGUIに対応させてくれた同期

## 参照     
#### データベース系の参照  
[MySQLでのSQLコードのまとめ](https://qiita.com/y_h_tomo/items/44a932ba9a6b2dcce1e6)

[MYSQL PRIMARY KEYの追加と削除](https://variable.jp/2009/07/21/mysql-primary-keyの追加と削除/)

[MySQLでカラムの順番を変更する](https://qiita.com/sayama0402/items/2fedb2f4ce8ab5da1438)

[mysqlのテーブルに後からAUTO INCREMENTをDBの最前列に追加するとき](https://satoru-net.hateblo.jp/entry/20130204/1359946271)

[主キーの設定・削除、AUTO_ICREMENT属性の設定](https://phpjavascriptroom.com/?t=mysql&p=autoincerment)

[Python+MySQL で dict で結果が返ってくるカーソルを使う](https://qiita.com/umezawatakeshi/items/7d7f4f8299e8d0d2db86)

[USBIP系の参照](http://ktkr3d.github.io/2020/07/06/USB-support-to-WSL2/)

[How to setup and use USB/IP](https://developer.ridgerun.com/wiki/index.php?title=How_to_setup_and_use_USB/IP)

[主キー駆動設計](https://qiita.com/wanko5296/items/a96bdeccc250f7c18cee)  


#### NFC関係  
[ICカードについて　- UID・Idmリスト -](https://www.kenbisha-iccard.com/information/idm.html)  

[Apple Pay](https://support.apple.com/ja-jp/HT203027)

[Google Pay](https://support.google.com/pay/answer/7643925)  

[IC SFCard Fan](http://www014.upp.so-net.ne.jp/SFCardFan/)

## 作成者  
[yusuke-1105](https://github.com/yusuke-1105)
