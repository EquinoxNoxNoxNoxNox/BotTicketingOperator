import datetime
import time
from threading import Timer
import re

from plugins.errors import *
from plugins.B_admin import getAdminByUid
from plugins import config
import plugins.B_users as users
import plugins.B_call as calls
import plugins.B_admin as admins

try:
    from pyrogram import Client , filters
    from pyrogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton

    from apscheduler.schedulers.background import BackgroundScheduler
except ModuleNotFoundError:
    import os
    os.system("pip install pyrogram")
    os.system("pip install apscheduler")
    os.system("pip install tinydb")
    print("\n\n\n\n\n\n\n\n\n\n\nRestart the program")
    quit()

bothash = "5545021461:AAGyzV5SWYlQsWhTmVGKkUDxb73vZ2NhpX8"
botClient = Client("support",api_id=2496,api_hash="8da85b0d5bfe62527e5b244c209159c3")

#Keyboards of admins
adminKeyBoards= {
    "start":[
            [KeyboardButton(text = config.Keyboard_Ready)],
            [KeyboardButton(text = config.Keyboard_CMDS)],
        ],
    "startCreset":[
            [KeyboardButton(text = config.Keyboard_Ready)], # ROW 1
            [KeyboardButton(text = config.Keyboard_CReset)] # ROW 2
        ],
    "OpenedConvo":[
            [KeyboardButton(text = config.Keyboard_Ready)],
            [KeyboardButton(text = config.Keyboard_Cancel)],
            [KeyboardButton(text = config.Keyboard_Close)]
        ],
    "SelectConvo":lambda callId : [
            [KeyboardButton(text = config.Keyboard_Accept.format(id=str(callId)))], # Row 1
            [KeyboardButton(text = config.Keyboard_Next.format(id=str(callId)))] # Row 2
        ],
    "adminVeryStart":[
            [KeyboardButton(text = config.Keyboard_Ready)],
            [KeyboardButton(text = config.Keyboard_CReset)],
            [KeyboardButton(text = config.Keyboard_CMDS)]
        ],
    "spamCallActions":lambda uid,callId : [
            [KeyboardButton(text = config.Keyboard_Close)],
            [KeyboardButton(text = f"/ban {str(uid)} , This action will be reported to the admin , it may have consequences for your job.")]
        ],
    
}

#######\#########/########
########\#######/#########
#########\ADMIN/##########
##########\###/###########
###########\#/############

#Ban a user
def ban(uid,t=2):
    _user = users.get(uid)
    calls.removeCall(_user.callId)
    botClient.send_message(chat_id = uid , text = "You are banned")
    users.setBan(uid,t)

#Unban a user
def unban(uid):
    botClient.send_message(chat_id = uid , text = "You have unbanend")
    users.removeBan(uid)

#RETURNS A DICTIONARY {}
def getConversation(callId)->dict:
    Messages = calls.getMessagesByCallId(callId)
    ButtonGetPhotos = InlineKeyboardMarkup([[InlineKeyboardButton(text="Get Files",callback_data=f"GetPhotosFromCallId-{str(callId)}")]])
    
    for Message in Messages:
        MatchedPhotoId = re.findall(r'фото(.*)фото', Message.Text)
        MatchedGifId = re.findall(r'гиф(.*)гиф', Message.Text)
        if(MatchedPhotoId):
            for pic in MatchedPhotoId:
                Message.Text = re.sub(pattern=r'фото.*фото'
                                    ,repl="Photo " + str(Messages.index(Message) + 1)
                                    ,string=Message.Text)
                Messages[Messages.index(Message)] = Message
        elif(MatchedGifId):
            for gif in MatchedGifId:
                Message.Text = re.sub(pattern=r'гиф.*гиф'
                                    ,repl="Gif " + str(Messages.index(Message) + 1)
                                    ,string=Message.Text)
                Messages[Messages.index(Message)] = Message
    _conversation = "".join([x.Text for x in Messages])
    res = {"conversation":_conversation,
           "fileButton" : ButtonGetPhotos}
    return res

