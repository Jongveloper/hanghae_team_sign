from flask import Flask, render_template, jsonify, request, session, redirect, url_for


app = Flask(__name__)
from pymongo import MongoClient


client = MongoClient('localhost',27017)
db= client.sign
SECRET_KEY = 'hanghae11team'

import jwt
import datetime
import hashlib


############################################
## 크롤링 ####################################
############################################

#html 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/컬렉션', methods=["GET"])
def get_컬렉션이름():

    순위리스트 = list(db.컬렉션이름.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'msg': list 연결되었습니다})




############################################
## HTML ####################################
############################################
@app.route('/')
def main():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', name=user_info["name"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    id = "ID"
    password = "PassWord"
    return render_template('login.html', id=id, password=password)

@app.route('/join')
def join():
    name= "이름"
    id = "아이디"
    password = "비밀번호"
    re_password = "비밀번호 재확인"
    return render_template('join.html', name=name, id=id, password=password, re_password=re_password)
@app.route('/main')
def index():
    return render_template('index.html')

############################################
## 로그인 ####################################
############################################

@app.route('/join/save', methods=['POST'])
def join_save():
    name_receive = request.form['name_give']
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    re_pw_receive = request.form['re_pw_give']

    check_duplicate_user = db.user.find_one({'id': id_receive})

    if check_duplicate_user is not None:
        if check_duplicate_user['id'] == id_receive:
            return jsonify({'result': 'fail', 'msg': '아이디가 중복되었습니다.'})

    if pw_receive != re_pw_receive:
        return jsonify({'result':'fail', 'msg': '비밀번호가 일치하지 않습니다.'})

    if id_receive == "" or name_receive == "" or pw_receive == "":
        return jsonify({'result':'fail', 'msg': "모두 입력해주세요!"})

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'name': name_receive, 'id': id_receive, 'pw': pw_hash})

    return jsonify({'result': 'success'})

# 로그인 api
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1000)
        }
        # payload 암호화
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})




@app.route('/api/name', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'id': payload['id']}, {'_id':0})
        return jsonify({'result': 'success', 'name': userinfo['name']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg' : '로그인 정보가 존재하지 않습니다.'})


@app.route('/like_bu', methods=['POST'])
def like_b():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_id = payload["id"]
        teams = list(db.teams.find({}))
        a = []
        for team in teams:
            tname = team["t_name"]
            if bool(db.likes.find_one({"post_id": tname, "id": user_id})):
                a.append(tname)



        print(a)
        return jsonify({"result": "success", 'msg': 'updated',  "post_id": a})
        # 좋아요 수 변경

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

# 좋아요 api


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        user_info = db.user.find_one({"id": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        action_receive = request.form["action_give"]
        league = db.teams.find_one({"t_name": post_id_receive})
        doc = {
            "post_id": post_id_receive,
            "id": user_info["id"],
            "league": league["league"]
        }



        if action_receive == "like":
            db.likes.insert_one(doc)

        else:
            db.likes.delete_one(doc)

        count = db.likes.count_documents({"post_id": post_id_receive})
        # u_id = payload["id"]
        # a = 0
        # if bool(db.likes.find_one({"id": u_id, "post_id": post_id_receive })):
        #     a = 1
        # else:
        #     a = 2

        return jsonify({"result": "success", 'msg': 'updated',  "count": count})
        # 좋아요 수 변경

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


