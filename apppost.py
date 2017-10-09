''' REST sample '''
#!flask/bin/python
import sqlite3
import json
from cerberus import Validator
from contextlib import closing
from flask import Flask, jsonify, abort, make_response, url_for, g, request, session, redirect, abort, render_template, flash
from datetime import datetime, date
from pprint import pprint

import requests as req
import simplejson as json
client_id = 'xxxxxxxxxxx'
client_secret = 'xxxxxxxxxxx'
getAccessToken = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials' % (
    client_id, client_secret)
r = req.get(getAccessToken)
obj = json.loads(r.text)
accessToken = obj['access_token']

# API version
VERSION = "v1.0"

# DB settings
DATABASE = 'apppost.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# building app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APPPOST_SETTINGS', silent=True)
CONTEXT_ROOT = "/todo/api/" + VERSION


def connect_db():
    """ connection作成用 """
    return sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_COLNAMES)


@app.before_request
def before_request():
    """ 【フレームワーク用】リクエスト受信時の初期化処理 """
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """ 【フレームワーク用】リクエスト終了時のお掃除処理 """
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.errorhandler(404)
def not_found(error):
    """ 【フレームワーク用】エラー時の処理 """
    return make_response(jsonify({'error': 'Not found'}), 404)


def select_for_object(query_string, params):
    """ 【共通処理】query_stringの実行結果をオブジェクト（連想配列）に変換して返す処理 """
    db = g.db
    cur = db.execute(query_string, params)
    column_names = [rec[0] for rec in cur.description]
    new_tasks = [
        {column_names[idx]:row[idx]
         for idx in range(len(column_names))
         } for row in cur.fetchall()]
    print(new_tasks)
    return new_tasks


def update_for_object(update_string, params):
    """ 【共通処理】updateの実行結果のカウント返す処理 """
    db = g.db
    cur = db.execute(update_string, params)
    db.commit()
    return cur


@app.route('/todo/api/v1.0/login', methods=['GET'])
def getLogin():
    """ 【API】ログインチェック """
    return jsonify('user_id' in session)


@app.route('/todo/api/v1.0/login', methods=['PUT'])
def login():
    """ 【API】ログイン """
    user_id = request.json.get('user_id')
    password = request.json.get('password')
    rememberme = request.json.get('rememberme')
    user = select_for_object(
        "select user_id from users where user_id=? and password=?", [user_id, password])
    session['user_id'] = user_id
    return jsonify(len(user) == 1)


@app.route('/todo/api/v1.0/login', methods=['POST'])
def signup():
    """ 【API】サインイン """
    user_id = request.json.get('user_id')
    password = request.json.get('password')
    print(user_id, password)
    cnt = 0
    try:
        cnt = update_for_object(
            "insert INTO users (user_id,password) values(?,?)", [user_id, password]).rowcount
        print("Count=", cnt)
    except sqlite3.Error as e:
        cnt = 0
    if cnt == 1:
        # OK
        session['user_id'] = user_id
        return jsonify(True)
    else:
        # NG
        return jsonify(False)


@app.route('/todo/api/v1.0/facebooklogin', methods=['PUT'])
def signup():
    """ 【API】facebookログイン """
    userAccessToken = request.json.get('accessToken')
    getData = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s' % (
        userAccessToken, accessToken)
    r = req.get(getData)
    obj = json.loads(r.text)
    user_id = obj['data']['user_id']
    cnt = 0
    user = select_for_object(
        "select user_id from users where user_id=?", [user_id])
    session['user_id'] = user_id
    if len(user) == 1:
        return jsonify(len(user) == 1)
    else:
        cnt = update_for_object(
            "insert INTO users (user_id) values(?)", [user_id])
        print("Count=", cnt)
        return jsonify(len(user) == 1)


@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    """ 【API】全タスクリストを返却する """
    print(session['user_id'])
    response = jsonify(select_for_object(
        "select * from tasks where user_id=? and status != -1 order by end_date", [session['user_id']]))
    return response


@app.route('/todo/api/v1.0/task', methods=['POST'])
def add_task():
    print(request.json)
    task = request.json
    """ 【API】タスクを追加する """

    # Validation Definition
    schema = {
        'end_date': {
            'type': 'date',
            'required': True,
            'empty': False,
        },
        'item': {
            'type': 'string',
            'required': True,
            'empty': False,
        }
    }

    # Create Validation Object
    v = Validator(schema)

    # Initialize response
    response = ""

    try:
        # Change the data type for validation of end_date
        data = {"end_date": datetime.strptime(request.json.get(
            'end_date'), '%Y-%m-%d'), "item": request.json.get('item')}
        if v.validate(data) == False:
            # response = "Argument Error"
            return response
    except ValueError:
        # response = "An error occurred"
        print("An error occurred")
        return response
    except TypeError:
        print("An error occurred")
        # response = "An error occurred"
        return response

    # Inject request data into database
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("insert into tasks (end_date,item,update_record_date,user_id) values (?,?,?,?)",
                    (data.get("end_date"), data.get("item"), datetime.now(), session["user_id"]))
        conn.commit()
        # response = "Data has been injected"
        return response
    except sqlite3.Error as e:
        # response = "An error occurred:" % e.args[0]
        return response


@app.route('/todo/api/v1.0/task/<task_id>', methods=['PUT'])
def upd_task(task_id):
    status = request.json.get('status')
    """ 【API】タスクを更新する """
    try:
        if status == None:
            task = request.json.get('task')
            end_date = task.get('end_date')
            item = task.get('item')
            status = task.get('status')
            response = update_for_object(
                "update tasks set end_date=?,item=?,status=?,update_record_date=? where task_id=?", [end_date, item, status, datetime.now(), int(task_id)])
        else:
            response = update_for_object(
                "update tasks set status=?,update_record_date=? where task_id=?", [status, datetime.now(), int(task_id)])
        return jsonify(0)
    except sqlite3.Error as e:
        # response = "An error occurred:" % e.args[0]
        return response


@app.route('/todo/api/v1.0/task', methods=['DELETE'])
def del_task():
    """ 【API】タスクを削除する """
    response = jsonify(update_for_object(
        "delete from tasks where task_id=?", [int(task.task_id)]))
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8200, debug=True)
