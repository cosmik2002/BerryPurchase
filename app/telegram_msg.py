import asyncio
import json
import os
import threading
from datetime import datetime
from random import random
from typing import Dict

from sqlalchemy.orm import scoped_session
from telegram import Update, Message
from telegram.ext import Updater, CommandHandler, ContextTypes, ApplicationBuilder, MessageHandler, filters

import database

import requests
import simplejson
import telebot
# from telebot.types import Message
from app.models import Messages, Customers, Settings


class BerriesBot:

    __instance = None
    application = None
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.__instance = super(BerriesBot, cls).__new__(cls)
            cls.__instance.__initialized = False
            print('tg_new')
        return cls.__instance

    def __init__(self):
        self.counters = {}
        self.session = database.SessionLocal
        self.key = os.getenv('TELEGRAM_BOT')
        self.x = random()
        print(f'tg init rand-x-{self.x}  threading.get_ident {threading.get_ident()}')
        # self.update_setting({'date': str(datetime.now()), 'started': 0, 'status': 0})
        self.bot = telebot.TeleBot(self.key)  # berries188bot

    def __del__(self):
        print(f'tg close {self.x} ' + str(threading.get_ident()))
        if self.application:
            self.application.shutdown()
            self.update_setting({})

    def get_setting(self):
        res = self.session.query(Settings).filter(Settings.name == Settings.TELEGRAMM).all()
        if not res:
            return self.update_setting({})
        else:
            return res[0]

    def update_setting(self, setting: Dict):
        if not hasattr(self, "session"):
            return
        s = self.session.query(Settings).filter(Settings.name == Settings.TELEGRAMM).all()
        if not s:
            s = Settings(name=Settings.TELEGRAMM, value=setting)
            self.session.add(s)
            self.session.commit()
            return s
        else:
            s[0].value = setting
            self.session.commit()
            return s

    def init_app(self, app):
        self.session = app.session
        self.update_setting({'date': str(datetime.now()), 'started': 0, 'status': 0})

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        cust = self.getCustomer(update.message)
        msg_date = update.message.date  # .strftime('%Y-%m-%d %H:%M:%S')
        chat_id = update.effective_chat.id
        text = update.message.text
        user_id = update.message.from_user.id
        msg = Messages(wa_id=str(chat_id) + "_" + str(update.message.message_id),
                       from_id=user_id,
                       customer_id=cust.id,
                       chat_id=chat_id,
                       timestamp=msg_date,
                       text=text)
        self.session.add(msg)
        self.session.commit()
        print(str(chat_id) + "_" + str(update.message.message_id) + text)
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    def stop(self):
        self.application.shutdown()
    def start_polling(self):
        s = self.get_setting()
        if 'started' in s.value:
            return
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.update_setting({'date': str(datetime.now()), 'started': 0, 'status': 0})
        self.application = ApplicationBuilder().token(self.key).build()
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.echo)

        self.application.add_handler(echo_handler)
        self.application.run_polling()
        print("Polling started")

    def getCustomer(self, message:Message) -> Customers:
        cust = self.session.query(Customers).filter_by(wa_id=message.from_user.id).all()
        if not cust:
            cust = Customers(wa_id=message.from_user.id, name=message.from_user.full_name, number=message.from_user.username)
            self.session.add(cust)
            self.session.commit()
            self.counters['new_customers'] += 1
        else:
            cust = cust[0]
        return cust

    def getUpdates(self):
        self.counters = {
            'new_messages': 0,
            'new_customers': 0,
            'upd_messages': 0,
            'success': False
        }
        updates = self.bot.get_updates()#(self.bot.last_update_id + 1),
                                       #timeout=1, long_polling_timeout=1)
        # with open('updates.json', 'w') as fp:
        #     simplejson.dump(updates, fp)
        # exit(0)

        for upd in updates:
            if upd.channel_post is not None:
                message: Message = upd.channel_post
                # self.process_channel_msg(message, upd)
            else:
                message: Message = upd.message or upd.edited_message
            chat_id = message.chat.id
            if chat_id != -1001788039692:
                continue
            if message.content_type == 'text':
                cust = self.getCustomer(message)
                ts = int(message.date)
                msg_date = datetime.fromtimestamp(ts)#.strftime('%Y-%m-%d %H:%M:%S')
                msg = Messages(wa_id=str(message.chat.id) + "_" + str(message.id),
                         from_id=message.from_user.id,
                         customer_id = cust.id,
                         chat_id=message.chat.id,
                         timestamp=msg_date,
                         text=message.text,)
                msg.props = {}
                self.session.add(msg)
                self.session.commit()
                    # if upd.message.chat.id in self.chat_ids:
                    #     self.process_message(message, chat_id)
        # self.bot.process_new_updates(updates)


    def getMessages(self):
        self.getUpdates()


if __name__ == "__main__":

    # key = os.getenv('TELEGRAM_BOT')
    # url = f"https://api.telegram.org/bot{key}/getUpdates"
    # result = requests.get(url)
    # jsonr = result.json()
    # if result.status_code == requests.codes.ok:
    #     with open('result.json', 'w') as fp:
    #         fp.write(json.dumps(jsonr['result']))

    BerriesBot().getMessages()
