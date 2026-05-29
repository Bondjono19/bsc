'''

Abastract class that system integrations can use to pass on access decision.


'''

from abc import ABC, abstractmethod
class AccessGrantor(ABC):

    @abstractmethod
    def grantAccess(self,data: str):
        pass

class AccessGrantorExample(AccessGrantor):

    #Has no actual functionality as its an example
    def grantAccess(self, data):
        if(data):
            print(data)
        print("acces granted")
        #logic for connecting to system
        return
    

accessGrantorExample = AccessGrantorExample()