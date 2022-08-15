from tinydb import TinyDB , Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import json
import time
import datetime
from . import errors

db = TinyDB("resources/messagePool.json", storage=CachingMiddleware(JSONStorage))

q = Query()


class Call():
    """
    REPRESENT A DATA MODEL FOR CALL
    """
    _="call"
    id = 0 # Id of call in pool
    status = 1 # status is wether call is open or occupied. 1 open , 0 occupied by an admin
    adminId = None # id of the admin that is taking the call
    createDate = int(time.time()) # create date of the call
    def __init__(self, status=1,adminId = None , id=0 , createDate=0) -> None:
        self.id = id
        self.status = status
        self.adminId = adminId
        self.createDate = createDate | self.createDate
    
    def getValues(self) -> dict:
        return {"id" : self.id , "status" : self.status, "adminId" : self.adminId, "createDate" : self.createDate,"_":self._}
    #RETURNS THE DATA IN JSON FORMAT
    def __str__(self) -> str:
        res = json.dumps(self.getValues())
        return res
        #return f'{{"id":{self.id},"status" : {self.status}, "adminId":{self.adminId},"createDate" : {self.createDate},"_":{self._}}}'

class Message():
    """
    REPRESENT A DATA MODEL FOR MESSAGE
    """
    _="message"
    CallId = 0 # Relational callId
    Text = "" # Text of the message. it may contain FileId of the uploaded photos form user
    def __init__(self ,CallId,Text) -> None:
        #Id of call
        self.CallId = CallId
        self.Text = Text
    
    def getValues(self) -> dict:
        return {"CallId":self.CallId,"Text":self.Text,"_":self._}
    #RETURNS THE DATA IN JSON FORMAT
    def __str__(self) -> str:
        res = json.dumps(self.getValues())
        return res

#Print calls in cmd (for debug purposes)
def CMD_showCalls():
    for i in db.search(q._=="call"):
        print(i)

#add or update a new message object in pool
def setMessage(param:Message,z=""):
    if(param.CallId==0):
        raise errors.E_CallNotFound("Call not found for the message")

    db.insert(param.getValues())
    return param

#Get a message object by call id
def getMessagesByCallId(callId) -> list:
    _res = []
    if(callId == 0):
        raise IndexError()
    Messages = db.search(q._ == "message" and q.CallId == callId)
    for i in Messages:
        if(i["CallId"] == callId):
            _res.append(Message(CallId=i["CallId"],Text=i["Text"]))
    return _res

def get(_id)->Call:
    _id = int(_id)
    try:
        if(_id == 0):
            raise IndexError("dont")
        res = db.search(q._ == "call" and q.id==_id)[0]
        return Call(status = res["status"], adminId=res["adminId"], id = int(res["id"]),createDate=res["createDate"])
    except IndexError:
        raise errors.E_CallNotFound(f"there are no calls with id {str(_id)} ")

# PRECURSOR FOR UPDATE TINYDB
def _updateCall(val):
    def update(doc):
        if(doc["id"] == val["id"]):
            for key in doc.keys(): # THERE IS A 'None' VALUE IN BETWEEN SO I COULDN'T USE dict.update() METHOD
                doc[key] = val[key]
    return update

def setCall(param:Call,z="") -> Call: # CALL
    val = param.getValues()
    if(param.id != 0):
        #res = db.upsert(val,q.id == val["id"] and q._ == "call")
        res = db.update(_updateCall(val),q._ == "call")
        if(res):
            return param
    else:
        try:
            LastRow = db.search(q._ == "call")[-1]
            param.id = LastRow["id"] + 1
        except IndexError: # IF THERE IS NO LAST ROW
            param.id = 1
        db.insert(param.getValues())
        return param

#This method will be called each 3/6/12 hours for clearing the data pool
def PoolDrain():
    ClosedCalls=[]
    try:
        with open("../public/savedPool.txt", "a+") as savedPoolFile:
            for poolObject in db.all():
                if(poolObject["_"] == "call"): # IF CURRENT poolObject IS A CALL
                    if(not poolObject["status"] and not poolObject["adminId"]): # IF CALL IS CLOSED
                        ClosedCalls.append(poolObject["id"])
                        removeCall(poolObject["id"])
                        ObjectToWrite = Call(poolObject["status"],
                                poolObject["adminId"],
                                poolObject["id"],
                                createDate=poolObject["createDate"])
                    else:
                        continue
                else: # IF CURRENT poolObject IS A MESSAGE
                    if(poolObject["CallId"] in ClosedCalls): # CHECK IF MESSAGE IS RELATED TO THE CALL
                        ObjectToWrite = Message(poolObject["CallId"],
                                                poolObject["Text"])
                    else:
                        continue
            savedPoolFile.write(str(ObjectToWrite)+",")
    except:
        pass
    

#get calls with open status
def getActive(adminCAncel=[]) -> Call:
    _ = db.search((q.status == 1) & (q._ == "call"))
    # print("*************************GET")
    # print(_)
    # print("*************************GETEND")
    try:
        return [Call(x["status"],x["adminId"],x["id"],createDate=x["createDate"]) for x in _ if x["id"] not in adminCAncel][0]
    except IndexError:
        raise errors.E_CallNotFound(f"There are no other calls\nYou skipped : {str(len(adminCAncel))}")

#Get admin open call
def getAdminCurrentCall(adminId) -> Call:
    _ = db.search((q.adminId == adminId) & (q.status == 0))
    try:
        return [Call(x["status"],x["adminId"],x["id"],createDate=x["createDate"]) for x in _][0]
    except IndexError:
        raise errors.E_CallNotFound("No active call for admin")

#remove call from pool
def removeCall(id):
    db.remove((q.id == id) | (q.callId == id))
    