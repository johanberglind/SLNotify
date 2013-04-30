import httplib, urllib


class Pushover(object):

    def __init__(self):
        pass


    def Send(self, token, user, message):
        self.mycon = httplib.HTTPSConnection("api.pushover.net:443")
        self.mycon.request("POST", "/1/messages.json",
        urllib.urlencode({
            "token": "{}".format(token),
            "user": "{}".format(user),
            "message": "{}".format(message),
            }), { "Content-type": "application/x-www-form-urlencoded" })
        self.data = self.mycon.getresponse()
        self.mycon.close()
        return (self.data)




