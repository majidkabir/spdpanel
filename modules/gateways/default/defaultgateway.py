from applications.spdpanel.modules.gateways.gateway import Gateway
from gluon import *

__author__ = 'majidkabir'

from suds.client import Client


class DefaultGateway(Gateway):
    """
     This is a default gateway that send sms through a webservice
     Some of the parameters this webservice needs for sending sms is in configuration file 'appconfig.ini'
     that this class load in initialization and other parameters sent from application
     appconfig.ini section
     [default_gateway]
     username = user
     password = pass
     domain = domain
     wsdl = http://example.com/Sendsms?wsdl
    """

    name = 'default_gateway'


    def __init__(self):
        """
        Initializing default gateway by persistence parameters from appconfig.ini
        """
        self.username = current.myconf.take(self.name + '.username')
        self.password = current.myconf.take(self.name + '.password')
        self.domain = current.myconf.take(self.name + '.domain')
        self.client = Client(current.myconf.take(self.name + '.wsdl'))

    def send_sms(self, sms):
        """
        Calling webservice for sending sms
        :param sms: contains sms parameters
        :return: msg_id or error
        """
        msgid = self.client.service.serviceSend(username = self.username,
                                                 password = self.password,
                                                 domain= self.domain,
                                                 messages = sms['message'].decode('utf-8'),
                                                 destinations= sms['to'],
                                                 originators = sms['sender'],
                                                 serviceId = sms['sid'])
        return msgid