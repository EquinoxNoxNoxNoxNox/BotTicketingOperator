from time import time
from . import errors , config

admins =[
    {
        "id":0,
        "name" : "first admin",
        "cIds" : []
    },
    {
        "id":1,
        "name" : "second admin",
        "cIds" : []
    }
]

#Get admin by given uid
def getAdminByUid(uid:int) -> dict:
    try:
        return [x for x in admins if x["id"]==config.admins.index(uid)][0]
    except IndexError or ValueError:
        raise errors.E_AdminNotFound("Admin is not been set in admins dict file , /plugins/B_admin.py")

#Set admin cancel calls
def setAdmin(param:dict) -> None:
    try:
        for a in admins:
            if a["id"] == param["id"]:
                for _ in a.keys():
                    a[_] = param[_]

    except KeyError:
        _ = {}
        for key in param.keys():
            _[key] = param[key]
    