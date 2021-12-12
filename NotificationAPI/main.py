from flask import Flask, request, send_from_directory, make_response,jsonify,json
import mysql.connector
from mysql.connector.constants import ClientFlag
import pymssql
import base64
from flask_cors import CORS
import  requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app = Flask(__name__)
cors = CORS(app, resorces={r'/d/*': {"origins": '*'}})
connection = pymssql.connect(server='34.132.235.237', user='sqlserver', password='1234', database='cloudapp')
cred = credentials.Certificate("notify-new-firebase-adminsdk-mi5z2-e765829aca.json")
firebase_admin.initialize_app(cred)
firestore_db= firestore.client()

@app.route("/api/cachedata",methods=['POST'])
def cachedata():
    try:
        content = request.json
        collection= content["collection"]
        recordName= content["record"]
        data=content["data"]
        insertData=storeToFireStore(collection,recordName,data)
        if insertData==None:
            return ("Created Record",201)
        return make_response("Cannot insert Record", 500)
    except Exception as ex:
        return make_response(ex.msg, 500)
@app.route("/api/getcachedata/<collection>/<session>",methods=['GET'])
def getcachedata(collection,session):
    try:
        doc=getFromStore(collection,session)
        if doc!=500 and doc is not None:
            return make_response(doc,200)
        else:
            return make_response("No data found",404)
    except Exception as ex:
        return make_response(ex.msg, 500)
@app.route("/api/deletecachedata/<collection>/<session>",methods=['DELETE'])
def deletecachedata(collection,session):
    try:
        val=deleteFromStore(collection,session)
        if val=="":
            return ("",204)
        return make_response("Cannot Delete Record", 500)
    except Exception as ex:
        return make_response(ex.msg, 500)
@app.route("/api/retriveuser",methods=['POST'])
def retriveuser():
    try:
        content=request.json
        username=content["username"]
        pwd=str(base64.urlsafe_b64decode(content["password"]),"utf-8")
        userRecord=getFromStore("userdetails",username)
        if(userRecord is None or userRecord==500 or userRecord.json["pwd"]!=pwd):
            cursor = connection.cursor()
            sql="SELECT email,username,client_token FROM users where (username like '"+username.lower()+"' or email like '"+username.lower()+"') and password like '"+pwd+"'"
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result)==1:
                userRecord={
                    "client_token":result[0][2],
                    "email": result[0][0],
                    "pwd": pwd,
                    "username":result[0][1]
                    }
                return make_response(jsonify(userRecord),200)
            return make_response('No Records Found from MSSQL', 404)
        else:
            return make_response(userRecord,200)
    except mysql.connector.Error as err:
        return make_response(err.msg, 500)
    except Exception as ex:
        return make_response(ex.msg, 500)
@app.route("/api/registeruser/<username>",methods=['POST'])
def registeruser(username):
    try:
        content=request.json
        email=content["email"]
        pwd=str(base64.urlsafe_b64decode(content["password"]),"utf-8")
        cursor = connection.cursor()
        sql = "INSERT INTO users (email, username, password) VALUES (%s, %s, %s)"
        cursor.execute(sql,(email.lower(),username.lower(),pwd))
        connection.commit()
        data={
            "email":email.lower(),
            "pwd":pwd,
            "username":username.lower(),
            "client_token":""
        }
        insertFb=storeToFireStore("userdetails",email.lower(),data)
        response = make_response('User Created', 201)
        return response
    except mysql.connector.Error as err:
        return make_response(err.msg, 500)
    except Exception as ex:
        return make_response(ex.msg, 500)
@app.route("/api/sendpushnotification",methods=['POST'])
def sendpushnotification():
    try:
        content = request.json
        sendPushTo = content["to"]
        title = content["title"]
        body = content["body"]
        clickAction=content["clickaction"]
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=AAAAeXmdUIg:APA91bE21RRxQMKcfUa-7HddZ0UBZYfpJrve84n4I-gssinAdgLS7PM4b-pts-Bz1Tf4Epx-6ioKncSkhify-Yqi5_90txCCJsSOiLRZWcDHjdG_HxcuJT-1PhumH-c9NnbwNpzCVcYY',
        }
        body= {
    "notification":{
        "title": title,
        "body": body,
        "icon":"/images/PushIcon.png",
        "click_action":clickAction
    },
  "to":sendPushTo
}
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        pushStatus = json.loads(response.text)
        if response.status_code==200 and pushStatus["success"]==1:
            result= make_response("", response.status_code)
        else:
            result = make_response("",404)
        return result
    except Exception as ex:
        return make_response(ex.msg, 500)
@app.route("/api/updatetoken/<email>",methods=['PATCH'])
def updatetoken(email):
    try:
        content=request.json
        token=content["token"]
        cursor = connection.cursor()
        sql = "update users set client_token='"+token+"' where email like '"+email+"'"
        cursor.execute(sql)
        connection.commit()
        getFb=getFromStore("userdetails",email)
        data=getFb.json
        data["client_token"]=token
        updateFb= storeToFireStore("userdetails", email.lower(), data)
        response = make_response('', 204)
        return response
    except mysql.connector.Error as err:
        return make_response(err.msg, 500)
    except Exception as ex:
        return make_response(ex.msg,500)
@app.route("/api/deleteuser/<email>",methods=['DELETE'])
def delteuser(email):
    try:
        cursor = connection.cursor()
        sql = "delete from users where email like '"+email+"'"
        cursor.execute(sql)
        connection.commit()
        deleteFb=deleteFromStore("userdetails",email)
        return make_response('', 204)
    except mysql.connector.Error as err:
        return make_response(err.msg, 500)
    except Exception as ex:
        return make_response(ex.msg, 500)

def storeToFireStore(collectionName,documentname,document):
    try:
        doc_ref = firestore_db.collection(collectionName).document(documentname)
        doc_ref.set(document)
        return None
    except  Exception as ex:
        return 500
def getFromStore(collectionName,documentname):
    try:
        doc_ref = firestore_db.collection(collectionName).document(documentname)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify(doc.to_dict())
        return None
    except  Exception as ex:
        return 500
def deleteFromStore(collectionName,documentname):
    try:
        val = firestore_db.collection(collectionName).document(documentname).delete()
        return ""
    except  Exception as ex:
        return 500

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

if __name__ == '__main__':
    app.run()