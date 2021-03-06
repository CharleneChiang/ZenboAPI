from flask import Flask
import yaml
import time
import json
import MySQLdb
from flask import request
from flask import jsonify
from flask_mysqldb import MySQL
import hashlib



# construct app
app = Flask(__name__)


# read server
with open("./config/server.yml", 'r') as stream:
    try:
        server_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# read database
with open("./config/database.yml", 'r') as stream:
    try:
        mysql_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# Set MySQL Config
app.config["MYSQL_HOST"] = mysql_config["host"]
app.config["MYSQL_USER"] = mysql_config["username"]
app.config["MYSQL_PASSWORD"] = mysql_config["password"]
app.config["MYSQL_DB"] = mysql_config["database"]

# Construct MySQL Object
mysql = MySQL(app)

# Insert register information


def insert_registeration(uid: str, name: str, email: str, gender: str, department: str, password: str, mysql=mysql):
    cur = mysql.connection.cursor()
    sql_command = "INSERT INTO library_db.user_info (uid, name, email, gender, department, password) VALUES (%s,%s,%s,%s,%s,%s);"
    try:
        cur.execute(sql_command, (uid, name, email,
                                    gender, department, password))
        mysql.connection.commit()
        return {"res": "success"}

            # fetch_data = cur.fetchall()
            # cur.close()
            # return fetch_data
    except:
        return {"res": "fail"}

# Register API


@app.route('/api/v1/register/', methods=['POST'])
def register_api():
    data = request.get_json()
    uid = data["uid"]
    name = data["name"]
    email = data["email"]
    gender = data["gender"]
    department = data["department"]
    # m = hashlib.sha256()
    password = hashlib.sha256(data["password"].encode("utf-8")).hexdigest()
    start_time = time.time()
    return_dict = insert_registeration(
        uid, name, email, gender, department, password)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    print(return_dict)
    return jsonify(return_dict)


# Get user-user list information
# def get_uuserbook(email: str, mysql=mysql):
#     cur = mysql.connection.cursor()
#     sql_command = "SELECT `uu_list` FROM user_info WHERE email = %s;"
#     cur.execute(sql_command, (email, ))
#     columns = [col[0] for col in cur.description]
#     fetch_data = {col: row for col, row in zip(columns, cur.fetchall()[0])}
#     cur.close()
#     return fetch_data


# User-User Suggestion API
# @app.route('/api/v1/uuser/', methods=['POST'])
# def uuser_api():
#     data = request.get_json()
#     email = data["email"]
#     start_time = time.time()
#     return_dict = get_uuserbook(email)
#     end_time = time.time()
#     handle_time = round(end_time - start_time, 2)
#     return_dict["handle_time"] = handle_time
#     return_dict["email"] = email
#     return jsonify(return_dict)

# Get user information


def get_userinfo(email: str, password: str, mysql=mysql):
    cur = mysql.connection.cursor()
    sql_command = "SELECT * FROM user_info WHERE email = %s AND password = %s;"
    try:
        cur.execute(sql_command, (email, password, ))
        # fetch_data = cur.fetchall()
        columns = [col[0] for col in cur.description]
        fetch_data = {col: row for col, row in zip(columns, cur.fetchall()[0])}
        fetch_data["res"] = "success"
        # print (fetch_data["uu_list"])
        book_detail = []
        book_final = []
        book_info = ""
        if fetch_data["uu_list"] is None:
            fetch_data["book_info"] = "null"
            return fetch_data
        else:
            for mmsid in json.loads(fetch_data["uu_list"]):
                # print(mmsid)
                sql_command = "SELECT mmsid, title, author, cover FROM mms_info WHERE mmsid = %s;"
                cur.execute(sql_command, (mmsid,))
                fetch_data1 = cur.fetchall()
                # columns = [col[0] for col in cur.description]
                # book_detail.append({col: row for col, row in zip(columns, cur.fetchall()[0])})
                book_detail.append(fetch_data1[0])
            for book in book_detail:
                book_final.append(str(book[0])+"@@" +
                                book[1]+"@#"+book[2]+"##"+book[3]+"#@")
            for i in range(len(book_final)):
                book_info += book_final[i]
            fetch_data["book_info"] = book_info
            return fetch_data
    except:
        return{"res": "fail"}

    cur.close()


def get_userloan(uid: int, mysql=mysql):
    cur = mysql.connection.cursor()
    sql_command = "SELECT `mmsid` FROM item_info LEFT JOIN loan_info on item_info.iid = loan_info.iid WHERE loan_info.uid = %s "
    cur.execute(sql_command, (uid,))
    fetch_data = cur.fetchall()
    # columns = [col[0] for col in cur.description]
    # fetch_data = {col: row for col, row in zip(columns, cur.fetchall()[0])}
    cur.close()
    return {"res": fetch_data}


# User Information API (Include recent loan data)

@app.route('/api/v1/userinfo/', methods=['POST'])
def userinfo_api():
    data = request.get_json()
    email = data["email"]
    password = hashlib.sha256(data["password"].encode("utf-8")).hexdigest()
    start_time = time.time()
    return_dict = get_userinfo(email, password)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["email"] = email

    return jsonify(return_dict)


@app.route('/api/v1/userloan/', methods=['POST'])
def userloan_api():
    data = request.get_json()
    uid = data["uid"]
    start_time = time.time()
    return_dict = get_userloan(uid)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["uid"] = uid
    return jsonify(return_dict)


# Get user-item list information
def get_uitembook(email: str, mysql=mysql):
    cur = mysql.connection.cursor()
    sql_command = "SELECT `ui_list` FROM mms_info LEFT JOIN user_info on user_info.uid = user_top_k.uid WHERE email = %s;"
    cur.execute(sql_command, (email, ))
    fetch_data = cur.fetchall()
    cur.close()
    return fetch_data


# User-Item Suggestion API
@app.route('/api/v1/useritem/', methods=['POST'])
def useritem_api():
    data = request.get_json()
    email = data["email"]
    start_time = time.time()
    return_dict = get_uitembook(email)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["email"] = email
    return jsonify(return_dict)

# Get item-item list information
# def get_iitembook(mmsid: str, mysql=mysql):
#     cur = mysql.connection.cursor()
#     sql_command = "SELECT `ii_top30`,hashtag FROM mms_info WHERE mmsid = %s;"
#     cur.execute(sql_command, (mmsid, ))
#     columns = [col[0] for col in cur.description]
#     fetch_data = {col: row for col, row in zip(columns, cur.fetchall()[0])}
#     cur.close()
#     return fetch_data

# Item-Item Suggestion API


# @app.route('/api/v1/iitem/', methods=['POST'])
# def iitem_api():
#     data = request.get_json()
#     mmsid = data["mmsid"]
#     start_time = time.time()
#     return_dict = get_iitembook(mmsid)
#     end_time = time.time()
#     handle_time = round(end_time - start_time, 2)
#     return_dict["handle_time"] = handle_time
#     return_dict["mmsid"] = mmsid
#     return jsonify(return_dict)

# Main Function


def main():
    app.run(debug=True, host=server_config["ip"], port=5001)


if __name__ == "__main__":
    main()


# /Users/charlene/Library/Android/Sdk
