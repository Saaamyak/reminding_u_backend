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

account_sid = os.environ.get('account_sid')
auth_token = os.environ.get('auth_token')
client = Client(account_sid, auth_token)


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "*"}})

taskid = []
taskdict = {}
@app.route("/")
def hello_world():
    thr = threading.Thread(target=scheduler, args=(), kwargs={})
    thr.start()
    print('threadstarted')
    return {'status': 200, 'message': 'SUCCESS', 'data': []}
@app.route("/settimer", methods=['POST'])
def set_timer():
    if request.method == 'POST':
        try:
            message = request.json['message']
            phonenumber = request.json['phonenumber']
            timeanddate = request.json['timeanddate']
            
            x=call_timer(message, phonenumber, timeanddate)
            print('initialx',x)
            return {'status': 200, 'message': 'Success' , 'data':json.dumps({'id':str(x)})}
        except Exception as e:
            return {'status': 500, 'message': str(e) }
    else:
        return {'status': 400, 'message': 'Method not allowed'}
def call_timer(message, phonenumber, timeanddate):
    print(message, phonenumber, timeanddate)
    mydate = datetime.datetime.fromtimestamp(int(timeanddate))
    print(mydate)
    myData = { "message": message, "phonenumber": phonenumber, "timeanddate": mydate }

    # x = collection.insert_one(myData)
    x=uuid.uuid4()
    taskdict[x]=myData
    taskid.append(x)
    taskid.sort(key=lambda x: taskdict[x]['timeanddate'].timestamp())
    # taskdict[x.inserted_id]=myData
    # taskid.append(x.inserted_id)
    # taskid.sort(key=lambda x: taskdict[x]['timeanddate'].timestamp())
    # return x.inserted_id
    return x

def callto(message,phonenumber):
    call = client.calls.create(
    twiml= "<Response><Say voice='Polly.Aditi'>"+str(message)+"</Say><Play>http://demo.twilio.com/docs/classic.mp3</Play></Response>",
    #twiml= '<Response><Say>Ahoy, World!</Say></Response>',
    to="+91" +str(phonenumber),
    from_="+17579976306"
    )
    print(call.sid)
def scheduler():
    print("Scheduling Task")
    while True: 
        if len(taskid) > 0 : 
            curtask=taskdict[taskid[0]]
            curtime=datetime.datetime.now()
            print("Printing time", curtime, account_sid, auth_token, curtask['timeanddate'])
            if curtime>=curtask['timeanddate']:
                callto(curtask['message'],curtask['phonenumber'])
                # myquery = { "_id":  taskid[0] }

                # collection.delete_one(myquery)
                del taskdict[taskid[0]]
                taskid.pop(0)
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
            print(id,taskid)
            print(taskdict)
            curid=taskid.index(id)
            del taskdict[taskid[curid]]
            taskid.pop(curid)
            return {'status': 200, 'message': 'Success' }
        except Exception as e:
            return {'status': 500, 'message': str(e) }
    else:
        return {'status': 400, 'message': 'Method not allowed'}
    
@app.route("/deleteall", methods=['POST'])
def delete_all():
    if request.method == 'POST':
        try:
            # collection.delete_many({})
            taskdict.clear()
            taskid.clear()
            return {'status': 200, 'message': 'Success' }
        except Exception as e:
            return {'status': 500, 'message': str(e) }
    else:
        return {'status': 400, 'message': 'Method not allowed'}
        
if __name__ == '__main__':
    # thr = threading.Thread(target=scheduler, args=(), kwargs={})
    # thr.start()
    # print('threadstarted')
    app.run(debug=False, host='0.0.0.0')

