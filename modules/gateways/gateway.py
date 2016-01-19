__author__ = 'majidkabir'

class Gateway:

    def send(self, sms):
        msgid = self.send_sms(sms)
        # TODO: Adding this msgid to redis for future use
        return msgid