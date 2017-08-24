''' REST sample '''
#!flask/bin/python
import sqlite3
import json
from contextlib import closing
from flask import Flask, jsonify, abort, make_response, url_for, g, request, session, redirect, abort, render_template, flash

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


def select_for_object(query_string):
    """ 【共通処理】query_stringの実行結果をオブジェクト（連想配列）に変換して返す処理 """
    db = g.db
    cur = db.execute(query_string)
    column_names = [rec[0] for rec in cur.description]
    new_tasks = [
        {column_names[idx]:row[idx]
         for idx in range(len(column_names))
         } for row in cur.fetchall()]
    print(new_tasks)
    return new_tasks


def update_for_object(update_string):
    """ 【共通処理】updateの実行結果のカウント返す処理 """
    db = g.db
    cur = db.execute(update_string)
    print(new_tasks)
    return new_tasks


@app.route(CONTEXT_ROOT + '/tasks', methods=['GET'])
def get_tasks():
    """ 【API】全タスクリストを返却する """
    response = jsonify(select_for_object('select * from tasks'))
    return response


@app.route(CONTEXT_ROOT + '/task', methods=['POST'])
def add_task():
    print(request.json)
    task = request.json
    """ 【API】タスクを追加する """
    # TODO must sanitize
    response = jsonify(update_for_object(
        'insert into tasks (end_date,item) values (%s,%s)' % (task.end_date, task.item)))
    return response


@app.route(CONTEXT_ROOT + '/task', methods=['PUT'])
def upd_task():
    """ 【API】タスクを更新する """
    response = jsonify(update_for_object(
        'update tasks set status=%d where task_id=%d' % (int(task.status), int(task.task_id))))
    return response


@app.route(CONTEXT_ROOT + '/task', methods=['DELETE'])
def del_task():
    """ 【API】タスクを削除する """
    response = jsonify(update_for_object(
        'delete from tasks where task_id=%s' % (int(task.task_id))))
    return response


if __name__ == '__main__':
    app.run(debug=True)
