'''

Abastract class that system integrations can use to pass on access decision.


'''

from abc import ABC, abstractmethod
class AccessGrantor(ABC):

    @abstractmethod
    def grantAccess(self,data: str):
        pass
