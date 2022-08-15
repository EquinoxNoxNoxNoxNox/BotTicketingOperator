class e_base(Exception):
    messageText = ""
    def __init__(self,message="") -> None:
        self.messageText = message

#when user is silenced
class E_IsSilence(e_base):
    def __init__(self, message="") -> None:
        super().__init__(message)

#shen user is not found in resource 
class E_UserNotFound(e_base):
    def __init__(self, message="") -> None:
        super().__init__(message)

#when callId is not set for a specific user
class E_CallNotFound(e_base):
    def __init__(self, message="") -> None:
        super().__init__(message=message)

#when there are no message for a specific callId
class E_MessageNotFound(e_base):
    def __init__(self, message="") -> None:
        super().__init__(message=message)

#when user is banned in filter
class E_RunTimeBanned(e_base):
    def __init__(self, message="") -> None:
        super().__init__(message=message)

#when admin not found in database
class E_AdminNotFound(e_base):
    def __init__(self, message="") -> None:
        super().__init__(message=message)