from threading import Thread
import traceback
from applications.spdpanel.modules.gateways.gatewaymanager import GatewayManager

__author__ = 'majidkabir'

import pika
import sys
from gluon import *

try:
    import cPickle as pickle
except:
    import pickle


class QueueManager:
    def __init__(self):
        self.gateway_manager = GatewayManager()

        self.sms_queue = 'sms_queue'
        self.sms_exchange = 'sms_exchange'
        # self.requeue_ids = current.myconf.take('')

        # This channel created for adding sms to queue
        sms_producer_channel = self.__create_channel(queue=self.sms_queue, exchange=self.sms_exchange)
        self.sms_producer_channel = sms_producer_channel


        # This channel created for consuming sent sms
        sms_consumer_channel = self.__create_channel(queue=self.sms_queue, exchange=self.sms_exchange)
        sms_consumer_channel.basic_consume(self.__sms_callback,
                                           queue=self.sms_queue)

        thread = Thread(target=self.sms_consumer_loop, args=(sms_consumer_channel,))
        thread.start()

    def sms_consumer_loop(self, channel):
        channel.start_consuming()
        print "OK"

    def __create_channel(self, queue, exchange):
        # Reading rabbitmq configs from appconfig.ini
        # if this configs not defined in appconfig.ini default config will be used
        # [rabbitmq] scop
        host = current.myconf.take("rabbitmq.host") or 'localhost'
        port = int(current.myconf.take("rabbitmq.port") or '5672')
        username = current.myconf.take("rabbitmq.username") or 'guest'
        password = current.myconf.take("rabbitmq.password") or 'guest'

        # Reading consumer config from appcongig.ini
        # if this configs not defined in appconfig.ini default config will be used
        # [sms_consumer] scope
        number_of_consumer = current.myconf.take("sms_consumer.number_of_consumer") or 1

        cred = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=cred))

        channel = connection.channel()
        channel.exchange_declare(exchange=exchange,
                                 type='topic')
        channel.queue_declare(queue,
                              durable=True)
        channel.queue_bind(exchange=exchange,
                           queue=queue,
                           routing_key="#")
        return channel

    def send_sms(self, sms):
        self.sms_producer_channel.basic_publish(exchange=self.sms_exchange,
                                                routing_key="",
                                                body=sms)

    def __sms_callback(self, ch, method, properties, body):
        """
        Consume sms from queue
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        # try:
        msgid = 0
        sms = pickle.loads(body)
        # print (sms)
        gateway = self.gateway_manager.select_gateway(sms)
        msgid = gateway.send_sms(sms)
        print msgid
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # TODO: add exception for pickle.load for removing this sms from queue
        # except:
        #     # TODO: logger must be added
        #     print "Error"
        #     traceback.print_exc(file=sys.stdout)
        #     pass
