import json
import time
from datetime import datetime
from typing import List

from javascript import require, On

import qrcode

from app.models import Messages, Customers
from database import Session

#Обертка node <-> python
#https://pypi.org/project/javascript/
#https://github.com/extremeheat/JSPyBridge
#Whatsapp-Web
#https://github.com/pedroslopez/whatsapp-web.js

class WhatsApp:
    def __init__(self, session):
        self.ready = False
        Client = require('whatsapp-web.js').Client
        LocalAuth = require('whatsapp-web.js').LocalAuth
        self.session = session
        self.client = Client({
            'authStrategy': LocalAuth()
        })

        @On(self.client, 'qr')
        def qr(this, code):
            print('scan code')
            img = qrcode.make(code)
            type(img)  # qrcode.image.pil.PilImage
            img.save("some_file.png")

        @On(self.client, 'message')
        def message(this, msg):
            if msg.body == '!ping':
                msg.reply("pong")

        @On(self.client, 'ready')
        def ready(*args):
            self.ready = True
            print('client ready')
            # self.read_messages()

        # messages = my_chat.fetchMessages({'limit':'Infinity'})
        # message = my_chat.sendMessage("test")

        self.client.initialize(timeout=1500)

    def read_messages(self):
        counters = {
            'new_messages': 0,
            'new_customers':0,
            'success': False
        }
        if not self.ready:
            return counters
        chats = self.client.getChats()
        # name = 'моё'
        name = 'Ягоды из Сербии в Чехове'
        my_chat = None
        for chat in chats:
            if chat.name == name:
                my_chat = chat
                break
        messages = my_chat.fetchMessages({'limit': 50})
        # print(messages)

        for i, message in enumerate(messages):
            t = datetime.utcfromtimestamp(message['timestamp'])
            cust = self.session.query(Customers).filter_by(wa_id=message['author']).all()
            if not cust:
                sender = message.getContact()
                cust = Customers(wa_id=sender.id._serialized, name=sender.name, number=sender.number,
                                 short_name=sender.shortName, push_name=sender.pushname)
                self.session.add(cust)
                self.session.commit()
                counters['new_customers'] += 1
            else:
                cust = cust[0]
            msg = self.session.query(Messages).filter_by(wa_id=message.id._serialized).all()
            if not msg:
                msg = Messages(wa_id=message.id._serialized, customer_id=cust.id, timestamp=t, text=message.body)
                self.session.add(msg)
                self.session.commit()
                counters['new_messages'] += 1
        counters['success'] = True
        return counters


if __name__ == "__main__":
    w = WhatsApp(Session())
    time.sleep(15)
    w.read_messages()
