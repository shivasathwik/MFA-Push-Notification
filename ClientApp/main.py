from flask import Flask, render_template, request, send_from_directory
import base64
import requests
import json
import time

app = Flask(__name__)
api_url="https://notificationapi-dot-mnsasista.uc.r.appspot.com/api"
authenticator_url="https://authenticator-dot-mnsasista.uc.r.appspot.com/"
@app.route("/")
def MainPage():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registeruser",methods=['POST'])
def registeruser():
    try:
        authenticator_url = "https://authenticator-dot-mnsasista.uc.r.appspot.com/"
        if(request.form['password']==request.form['confirm']):
            pwd = str(base64.urlsafe_b64encode(request.form['password'].encode("utf-8")),"utf-8")
            input = {"email": request.form['email'], "password": pwd}
            result = requests.post(url=api_url+"/registeruser/"+request.form['username'], data=json.dumps(input), headers={'Content-Type': 'application/json'})
            if (int(result.status_code) == 201):
                authenticator_url+="?email="+request.form['email']
                # return "<p>User Registered Successfully!!! Please verify the account using the link <a href="+authenticator_url+" >Verify Here</a></p>"
                return render_template("verify.html",inputdata=authenticator_url)
            else:
                return render_template("error.html",inputdata=result.text)
        else:
            return render_template("error.html", inputdata="Confirm PWD not matched")
    except Exception as ex:
        return render_template("error.html", inputdata=ex.msg)

@app.route("/login",methods=['POST'])
def login():
    try:
        pwd = str(base64.urlsafe_b64encode(request.form['pwd'].encode("utf-8")),"utf-8")
        input={"username":request.form['username'],"password":pwd}
        result=requests.post(url=api_url+"/retriveuser", data=json.dumps(input),headers={'Content-Type': 'application/json'})
        if(int(result.status_code)==200 and len(result.text)>0):
            userInfo=json.loads(result.text)
            usersession=str(base64.urlsafe_b64encode(str(userInfo["email"] + ":" + str(time.time())).encode("utf-8")), "utf-8")
            setSession=storeSession(usersession,{"isApproved":""})
            notify=pushnotification(userInfo["client_token"],usersession)
            if(setSession==notify):
                userAction=pool(usersession)
                if(userAction==200):
                    removeSession=deleteSession(usersession)
                    return render_template("home.html",inputdata=userInfo["username"])
                elif userAction==404:
                    removeSession = deleteSession(usersession)
                    return render_template("index.html")
            else:
                removeSession = deleteSession(usersession)
                return render_template("error.html",inputdata=notify)
        else:
            return render_template("error.html", inputdata="Login Failed.Please check Username/Pwd")
    except Exception as ex:
        return render_template("error.html",inputdata=ex.msg)
def pool(session):
    while True:
        try:
            userSession=requests.get(url=api_url+"/getcachedata/cloudsession/"+session)
            if int(userSession.status_code)==200 and len(userSession.text)>0:
                userSessionValue=json.loads(userSession.text)
                if(userSessionValue["isApproved"]==1):
                    return 200
                elif userSessionValue["isApproved"]==0:
                    return 404
            pool(session)
        except Exception:
            return
def pushnotification(to,usersession):
    try:
        authenticator_url = "https://authenticator-dot-mnsasista.uc.r.appspot.com/"
        input = {"to":to,"title":"MFA Authentication","body":"Click to approve the login","clickaction":"https://authenticator-dot-mnsasista.uc.r.appspot.com/confirm?user="+usersession}
        result=requests.post(url=api_url+"/sendpushnotification", data=json.dumps(input),headers={'Content-Type': 'application/json'})
        if (int(result.status_code) == 200):
            return 200
        else:
            user=str(base64.urlsafe_b64decode(usersession), "utf-8").split(":")[0]
            authenticator_url += "?email=" + user
            # return "<p>Please reset the notification permission using the link <a href=" + authenticator_url +">Verify Here</a></p>"
            return render_template("verify.html", inputdata=authenticator_url)
    except Exception as ex:
        return ex.msg
def storeSession(sesssionid,value):
    try:
        input = {"collection":"cloudsession","record":sesssionid,"data":value}
        result=requests.post(url=api_url+"/cachedata", data=json.dumps(input),headers={'Content-Type': 'application/json'})
        if (int(result.status_code) == 201):
            return 200
    except Exception as ex:
        return ex.msg
def deleteSession(sesssionid):
    try:
        result=requests.delete(url=api_url+"/deletecachedata/cloudsession/"+sesssionid)
        if (int(result.status_code) == 204):
            return 200
    except Exception as ex:
        return ex.msg
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
