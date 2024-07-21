from flask import Flask,request
from flask_cors import CORS
import threading
# from bson.objectid import ObjectId
import json
import time
import datetime
import uuid
import os
from twilio.rest import Client

# import pymongo
# client = pymongo.MongoClient('localhost', 27017)
# db = client.ReminderApp
# collection = db.tasks

account_sid = "AC5e4990c3db2e05e0318a3c98c7f0e888"
auth_token = "f3cd5ae5c0dc77f4307bde8e9a9608bf"
client = Client(account_sid, auth_token)


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "*"}})


taskid = []
taskdict = {}
lock = threading.Lock()

@app.route("/")
def hello_world():
    thr = threading.Thread(target=scheduler, args=(), kwargs={})
    thr.start()
    print("Scheduler thread started.")
    return {'status': 200, 'message': 'SUCCESS', 'data': []}

@app.route("/settimer", methods=['POST'])
def set_timer():
    if request.method == 'POST':
        try:
            message = request.json['message']
            phonenumber = request.json['phonenumber']
            timeanddate = request.json['timeanddate']
            x = call_timer(message, phonenumber, timeanddate)
            print(f"Timer set with id: {x}")
            return {'status': 200, 'message': 'Success', 'data': json.dumps({'id': str(x)})}
        except Exception as e:
            print(f"Error in set_timer: {e}")
            return {'status': 500, 'message': str(e)}
    else:
        print("Invalid method for set_timer.")
        return {'status': 400, 'message': 'Method not allowed'}

def call_timer(message, phonenumber, timeanddate):
    mydate = datetime.datetime.fromtimestamp(int(timeanddate))
    myData = {"message": message, "phonenumber": phonenumber, "timeanddate": mydate}
    
     # x = collection.insert_one(myData)
    x = uuid.uuid4()
    
    with lock:
        taskdict[x] = myData
        taskid.append(x)
        taskid.sort(key=lambda x: taskdict[x]['timeanddate'].timestamp())
        print(f"Task scheduled: {myData}")
   # taskdict[x.inserted_id]=myData
    # taskid.append(x.inserted_id)
    # taskid.sort(key=lambda x: taskdict[x]['timeanddate'].timestamp())
    # return x.inserted_id
    return x

def callto(message, phonenumber):
    print(f"Making call to {phonenumber} with message: {message}")
    call = client.calls.create(
        twiml=f"<Response><Say voice='Polly.Aditi'>{message}</Say><Play>http://demo.twilio.com/docs/classic.mp3</Play></Response>",
        to=f"+91{phonenumber}",
        from_="+16822171724"
    )
    print("Call placed successfully.")

def scheduler():
    print("Scheduler started.")
    while True:
        with lock:
            if taskid:
                curtask = taskdict[taskid[0]]
                curtime = datetime.datetime.now()
                print(f"Current time: {curtime}, Task time: {curtask['timeanddate']}")
                if curtime >= curtask['timeanddate']:
                    print("Time to make a call.")
                    callto(curtask['message'], curtask['phonenumber'])
                    del taskdict[taskid[0]]
                    taskid.pop(0)
                    print("Task completed and removed.")
        time.sleep(1)

@app.route("/deletetimer", methods=['POST'])
def delete_timer():
    if request.method == 'POST':
        try:
            id = request.json['id']
            id = uuid.UUID(id)
            # id = ObjectId(id)
            # myquery = { "_id":  id }

            # collection.delete_one(myquery)
             
            with lock:
                curid = taskid.index(id)
                del taskdict[taskid[curid]]
                taskid.pop(curid)
                print(f"Deleted timer with id: {id}")

            return {'status': 200, 'message': 'Success'}
        except Exception as e:
            print(f"Error in delete_timer: {e}")
            return {'status': 500, 'message': str(e)}
    else:
        print("Invalid method for delete_timer.")
        return {'status': 400, 'message': 'Method not allowed'}

@app.route("/deleteall", methods=['POST'])
def delete_all():
    if request.method == 'POST':
        try:
            with lock:
                # collection.delete_many({})
                taskdict.clear()
                taskid.clear()
                print("All timers deleted.")
            return {'status': 200, 'message': 'Success'}
        except Exception as e:
            print(f"Error in delete_all: {e}")
            return {'status': 500, 'message': str(e)}
    else:
        print("Invalid method for delete_all.")
        return {'status': 400, 'message': 'Method not allowed'}

if __name__ == '__main__':
    thr = threading.Thread(target=scheduler, args=(), kwargs={})
    thr.start()
    print("Starting Flask app.")
    app.run(debug=False, host='0.0.0.0')