#Send logs/reports to the main admin
def adminReport(uid,message,adminId=0):
    try:
        _rptxt = config.Text_logAdminMain.format(typeUser="admin" if adminId != 0 else "operator",uid = uid , text = message , time = " ".join(str(datetime.datetime.fromtimestamp(int(time.time()))).split("-")[1:]))
        
        if(adminId != 0):
            _rptxt = config.Text_logAdmin.format(text = message , time = " ".join(str(datetime.datetime.fromtimestamp(int(time.time()))).split("-")[1:]))
        
        botClient.send_message(chat_id=config.admins[adminId],text=_rptxt,reply_markup=ReplyKeyboardMarkup(adminKeyBoards["startCreset"] ,resize_keyboard=True))
    except Exception as e:
        raise e

####################################################################################
####################################################################################
#################################################################################### COMMANDS
#/cmd Sends list of commands for admin
@botClient.on_message((filters.command("cmds") | filters.command("help")) & filters.user(config.admins))
def commandsGuide(client,message):
    uid = message.from_user.id
    if(config.admins.index(int(uid))):
        message.reply_text(config.Text_HelpCmd + "\n /showDb for getting all the pool printed")
    else:
        message.reply_text(config.Text_HelpCmd)

#/getUser [UID]
@botClient.on_message(filters.command("getUser"))
def commandGetUserByUid(client,message):
    try:
        uid = message.command[1]
    except IndexError:
        message.reply_text("/getUser [uid]", quote=True)
        return
    message.reply_text(f"[CLICK TO OPEN THE PROFILE](tg://user?id={uid})")

#/getUID [username/'me']
@botClient.on_message(filters.command("getUID"))
def commandGetUserByUid(client,message):
    try:
        userName = message.command[1]
        if(userName == "me"):
            userId = message.from_user.id
            message.reply_text(f"{str(userId)}")
            return
        user = client.get_users([userName])
        if(len(user)):
            message.reply_text(f"{user[0].id}")
            return
        message.reply_text(f"{message.command[1]} doesn't exist", quote=True)
    except IndexError:
        message.reply_text("/getUID [username]", quote=True)
        return
    

#/getPhoto [fileId]
@botClient.on_message(filters.command("getPhoto") & filters.user(config.admins))
def commandGetPhoto(client,message):
    try:
        fileId = message.command[1]
        client.send_photo(chat_id = message.from_user.id,photo = fileId)
    except IndexError:
        message.reply_text("/getPhoto [fileId]")
    except Exception as e:
        adminReport(message.from_user.id , str.args(),admins.getAdminByUid(message.from_user.id)["uid"])

#/ban [uid]
@botClient.on_message(filters.command("ban") & filters.user(config.admins))
def commandAdminStart(client,message):
    try:
        adminUid = message.from_user.id
        try:
            uidToBan = message.command[1]
            ban(uidToBan)
        except IndexError:
            message.reply_text("/ban [uid]", quote=True)
            return
        botClient.send_message(
            chat_id=adminUid 
            ,text="User banned successfully" 
            ,reply_markup=ReplyKeyboardMarkup(
                adminKeyBoards["start"],resize_keyboard=True)
        )
        return
    except e_base as e:
        adminReport(adminUid , e.messageText)

#/unban [uid]
@botClient.on_message(filters.command("unban") & filters.user(config.admins))
def commandAdminStart(client,message):
    try:
        adminUid = message.from_user.id
        try:
            uid = message.command[1]
            unban(uid)
        except IndexError:
            message.reply_text("/unban [uid]", quote=True)
            return
        botClient.send_message(
            chat_id=adminUid 
            ,text="User unbanned successfully" 
            ,reply_markup=ReplyKeyboardMarkup(AdminKeyBoard["start"],resize_keyboard=True)
        )
        adminReport(adminUid , config.Text_AdminConvToUser.format(name="User",uid=uid,text="Has unbanned by that admin"))
        
    except e_base as e:
        adminReport(adminUid , e.messageText)

#/show db #PRINTS CALLS IN DB
@botClient.on_message(filters.command("showDb") & filters.user(config.admins))
def commandShowDb(client,message):
    calls.CMD_showCalls()
