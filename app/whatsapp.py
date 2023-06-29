import base64
import json
import os.path
import threading
import time
from datetime import datetime
from mimetypes import guess_extension
from multiprocessing import Process
from pathlib import Path
from typing import List, Dict

from javascript import require, On

import qrcode

from app.models import Messages, Customers, Settings
from database import Session


# Обертка node <-> python
# https://pypi.org/project/javascript/
# https://github.com/extremeheat/JSPyBridge
# Whatsapp-Web
# https://github.com/pedroslopez/whatsapp-web.js


class WhatsApp:
    __instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.__instance = super(WhatsApp, cls).__new__(cls)
            cls.__instance.__initialized = False
            print(threading.get_ident())
        return cls.__instance

    def __del__(self):
        print('wa close')
        self.update_setting({})
    def get_setting(self):
        res = self.session.query(Settings).filter(Settings.name == Settings.WA_CLIENT).all()
        if not res:
            return self.update_setting({})
        else:
            return res[0]

    def update_setting(self, setting: Dict):
        if not hasattr(self, "session"):
            return
        s = self.session.query(Settings).filter(Settings.name==Settings.WA_CLIENT).all()
        if not s:
            s = Settings(name=Settings.WA_CLIENT, value=setting)
            self.session.add(s)
            self.session.commit()
            return s
        else:
            s[0].value = setting
            self.session.commit()
            return s

    def init_app(self, app):
        self.session = app.session
        self.update_setting({'date': str(datetime.now()), 'started': False})

    def start(self):
        s = self.get_setting()
        if s.value['started']:
            return
        self.media_path_name = 'Media'
        self.media_path = Path(self.media_path_name)
        if not self.media_path.is_dir():
            self.media_path.mkdir()
        self.update_setting({'date': str(datetime.now()), 'started': False})
        self.session = None
        self.proc = threading.Thread(target=self.start_client)
        self.proc.start()

        # return
    def start_client(self):
        self.ready = False
        self.session = Session()
        Client = require('whatsapp-web.js').Client
        LocalAuth = require('whatsapp-web.js').LocalAuth
        # self.session = session
        self.client = Client({
            'authStrategy': LocalAuth()
        })

        @On(self.client, 'qr')
        def qr(this, code):
            print('scan code')
            self.update_setting({'qrcode':code, 'date':str(datetime.now()), 'started':False})
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
            self.update_setting({'date':str(datetime.now()), 'started':True})
            print('client ready')
            # self.read_messages()

        # messages = my_chat.fetchMessages({'limit':'Infinity'})
        # message = my_chat.sendMessage("test")

        self.client.initialize(timeout=1500)
        print("wa initialized")

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

    def logout(self):
        self.client.logout()
    def login(self):
        self.client.initialize(timeout=1500)

    def read_messages(self):
        counters = {
            'new_messages': 0,
            'new_customers': 0,
            'upd_messages': 0,
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
        messages = my_chat.fetchMessages({'limit': 500})
        # print(messages)

        for i, message in enumerate(messages):
            links = message.links
            (quoted, media,media_key) = (None, None, None)
            if message.hasQuotedMsg:
                quoted = message.getQuotedMessage()
            if message.hasMedia:
                media = message.downloadMedia(timeout=500) #mimetype: 'image/jpeg', data: (base64?data); mimetype: 'application/pdf', data: (base64?data)
            media_key = message.mediaKey
            if any([links, quoted, media, media_key]):
                t=0
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

            def get_props(message):
                props = {}
                if message.hasMedia:
                    media = message.downloadMedia(
                        timeout=500)  # mimetype: 'image/jpeg', data: (base64?data); mimetype: 'application/pdf', data: (base64?data)
                    if media:
                        ext = guess_extension(media.mimetype)
                        filename = Path(self.media_path, message.id._serialized+ext)
                        with open(filename, 'wb') as f:
                            f.write(base64.b64decode(media.data.encode('utf-8')))
                        props['media'] = {
                            'mimetype': media.mimetype,
                            'file': str(filename)
                        }
                if len(list(message.links)) > 0:
                    props['links'] = list(message.links)
                return props

            msg = self.session.query(Messages).filter_by(wa_id=message.id._serialized).all()
            if not msg:
                msg = Messages(wa_id=message.id._serialized, customer_id=cust.id, timestamp=t, text=message.body)
                msg.props = get_props(message)
                if message.hasQuotedMsg:
                    quoted = self.session.query(Messages).filter_by(wa_id=message.getQuotedMessage().id._serialized).first()
                    if quoted:
                        msg.quoted_id = quoted.id
                        self.session.add(msg)
                        self.session.commit()
                counters['new_messages'] += 1
            else:
                if message.hasQuotedMsg:
                    qt_msg = message.getQuotedMessage()
                    quoted = self.session.query(Messages).filter_by(wa_id=qt_msg.id._serialized).first()
                    # if not quoted:
                        # error Class 'builtins.list' is not mapped
                        # get customer_id
                        # quoted = Messages(wa_id=qt_msg.id._serialized, customer_id=cust.id, timestamp=t,
                        #                text=qt_msg.body)
                        # self.session.add(msg)
                        # self.session.commit()
                    if quoted:
                        msg[0].quoted_id = quoted.id
                        self.session.commit()
                props = get_props(message)
                if len(props) > 0:
                    if msg[0].props:
                        props = {**props, **msg[0].props}
                    msg[0].props = props
                    self.session.commit()
                    counters['upd_messages'] += 1
                self.save_process(counters)
                print('\r' + str(i), end='')
        counters['success'] = True
        return counters

    def save_process(self, process):
        setting = self.session.query(Settings).filter(Settings.name == 'process').first()
        if not setting:
            setting = Settings(name = 'process', value = process)
            self.session.add(setting)
        else:
            setting.value = process
        self.session.commit()


if __name__ == "__main__":
    w = WhatsApp()
    time.sleep(15)
    w.read_messages()
