from tools import update_sql, dics, message, database, status
from flask import Flask, request, render_template, url_for
from pysnooper import snoop
import datetime
import os

app = Flask(__name__)

# 強制退室でメッセージを送る関数============================================------------------------------
def message_leaving(STATUS):
    update_sql(f"update student_tb set {STATUS}='OUT' where {STATUS}='IN'")  #roomaのSTATUSを全てOUTに
    message("warning", STATUS, "強制退室", f"<強制退室> Bye")   #強制退室のメッセージを送る
    message(None, STATUS, '退室', dics['退室'])   #退室のメッセージを送る

# 入退室の登録ができたか否かを確認する関数===================---------------------------------------------
def show_result(nickname, room):
    data_tb=database[room]
    update_sql(f"update {data_tb} set flag='0'")              #読み取りを登録モードにする
    update_sql(f"update {data_tb} set nickname='{nickname}'") #入力されたニックネームをデータベースに入れる

    #ニックネームを含めて、学生証の登録が済んだか否かを確認---------------------------
    start_time=datetime.datetime.now()
    #3秒以内にsuccessかfailureが返ってこなかったら、結果をNULLで返す
    while (datetime.datetime.now()-start_time).total_seconds()<3:
        if (result:=update_sql(f"select * from {data_tb}")['result'])!='NULL':break
        else: pass
    #---------------------------------------------------------------------------------
    update_sql(f"update {data_tb} set result='NULL'")    #データベースのresultの値を元に戻す
    update_sql(f"update {data_tb} set nickname='NULL'")  #データベースのnicknameの値を元に戻す
    update_sql(f"update {data_tb} set flag='1'")

    return result

@app.context_processor
def overrUNIV_IDe_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static' and (filename := values.get('Regist.css', None)):
        file_path = os.path.join(endpoint, filename)
        values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route("/")
def index(): return render_template('Regist.html')

#@snoop()
@app.route('/regist', methods=['GET','POST'])
def regist():
    try:
        #ここでどちらのボタンが押されたかわかり、つまりどちらの部屋のニックネームの登録、変更モードかどうかがわかる
        room=request.form['room']
        #入力されたニックネームをここで取得
        nickname=request.form['regist']

        num_before=update_sql(f"select count(*) from student_tb where NICKNAME ='{nickname}'")['count(*)']

        # 強制退室======================================================================--------------
        # room aの強制退室
        if request.form['regist'] == "reset" and request.form['room'] == "room-a":
            message_leaving('STATUS_A')
            return render_template('Result.html', result="R E S E T", message1='部　室')

        # room bの強制退室
        elif request.form['regist'] == "reset" and request.form['room'] == "room-b":
            message_leaving('STATUS_B')
            return render_template('Result.html', result="R E S E T", message1='地下室')


        # nicknameが空でなく、ニックネームがその時点で他の人に登録されていなかった時============================
        if nickname!="": result=show_result(nickname, room)
        else: result='failure'

        # 学生証を一度登録したことがあるひとがニックネームを変えた時=====================================-----
        if result == "success":
            if num_before==0:
                #本名取得
                name=update_sql(f"select * from student_tb where NICKNAME ='{nickname}'")['NAME']
                #slackにニックネームが変更されたことを通知
                message(None, status[room], 'none', f'{name}さんがニックネームを{nickname}に変更したで')

            return render_template('Result.html',
                                    result="S U C C E S S",
                                    message1=f'"{nickname}"として登録しました。',
                                    message2='今日も頑張って！')


        #しっかりとカードがタッチできていないか何かの問題で登録が失敗した時=============------------------------
        elif result == "failure":
            return render_template('Result.html',
                                    result="F A I L U R E",
                                    message1='他のニックネームに変えてみてね！',
                                    message2='あるいはカードのタッチに問題があったかも')


        #初めて登録した人に出てくる=================================================================-----
        elif result == "fir_suc":
            #本名取得
            name=update_sql(f"select * from student_tb where NICKNAME ='{nickname}'")['NAME']
            #slackにニックネームが変更されたことを通知
            message(None, status[room], 'none', f'{name}さんがニックネームを{nickname}に登録したで')

            return render_template('Result.html', 
                                    result="WELCOME TO DTK !",
                                    message1=f'"{nickname}"',
                                    message2='電通研でこれからがんばってね！')


        #上記のいずれに該当しなければエラー=========================================-----------------------
        else:
            return render_template('Result.html',
                                    result="E R R O R",
                                    message1='きちんとカードが反応していないみたい',
                                    message2='それかパソリが反応していないのかな ?')                   
    except Exception as e:
            return render_template('Result.html',
                        result="E R R O R",
                        message1='正しいニックネームを入力してね')  


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)