####################################################################################
####################################################################################
#################################################################################### COMMANDS END

#command admin /start
@botClient.on_message(filters.command("start") & filters.user(config.admins))
def commandAdminStart(client,message):
    try:
        uid = message.from_user.id
        _admin = admins.getAdminByUid(uid)
        
        botClient.send_message(chat_id=uid ,text=config.Text_adminStart.format(name = _admin["name"]) ,reply_markup=ReplyKeyboardMarkup(
            adminKeyBoards["adminVeryStart"]
            ,resize_keyboard=True))
        
    except Exception as e:
        raise e

#command admin /ready /next /cReset
@botClient.on_message((filters.command("ready") | filters.command("cReset") | filters.command("next")) & filters.user(config.admins))
def commandAdminReady(client,message):
    adminUid = message.from_user.id
    _a = admins.getAdminByUid(adminUid)
    if(message.command[0] == "next"):
        _a["cIds"].append(int(message.command[1]))
    if(message.command[0] == "creset"):
        _a["cIds"] = []
    admins.setAdmin(_a)
    try:
        _admin = admins.getAdminByUid(adminUid)
    
        try:
            callCurrent = calls.getAdminCurrentCall(_admin["id"])
            Messages = getConversation(callCurrent.id)
            client.send_message(chat_id=adminUid ,text=Messages["conversation"]
                                ,reply_markup=Messages["fileButton"])
                                #,reply_markup=ReplyKeyboardMarkup(adminKeyBoards["OpenedConvo"]))
            return
        except E_CallNotFound as e:
            callToPick = calls.getActive(_admin["cIds"])
                    
        try:
            _user = users.getByCallId(callToPick.id)
        except E_UserNotFound:
            calls.removeCall(callToPick.id)
            adminReport(0 ,"We have some irregularity in between MessagePool datas. User of the call is not registered within server.\nso , call with the Id "+str(callToPick.id)+"has been removed automatically" )
            return
    
        
        Messages = calls.getMessagesByCallId(callToPick.id)
        try: #TRY TO SHOW A MESSAGE DEMO/CALL TITLE/FIRST MESSAGE OF THE CALL
            MessageText=Messages[0].Text
            MatchedPhotoId = re.findall(r'фото(.*)фото', MessageText)
            MatchedGifId = re.findall(r'гиф(.*)гиф', MessageText)
            if(MatchedPhotoId):
                MessageText=re.sub(pattern=r'гиф.*гиф'
                      ,repl="__Gif__"
                      ,string=MessageText)
            elif(MatchedGifId):
                MessageText=re.sub(pattern=r'фото.*фото'
                        ,repl="__Pic__"
                        ,string=MessageText)
            botClient.send_message(chat_id=adminUid ,text=MessageText,reply_markup=ReplyKeyboardMarkup(adminKeyBoards["SelectConvo"](callToPick.id)))
        except IndexError:
            raise E_MessageNotFound("Theres no message in this call\n you can permit the following action (On the keyboard below): \n __BAN user__ Or __Close the call__")

    except E_MessageNotFound as e:
        client.send_message(chat_id=adminUid ,
                            text=e.messageText ,
                            reply_markup=ReplyKeyboardMarkup(adminKeyBoards["spamCallActions"](_user.uid,callToPick.id)))
    
    except e_base as e:
        adminReport(adminUid,e.messageText,admins.getAdminByUid(adminUid)["id"])

