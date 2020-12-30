from pysnooper import snoop
from tools import *
import datetime
import binascii
import time
import nfc

#入退室の際のデータベース操作関数
def IO(ID: str, STATUS: str) -> None:
    conn=sql()
    cursor = conn.cursor()

    #入退室する前の人の数をチェック------------------------------------------------------
    cursor.execute(f"select count(*) from student_tb where {STATUS}='IN'")
    _num = cursor.fetchone()
    num_before = _num['count(*)']

    #そのIDに関して登録されている事をここで全て取得----------------------------------------
    cursor.execute(f"select * from student_tb where ID='{str(ID)}'")
    io = cursor.fetchone()

    #その人の入退室状況を変更-----------------------------------------------------------
    if str(io[STATUS]) == "OUT":    #"OUT"だったら"IN"に
        color, status_now = "good", "入室"
        cursor.execute(f"update student_tb set {STATUS}='IN' where ID='{str(ID)}'")
        conn.commit()
        cursor.close()
        conn.close()
        #もしもう一方の部屋の入退室で退室処理をせずにこちらの部屋に来た時
        ANOTHER_STATUS='STATUS_B' if STATUS=='STATUS_A' else 'STATUS_A'
        #もう一方の部屋が"IN"の時それを"OUT"にするためにIO関数を再帰的に動かす
        #再帰的と言ってもループではなく一回だけ
        if str(io[ANOTHER_STATUS]) == "IN": #もしSTATUSBがまだINの状態であれば
            IO(ID, ANOTHER_STATUS)
    else:   #"IN"だったら"OUT"に
        color, status_now = "danger", "退室"
        cursor.execute(f"update student_tb set {STATUS}='OUT' where ID='{str(ID)}'")
        conn.commit()
        cursor.close()
        conn.close()
    #上で再帰的に関数を呼び出す処理があるためconnは一回閉じなければいけない

    conn=sql()
    cursor = conn.cursor()
    
    #そのIDに結び付けられているNICKNAMEを呼び出す-------------------------------------------
    cursor.execute(f"select NICKNAME from student_tb where ID='{str(ID)}'")
    nickname = cursor.fetchone()['NICKNAME']

    #入退室した後の人の数-----------------------------------------------------------------
    cursor.execute(f"select count(*) from student_tb where {STATUS}='IN'")
    _num_after = cursor.fetchone()
    num_after = _num_after['count(*)']

    print(nickname)
    cursor.close()
    conn.close()
    #======================================================================================
    #もともと0人で、1人入ってきたらOPEN
    if num_before == 0 and num_after == 1: message(None, STATUS, status_now, dics[status_now])

    #現在の状態をお知らせ
    message(color, STATUS, status_now, f"<{status_now}>: {nickname}\n現在 {num_after} 人です")

    #0人になったらCLOSE
    if num_after == 0: message(None, STATUS, status_now, dics[status_now])

#学生証から名前と学生証のIDを読み取る関数
def scan_UNIV(target_res: nfc, clf: nfc) -> str:
    tag = nfc.tag.activate_tt3(clf, target_res)
    service_code = [nfc.tag.tt3.ServiceCode(0x100B >> 6, 0x100B & 0x3f)]
    bc_univ_id = [nfc.tag.tt3.BlockCode(0)]
    bc_name = [nfc.tag.tt3.BlockCode(1)]
    name = tag.read_without_encryption(service_code, bc_name).decode()        #学生証から名前を引き出す
    univ_id = tag.read_without_encryption(service_code, bc_univ_id).decode()  #学生証から(学生証の)IDを抜き出す
    return name, univ_id

#学生証のIDからIDを検索する関数
def connected_UNIV(univ_id: str) -> str:
    ID=update_sql(f"select ID from student_tb where UNIV_ID='{univ_id}'")['ID']
    return ID

#交通系ICカードからidmを読み取る関数
def scan_transport(target_res: nfc, clf: nfc) -> str:
    tag = nfc.tag.activate_tt3(clf, target_res)
    _idm = binascii.hexlify(tag.idm)
    idm=_idm.decode()   #idmを抜き出す
    return idm

#交通系ICカードのidmからIDを読み取る関数
def connected_transport(idm: str) -> str:
    try: return update_sql(f"select ID from student_tb where TRANSPORTATION_ID1='{idm}'")['ID']
    except: pass
    try: return update_sql(f"select ID from student_tb where TRANSPORTATION_ID2='{idm}'")['ID']
    except: return

#そのIDが直近で検出されたかどうかを判別する関数
def process(ID:str, STATUS: str, latestID:str, latestTIME: datetime) -> str and datetime:
    lag = datetime.datetime.now() - latestTIME
    #IDが直近7秒以内に検出されたことのあるIDのとき
    if ID==latestID and lag.total_seconds() < WAIT_TIME:
        #次にスキャンできるまでの秒数を一応表示
        print("Please wait "+str(int(WAIT_TIME-lag.total_seconds())+1)+" seconds")
        time.sleep(0.5)
        return latestID, latestTIME
    else:   #IDが3秒以内に検出されてものでなければ
        IO(ID, STATUS)  #入退室の動作を行う
        return ID, datetime.datetime.now()

