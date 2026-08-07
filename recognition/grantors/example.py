from recognition.accessGrantor import AccessGrantor

class AccessGrantorExample(AccessGrantor):

    #Has no actual functionality as its an example
    def grantAccess(self, data):
        if(data):
            print(data)
        print("Access grantor implementation invoked - acces granted")
        #logic for connecting some system
        return