#command admin /accept [callId]
@botClient.on_message(filters.command("accept") & filters.user(config.admins))
def commandAdminAcceptCall(client,message):
    adminUid = message.from_user.id # Admin user id
    callId = message.command[1]
    _a = admins.getAdminByUid(adminUid)
    try:
        callToPick = calls.get(int(callId))
    except E_CallNotFound:
        client.send_message(chat_id = adminUid,text="callId "+ str(callId) +" is not available.",reply_markup=ReplyKeyboardMarkup(
            adminKeyBoards["start"]
        ))
        return
    try:
        _u = users.getByCallId(int(callId))
    except E_UserNotFound:
        calls.removeCall(callToPick.id)
        return
    try:
        Messages = getConversation(callToPick.id)
    except E_MessageNotFound as e:
        calls.removeCall(callToPick.id)
        adminReport(adminUid,e.textMessage,admins.getAdminByUid(adminUid)["id"])
        return

    if(callToPick.adminId):
        client.send_message(chat_id=adminUid ,text=Messages["conversation"]
                                ,reply_markup=config.Text_CallAlreadyOpen.format(uid=callToPick.adminId))
        return

    callToPick.status = 0
    callToPick.adminId = admins.getAdminByUid(adminUid)["id"]
    calls.setCall(callToPick,"commandAdminAcceptCall")

    client.send_message(chat_id=adminUid,
                        text=Messages["conversation"],
                        reply_markup = Messages["fileButton"])

    client.send_message(chat_id = adminUid,
        text=config.Text_callPickedAdmin,
        reply_markup=ReplyKeyboardMarkup(adminKeyBoards["OpenedConvo"])
    )
    calls.setMessage(calls.Message(callToPick.id,
                                   config.Text_adminOpenConv.format(name=_a["name"],
                                                                    uid=adminUid,
                                                                    message=message.text,
                                                                    time = " ".join(str(datetime.datetime.fromtimestamp(int(time.time()))).split("-")[1:])
                                                                   )))
    admins.setAdmin(_a)
    users.resetLimits(_u)

#SKIP THE CURRENT CALL
@botClient.on_message(filters.user(config.admins) & filters.command("skip"))
def commandAdminCancelCall(client,message):
    uid = message.from_user.id # Admin user id
    _admin = admins.getAdminByUid(uid)
    try:
        _c = calls.getAdminCurrentCall(_admin["id"])
    except E_CallNotFound:
        return
    _c.status = 1
    _c.adminId = None
    _admin["cIds"].append(_c.id)
    calls.setCall(_c,"commandAdminAcceptCall")
    botClient.send_message(chat_id=config.admins[_admin["id"]] 
        ,text=f"You have skipped the call , select ready to get the next opened call" 
        ,reply_markup=ReplyKeyboardMarkup(adminKeyBoards["start"])
    )

#CLOSE THE CURRENT CALL
@botClient.on_message(filters.user(config.admins) & filters.command("cancel"))
def commandAdminCloseCall(client,message):
    uid = message.from_user.id # Admin user id
    _admin = admins.getAdminByUid(uid)
    
    try:
        _c = calls.getAdminCurrentCall(admins.getAdminByUid(uid)["id"])
    except E_CallNotFound:
        try:
            _c = calls.get(int(message.command[1]))
        except IndexError:
            client.send_message(chat_id=config.admins[_admin["id"]] ,text=config.Text_adminStart.format(name = _admin["name"]))
            return
        
    _u = users.getByCallId(_c.id)
    
    _c.status = 0
    _c.adminId = None
    _u.callId = 0
    users.setUser(_u)
    calls.setCall(_c)
    client.send_message(chat_id=config.admins[_admin["id"]] 
                    ,text=config.Text_adminStart.format(name = _admin["name"])
                    ,reply_markup=ReplyKeyboardMarkup(adminKeyBoards["start"]))
    
#When admin respnose to call
@botClient.on_message(filters.incoming & filters.user(config.admins))
def messageAdminMessage(client,message):
    adminUid = message.from_user.id # Admin user id
    try:
        if(message.text[0] == "/"):
            return
        try:
            CurrentCall = calls.getAdminCurrentCall(admins.getAdminByUid(adminUid)["id"])
            _user = users.getByCallId(CurrentCall.id)
            client.send_message(
                chat_id=message.chat.id,
                text="Do you confirm this message to be send?",
                reply_to_message_id=message.message_id,
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="Confirm",callback_data=f"ConfirmMessageAdmin-{message.message_id}-{_user.uid}")],
                    [InlineKeyboardButton(text="Cancel",callback_data=f"ConfirmMessageAdmin-{message.message_id}")]
                ])
            )
            
        except E_UserNotFound as e:
            calls.removeCall(_c.id)
            message.reply(config.Text_logAdmin.format(text = e.messageText , uid = adminUid , time = str(datetime.datetime.fromtimestamp(int(time.time())))))
    except e_base as e:
        adminReport(adminUid,e.messageText,admins.getAdminByUid(adminUid)["id"])

