'''

Abastract class that system integrations can use to pass on access decision.


'''

from abc import ABC, abstractmethod
from typing import JSON
class AccessGrantor(ABC):

    @abstractmethod
    def grantAccess(self,data: JSON):
        pass

class AccessGrantorExample(AccessGrantor):

    #Has no actual functionality as its an example
    def grantAccess(self, data):
        print(data)
        #logic for connecting to system
        return
    

accessGrantorExample = AccessGrantorExample()