#学生証でニックネームを登録するための関数
def regist_UNIV(name: str, univ_id: str) -> None:
    result="NULL"
    try:
        nickname=update_sql(f"select * from {DATA_TB}")['nickname']
        if update_sql(f"select count(*) from student_tb where UNIV_ID='{univ_id}'")['count(*)'] == 1:
            #その学生証がすでにデータベースに登録されている時
            #NICKNAMEを変更
            update_sql(f"update student_tb set NICKNAME='{nickname}' where UNIV_ID='{univ_id}'")
            result='success'
        else:                           
            #その学生証がまだデータベースに登録されていないとき
            number=update_sql("select max(ID) from student_tb")['max(ID)']+1 #初めて登録する人にはデータベースのIDの最大値に１を足したIDを割り当てる
            update_sql(f"insert into student_tb values('{number}', '{univ_id}', NULL, NULL, '{name}', '{nickname}', 'OUT', 'OUT')")
            result='fir_suc'
    except: result='failure'
    finally:
        update_sql(f"update {DATA_TB} set result='{result}'")
        update_sql(f"update {DATA_TB} set flag='1'")
        print(result)

#交通系ICカードでニックネームを登録するための関数
def regist_transportation(idm: str) -> None:
    result="NULL"
    #もしこれまでに登録がされたことのないsuicaであれば、入力されたnicknameからtransportation_idを登録する
    #もしこれまでに登録されたことのあるsuicaであれば、入力されたnicknameに変更する
    try:
        nickname=update_sql(f"select * from {DATA_TB}")['nickname']
        #そのニックネームの人が交通系ICカードを何枚登録しているかをカウント
        count0=int(update_sql(f"select count(TRANSPORTATION_ID1) from student_tb where NICKNAME='{nickname}'")['count(TRANSPORTATION_ID1)'])+ \
               int(update_sql(f"select count(TRANSPORTATION_ID2) from student_tb where NICKNAME='{nickname}'")['count(TRANSPORTATION_ID2)'])
        
        #そのidmがデータベースに登録されているか否かをカウント
        count1=update_sql(f"select count(*) from student_tb where TRANSPORTATION_ID1='{idm}'")['count(*)']
        count2=update_sql(f"select count(*) from student_tb where TRANSPORTATION_ID2='{idm}'")['count(*)']

        if count0==0 and count1==0 and count2==0:
            #そのニックネームに交通系ICカードが登録されていない、且つ
            #そのidmを持つ交通系ICがデータベースのどこにも登録されていない
            #入力されたニックネームのところに交通系ICのidmを入れる
            update_sql(f"update student_tb set TRANSPORTATION_ID1='{idm}' where NICKNAME='{nickname}'")

        elif count0==1 and count1==0 and count2==0:
            #そのニックネームに交通系ICカードが登録されている、且つ
            #そのidmを持つ交通系ICがデータベースのどこにも登録されていない
            #入力されたニックネームのところに交通系ICのidmを入れる
            update_sql(f"update student_tb set TRANSPORTATION_ID2='{idm}' where NICKNAME='{nickname}'")

        else:   #そのidmと結び付けられているところのnicknameを入力されたものに変える
            try: update_sql(f"update student_tb set NICKNAME='{nickname}' where TRANSPORTATION_ID1='{idm}'")
            except: pass
            try: update_sql(f"update student_tb set NICKNAME='{nickname}' where TRANSPORTATION_ID2='{idm}'")
            except: raise

        result='success'

    except: result='failure'

    finally:
        update_sql(f"update {DATA_TB} set result='{result}'")
        update_sql(f"update {DATA_TB} set flag='1'")
        print(result)
        
#@snoop()
def Read(clf: nfc, STATUS: str) -> None:
    latestID = "0"
    latestTIME = datetime.datetime.now()
    while True:
        #学生証の読み取り
        target_req = nfc.clf.RemoteTarget("212F")
        target_res = clf.sense(target_req, iterations=1, interval=0.01)
        #読み取りを交通系ICカード専用モードに設定。これによりiPhoneのSuicaやPasmoを呼び出せる
        target_req.sensf_req = bytearray.fromhex("0000030000")
        if not target_res is None: #もし学生証が読み込めていたら
            try:
                name, univ_id=scan_UNIV(target_res, clf)
                #入退室管理モードの時
                if update_sql(f'select * from {DATA_TB}')['flag']=="1":
                    ID=connected_UNIV(univ_id)  #電通研の各個人に割り振られているIDを学生証のIDから抽出
                    latestID, latestTIME=process(ID, STATUS, latestID, latestTIME)
                else:   #登録モードの時
                    regist_UNIV(name, univ_id)  #学生証のIDと名前をデータベースに登録 or ニックネームの変更
                    time.sleep(2.0)
            #except Exception as e: print(e)
            except: pass

        else: #もし交通系ICカードが読み込めていたら or どちらも読み込めていなかったら
            target_res = clf.sense(target_req, iterations=30, interval=0.01)
            try:
                #交通系ICカードの読み取り。もしここで読み込めなかったら、またループの最初に戻る
                idm=scan_transport(target_res, clf)
                #入退室管理モードの時
                if update_sql(f'select * from {DATA_TB}')['flag']=="1":
                    ID=connected_transport(idm)  #電通研の各個人に割り振られているIDを交通系ICカードのidmから抽出
                    latestID, latestTIME=process(ID, STATUS, latestID, latestTIME)
                else:   #登録モードの時
                    regist_transportation(idm)  #交通系ICのidmをデータベースに登録 or ニックネームの変更
                    time.sleep(2.0)
            # except Exception as e: print(e)
            except: pass

if __name__ == "__main__":
    #カード読み取りシステムの実行=============
    print('===== I\'M READY =====')
    with nfc.ContactlessFrontend(usb) as clf:
        Read(clf, STATUS)