#ADMIN MESSAGE CONFIRM CALLBACK
@botClient.on_callback_query(filters.regex(r'^ConfirmMessageAdmin-.*'))
def callBackMessageConfirm(client, callback_query):
    adminUid = callback_query.from_user.id # Admin user id
    mid = callback_query.message.message_id
    _MessageToSendId = callback_query.data.split("-")[1]
    try:
        UserToSendId = callback_query.data.split("-")[2]
    except IndexError:
        client.edit_message_text(chat_id = adminUid, message_id = mid, text = "Message canceled",reply_markup =[])
        return
    try:
        CurrentCall = calls.getAdminCurrentCall(admins.getAdminByUid(adminUid)["id"])
        CurrentAdmin = admins.getAdminByUid(adminUid)
        MessageToSend = client.get_messages(adminUid, int(_MessageToSendId))
        _user = users.getByCallId(CurrentCall.id)

        if(MessageToSend.photo):
            client.send_photo(chat_id = UserToSendId,photo = MessageToSend.photo.file_id)
            MessageToSend.text = MessageToSend.caption or f"фото{MessageToSend.photo.file_id}фото"
        elif(MessageToSend.animation):
            client.send_animation(chat_id = UserToSendId,animation = MessageToSend.animation.file_id)
            MessageToSend.text = MessageToSend.caption or f"гиф{MessageToSend.photo.file_id}гиф"
        
        if(MessageToSend.text):
            client.send_message(chat_id = UserToSendId , text = MessageToSend.text)
        else:
            client.edit_message_text(chat_id = adminUid, message_id = mid, text = config.Text_FileInvalid,reply_markup =[])
            return
        
        calls.setMessage(calls.Message(CurrentCall.id,config.Text_AdminConvToUser.format(name=CurrentAdmin["name"],
                                                                                         uid=adminUid,
                                                                                         text=MessageToSend.text)))
        client.edit_message_text(chat_id = adminUid, message_id = mid, text = "Message sent successfully",reply_markup =[])
    except Exception as e:
        raise e
        adminReport(adminUid,str(e.args))

#ADMIN GET PHOTOS SENT IN A CALL
@botClient.on_callback_query(filters.regex(r'^GetPhotosFromCallId-.*'))
def callBackGetPhoto(client, callback_query):
    CallId = callback_query.data.split("-")[1]
    MessagesToGetPicsFrom = calls.getMessagesByCallId(int(CallId))
    for Message in MessagesToGetPicsFrom:
        PhotoIds = re.findall(r'фото(.*)фото', Message.Text)
        GifIds = re.findall(r'гиф(.*)гиф', Message.Text)
        if(GifIds):
            _gifCounter = 0
            for gif in GifIds:
                _gifCounter += 1
                client.send_animation(chat_id = callback_query.from_user.id,
                                  caption = f"{str(MessagesToGetPicsFrom.index(Message) + 1)}",
                                  animation = gif)
        if(PhotoIds):
            for pic in PhotoIds:
                client.send_photo(chat_id = callback_query.from_user.id,
                                  caption = f"{str(MessagesToGetPicsFrom.index(Message) + 1)}",
                                  photo = pic)

###########/#\###########
##########/###\##########
#########/#USER\#########
########/#######\########
#######/#########\#######

#Filter for avoiding users that are banned , base for all user custom filters
def filterBanned(uid) -> bool:
    res = users.isBan(uid)
    return res

#Filter for avoiding users with already saved Call; returns false if user have a Call or Banned
def filterUserCall(uid) -> bool:
    if(filterBanned(uid)):
        return False
    try:
        _u = users.get(uid)
        if _u.cLimit == 5:
            botClient.send_message(
                chat_id = uid,
                text = config.Text_userWarnBan.format(attempt = str(5))
            )
        if _u.cLimit >= 10:
            ban(uid,1)
            adminReport(uid,"user is banned due over-usage of command '/start' (call)")
            return False
        if(_u.callId):
            botClient.send_message(chat_id = uid , text = config.Text_userAlreadyOpenConv)
            _u.cLimit += 1
            users.setUser(_u)
            return False
        return True
    except E_UserNotFound:
        return True

