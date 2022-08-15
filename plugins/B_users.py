from tinydb import TinyDB , Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from time import time
from . import errors

users = TinyDB("resources/users.json", storage=CachingMiddleware(JSONStorage))

banned = TinyDB("resources/bannedUsers.json" , storage=CachingMiddleware(JSONStorage))

banTypes = [
    "Spam without call",
    "Spam with call",
    "admin ban"
]
q = Query()

class User:
    callId=0 # Id of a call in pool
    uid=0 # User id of user in telegram
    cLimit = 0 # Number of call attempts, this will warn in 5 and bans in 10
    mLimit = 0 # Number of messages sent to a call , this will warn in 10 and bans in 20

    def __init__(self,uid,callId=0,cLimit=0,mLimit=0) -> None:
        self.uid = uid
        self.callId = callId
        self.cLimit = cLimit
        self.mLimit = mLimit

    def getValues(self):
        return {"uid":self.uid,"callId" : self.callId,"mLimit":self.mLimit,"cLimit":self.cLimit}

#Check if uid is in banend ones
def isBan(uid) -> bool:
    _ = banned.all()
    return uid in _

#Set a uid in banneds
def setBan(uid,type) -> None:
    banned.insert({uid:type})

#Set a uid in banneds
def removeBan(uid) -> None:
    _ = banned.all()
    for i in range(len(_)):
        if(_[i]["uid"] == uid):
            banned.remove(doc_ids = [_[i].doc_id])

#get user from db
def get(uid) -> User:
    try:
        res = users.search(q.uid == uid)[0]
        return User(uid = res["uid"], callId = res["callId"], cLimit= res["cLimit"], mLimit=res["mLimit"])
    except IndexError:
        raise errors.E_UserNotFound(f"user with the uid {str(uid)} not found in db")

#add user to db
def setUser(param : User,z="") -> User:
    val = param.getValues()
    res = users.update(val,q.uid == val["uid"])
    if(res):
        return param
    users.insert(param.getValues())
    return param

#get user by call id
def getByCallId(callId) -> User:
    try:
        if(callId == 0):
            raise IndexError("CallId is not valid")
        callId = int(callId)
        res = users.search(q.callId == callId)[0]
        return User(uid = res["uid"], callId = res["callId"], cLimit= res["cLimit"], mLimit=["mLimit"])
    except IndexError:
        raise errors.E_UserNotFound(f"user with call id {str(callId)} not found in db")

def resetLimits(param : User):
    param.cLimit = 0
    param.mLimit = 0
    setUser(param)