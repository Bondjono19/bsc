from recognition.accessGrantor import AccessGrantor
import requests
class AccessGrantorT8(AccessGrantor):

    def grantAccess(self, data):
        res = requests.post(url="https://webhook.site/90bca693-6dcb-46f0-b732-0c7b142ad9f5",json={"Name": data})
        print(res)