#User message spam filter
def filterUserMessage(_,__,message):
    uid = message.from_user.id 
    try:
        try:
            _u=users.get(uid)
        except E_UserNotFound:
            message.reply("Use /start to start a new conversation then re-send your message.")
            return False
        
        if(message.text != None and not message.photo):
            if(10>len(message.text)):
                botClient.send_message(chat_id = uid,
                                    text="Your message should atleast contain 10 characters")
                return False
        
        isban = filterBanned(uid)
        if(isban):
            return False
        if(_u.mLimit == 5):
            botClient.send_message(
                    chat_id = uid,
                    text = config.Text_userWarnBan.format(attempt = str(5))
                )

            _u.mLimit += 1
            users.setUser(_u)
            return False
        elif(_u.mLimit > 10):
            ban(_u.uid,0)
            adminReport(_u.uid,"User banned becuz of spam without call")
            return False
        _u.mLimit += 1
        users.setUser(_u)
        return True
    except e_base as e:
        adminReport(uid, e.messageText)

#User start 
@botClient.on_message(filters.command("start"))
def commandUserStart(client,message) -> None:
    uid=message.from_user.id
    if(filterUserCall(uid)==False):
        return
    try:
        _user = users.get(uid)
    except E_UserNotFound:
        _user = users.setUser(users.User(uid))
    
    try:
        _call = calls.get(_user.callId)
        _user.callId = _call.id
    except E_CallNotFound:
        _call  = calls.setCall(calls.Call())

    _user.callId = _call.id
    users.setUser(_user,"User call added")
    client.send_message(chat_id = uid
                        ,text=config.Text_userStart.format(fname=message.from_user.first_name)
                        ,reply_markup = [])

ftc = filters.create(filterUserMessage)
# ANSWER USER AFTER BOT FAKE TYPINGs OVER
_isConfirmedMessage = True
def sendCallSuccessFunction(uid,text):
    global _isConfirmedMessage
    if(_isConfirmedMessage):
        botClient.send_chat_action(uid, "cancel")
        botClient.send_message(chat_id = uid,text = text)
    _isConfirmedMessage = False
    return

#user message
@botClient.on_message(ftc)
def messageUser(client,message):
    global _isConfirmedMessage
    uid = message.from_user.id
    photos = []
    gifs = []
    if(message.photo):
        photos.append(message.photo.file_id)
        message.text="\n".join(["фото" + x + "фото " for x in photos]) + (message.caption or "")
        
    if(message.animation):
        gifs.append(message.animation.file_id)
        message.text="\n".join(["гиф" + x + "гиф " for x in gifs]) + (message.caption or "")
    if(message.audio or message.document or message.sticker or message.game or message.video or message.voice):
        client.send_message(chat_id = uid,text=config.Text_FileInvalid)
        return
    _user = users.get(uid)
    
    try:
        _call = calls.get(_user.callId)
    except E_CallNotFound:
        message.reply("Use /start to start a new conversation")
        return

    try:
        calls.setMessage(calls.Message(_call.id,config.Text_newCallMessage.format( #SAVIGN A NEW MESSAGE TO POOL
            type = "user" , 
            uid = str(uid) ,
            time = " ".join(str(datetime.datetime.fromtimestamp(int(time.time()))).split("-")[1:]),
            text = message.text
        )),"messageUser")
        
        _isConfirmedMessage = True
        client.send_chat_action(uid, "typing")
        _textSuccess = config.Text_usesSuccessCall.format(mid = str(uid) + str(_call.id))
        t = Timer(2.0, sendCallSuccessFunction , [uid,_textSuccess])
        t.start()
    except e_base as e:
        adminReport(uid,e.messageText)


check_point_timer = BackgroundScheduler({
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '10',
    'apscheduler.timezone': 'UTC',
})
check_point_timer.add_job(calls.PoolDrain, "interval", seconds=60)
check_point_timer.start()

print("Client connected")
botClient.run()