import os

import telebot
from telebot.types import Message
from app.models import Messages, Customers


class BerriesBot:

    def __init__(self, session):
        self.counters = {}
        self.session = session
        key=os.getenv('TELEGRAM_BOT')
        self.bot = telebot.TeleBot(key)  # berries188bot

    def getCustomer(self, message:Message):
        cust = self.session.query(Customers).filter_by(wa_id=message.from_user).all()
        if not cust:
            sender = message.getContact()
            cust = Customers(wa_id=sender.id._serialized, name=sender.name, number=sender.number,
                             short_name=sender.shortName, push_name=sender.pushname)
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
        updates = self.bot.get_updates(#offset=(self.bot.last_update_id + 1),
                                       timeout=1, long_polling_timeout=1)

        self.bot.process_new_updates(updates)

        for upd in updates:
            if upd.channel_post is not None:
                message: Message = upd.channel_post
                Messages(wa_id=message.chat.id+"_"+message.id,
                         from_id=message.from_user,
                         chat_id=message.chat.id,
                         timestamp=message.date,
                         text=message.text)
                # self.process_channel_msg(message, upd)
            else:
                message = upd.message
                chat_id = message.chat.id
                if message.content_type == 'text':
                    message = message.text
                    self.logger.info("tg chat_id:{}, msg {}".format(chat_id, message))
                    # if upd.message.chat.id in self.chat_ids:
                    #     self.process_message(message, chat_id)


    def getMessages(self):
        self.getUpdates()


if __name__ == "__main__":
    BerriesBot.getMessages();