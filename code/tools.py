from io import UnsupportedOperation
import pymysql.cursors
import requests
import json
import sys
import os

#slackメッセージを送るための関数
def message(color: str, STATUS: str, status: str, text: str) -> None:
    attachment = {
        "color": color,             #メッセージの色決定
        "username": name[status],   #メッセージを送るユーザネームを設定
        "icon_emoji": icon[status], #アイコンの絵文字を設定
        "pretext": "",
        "text": text,               #メッセージに書く内容を書く
        "mrkdwn": ["text"],         #マークダウン方式で書く
    }

    #送信!
    requests.post(slack[STATUS], data=json.dumps(attachment))

def sql() -> pymysql:
    return pymysql.connect(host=DATABASE_IP,
                           user='root',
                           password=DATABASE_PASS,
                           db='io',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)

#MySQLを操作するための関数
def update_sql(command: str) -> dict:
    #このへんはお決まりのコード
    conn=sql()
    cursor = conn.cursor()
    cursor.execute(command)
    conn.commit()
    conn.close()
    return cursor.fetchone()

#slackにメッセージを送るURlを格納
slack={'STATUS_A': os.environ['TEST1'],
       'STATUS_B': os.environ['TEST2']}

#slackのメッセージのアイコンを設定
icon={"入室":":den:",
      "退室":":tsu:",
      "強制退室":":tsu:",
      'none':":den-tu:"}

#slackのメッセージの表示名設定
name={"入室":"でん",
      "退室":"つー",
      "強制退室":"つー", 
      'none':"でん&つー"}

#開室、施錠されるときのメッセージ
dics={"入室":"`~~~HI Bestie !~~~`", 
      "退室":"`~~BYE Bestie !~~`"}

#データベース選択用
database={'room-a': 'utila_tb',
          'room-b':'utilb_tb'}

#STATUS選択用
status={'room-a':'STATUS_A',
        'room-b':'STATUS_B'}

WAIT_TIME=7 #同じUNIV_IDの入退室は7秒間おく
DATABASE_IP=os.environ['IP_ADDRESS1']       #データベースのIPアドレス
DATABASE_PASS=os.environ['DATABASE_PASS']   #データベースのパスワード

# ROOM A用-----------------------------------------
try: update_sql(f"update utila_tb set flag='1'")
except OSError:
    DATABASE_IP=os.environ['IP_ADDRESS2']
    update_sql(f"update utila_tb set flag='1'")
#ROOM B用------------------------------------------
except:
    #時々データベースのIPアドレスがIP_ADDRESS1でないときがあるのでそれの回避策
    DATABASE_IP=os.environ['IP_ADDRESS3']
    update_sql(f"update utilb_tb set flag='1'")

# ここでtry文を使っているのはui.pyがこのファイルをimportした時にエラーが出るのを防ぐため
# ui.pyでエラーが出るのはargsが設定されていないため
try:
    room=sys.argv[1]        #引数からプログラムを動かす
    usb=sys.argv[2]         #引数からpasoriの'bus id'と'device id'とを入力
    STATUS=status[room]     #データベース操作のコマンドの際に使用する部屋ごとの'status'
    DATA_TB=database[room]  #フラグ等で使用するデータベースでどちらを使うのか
    update_sql(f"update {DATA_TB} set result='NULL'")
    update_sql(f"update {DATA_TB} set nickname='NULL'")
except: pass