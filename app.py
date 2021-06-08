from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient
from werkzeug.utils import secure_filename

client = MongoClient('localhost',27017)
db= client.sign
SECRET_KEY = 'hanghae11team'
import jwt
import datetime
import hashlib

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


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.posts.find({}).sort("date", -1).limit(20))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다."})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 좋아요 api

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["name"]
        }



        if action_receive == "like":
            db.likes.insert_one(doc)

        else:
            db.likes.delete_one(doc)


        return jsonify({"result": "success", 'msg': 'updated'})
        # 좋아요 수 변경

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
