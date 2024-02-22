import json
import os
from datetime import datetime

from sqlalchemy.orm import scoped_session

import database

import requests
import simplejson
import telebot
from telebot.types import Message
from app.models import Messages, Customers


class BerriesBot:

    def __init__(self, session):
        self.counters = {}
        self.session = session
        key=os.getenv('TELEGRAM_BOT')
        self.bot = telebot.TeleBot(key)  # berries188bot

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
        updates = self.bot.get_updates(#offset=-1,#(self.bot.last_update_id + 1),
                                       timeout=1, long_polling_timeout=1)
        # with open('updates.json', 'w') as fp:
        #     simplejson.dump(updates, fp)
        # exit(0)

        for upd in updates:
            if upd.channel_post is not None:
                message: Message = upd.channel_post
                # self.process_channel_msg(message, upd)
            else:
                message: Message = upd.message
                chat_id = message.chat.id
            if message.content_type == 'text':
                cust = self.getCustomer(message)
                ts = int(message.date)
                msg_date = datetime.fromtimestamp(ts)#.strftime('%Y-%m-%d %H:%M:%S')
                msg = Messages(wa_id=str(message.chat.id) + "_" + str(message.id),
                         from_id=message.from_user.id,
                         customer_id = cust.id,
                         chat_id=message.chat.id,
                         timestamp=msg_date,
                         text=message.text)
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

    BerriesBot(database.SessionLocal).getMessages()
