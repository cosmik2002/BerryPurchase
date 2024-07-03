import asyncio
import json
import os
from datetime import datetime

from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import ChannelParticipantsSearch, Message

import database
from app.models import Messages, Customers


class TelegramApi:
    def __init__(self):
        self.session = database.SessionLocal
        self.counters = {
            'new_messages': 0,
            'new_customers': 0,
            'upd_messages': 0,
            'success': False
        }
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.username = os.getenv('TELEGRAM_USERNAME')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.client = TelegramClient(self.username, self.api_id, self.api_hash, system_version="4.16.30-vxCUSTOM")
        self.client.start()

    def load_messages(self):
        with self.client:
            self.client.loop.run_until_complete(self.work())
        return self.counters

    def getCustomer(self, message: Message) -> Customers:
        cust = self.session.query(Customers).filter_by(wa_id=message.from_id.user_id).all()
        if not cust:
            cust = Customers(wa_id=message.from_id.user_id,
                             name=f"{message.sender.first_name} {message.sender.last_name}",
                             number=message.sender.username)
            self.session.add(cust)
            self.session.commit()
            self.counters['new_customers'] += 1
        else:
            cust = cust[0]
        return cust

    def send(self, c_id: int, text):
        with self.client:
            self.client.loop.run_until_complete(self._send(c_id, text))

    async def _send(self, c_id: int, text):
        # Now you can use all client methods listed below, like for example...
        await self.client.send_message(c_id, text)

    async def work(self):
        client = self.client
        # async for dialog in client.iter_dialogs():
        #     print(dialog.name, 'has ID', dialog.id)
        # message: Messages
        async for message in client.iter_messages('Ягоды urbanfood Чехов', limit=50):
            print(message.id, message.text)
            message_id = str(message.chat_id) + "_" + str(message.id)
            msg = self.session.query(Messages).filter_by(wa_id=message_id).all()
            if not msg:
                cust = self.getCustomer(message)
                msg = Messages(wa_id=message_id,
                               from_id=message.sender.id,
                               customer_id=cust.id,
                               chat_id=message.chat_id,
                               timestamp=message.date,
                               text=message.text, )
                msg.props = {'msg': 'tg'}
                self.session.add(msg)
                self.session.commit()
                self.counters['new_messages'] += 1
            else:
                self.counters['upd_messages'] += 1
        # url = -1001788039692
        # channel = await self.client.get_entity(url)
        # await self.dump_all_participants(channel)
        # await self.dump_all_messages(channel)

    async def dump_all_participants(self, channel):
        """Записывает json-файл с информацией о всех участниках канала/чата"""
        offset_user = 0  # номер участника, с которого начинается считывание
        limit_user = 100  # максимальное число записей, передаваемых за один раз

        all_participants = []  # список всех участников канала
        filter_user = ChannelParticipantsSearch('')

        while True:
            participants = await self.client(GetParticipantsRequest(channel,
                                                                    filter_user, offset_user, limit_user, hash=0))
            if not participants.users:
                break
            all_participants.extend(participants.users)
            offset_user += len(participants.users)

        all_users_details = []  # список словарей с интересующими параметрами участников канала

        for participant in all_participants:
            all_users_details.append({"id": participant.id,
                                      "first_name": participant.first_name,
                                      "last_name": participant.last_name,
                                      "user": participant.username,
                                      "phone": participant.phone,
                                      "is_bot": participant.bot})

        with open('channel_users.json', 'w', encoding='utf8') as outfile:
            json.dump(all_users_details, outfile, ensure_ascii=False)

    async def dump_all_messages(self, channel):
        """Записывает json-файл с информацией о всех сообщениях канала/чата"""
        offset_msg = 0  # номер записи, с которой начинается считывание
        limit_msg = 100  # максимальное число записей, передаваемых за один раз

        all_messages = []  # список всех сообщений
        total_messages = 0
        total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

        class DateTimeEncoder(json.JSONEncoder):
            '''Класс для сериализации записи дат в JSON'''

            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                if isinstance(o, bytes):
                    return list(o)
                return json.JSONEncoder.default(self, o)

        while True:
            history = await self.client(GetHistoryRequest(
                peer=channel,
                offset_id=offset_msg,
                offset_date=None, add_offset=0,
                limit=limit_msg, max_id=0, min_id=0,
                hash=0))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                all_messages.append(message.to_dict())
            offset_msg = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break

        with open('channel_messages.json', 'w', encoding='utf8') as outfile:
            json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)


if __name__ == "__main__":
    TelegramApi().load_messages()
