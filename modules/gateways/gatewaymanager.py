__author__ = 'majidkabir'

from applications.spdpanel.modules.gateways.default.defaultgateway import DefaultGateway

class GatewayManager:
    list_of_gateways = [];

    def __init__(self):
        gateway = DefaultGateway()
        self.list_of_gateways.append(gateway)
        pass

    def select_gateway(self, sms):
        gateway = None
        if len(self.list_of_gateways) > 0 :
            gateway = self.list_of_gateways[0]
        return gateway
