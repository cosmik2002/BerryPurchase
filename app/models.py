from dataclasses import dataclass

import marshmallow
# import redis
import simplejson as simplejson
from flask import current_app
from marshmallow import EXCLUDE, INCLUDE
from marshmallow_sqlalchemy import fields, auto_field
from sqlalchemy import func, Column, Integer, String, ForeignKey, LargeBinary, Numeric, DateTime, Time, Text, Table, \
    JSON, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, configure_mappers, column_property, aliased

from database import Base
import marshmallow_sqlalchemy as ma
# import rq

# alembic revision --autogenerate -m "card_number_field"
# alembic upgrade head
# alembic downgrade -1
# 91d5ff360882_price_field.py - см при проблемах с sqlite

class smsMsg(Base):
    __tablename__ = "sms_msg"
    id: Column = Column(Integer, primary_key=True)
    msg: Column = Column(Text)
    sender: Column = Column(Text)
    value: Column = Column(Numeric)
    date: Column = Column(DateTime)


class Clients(Base):
    __tablename__ = "clients"
    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(Text)
    duplicate_for: Column = Column(Integer, ForeignKey(id))
    payers = relationship("Payers", secondary="payers_to_clients", back_populates="clients")
    customers = relationship('Customers', secondary='customers_to_clients', back_populates='clients')


class Goods(Base):
    __tablename__ = "goods"
    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(Text)
    variants: Column = Column(Text)
    active: Column = Column(Boolean)
    price: Column = Column(Numeric)
    url: Column = Column(Text)
    image: Column = Column(Text)
    org_price: Column = Column(Numeric)
    type: Column = Column(Text)
    short_name: Column = Column(Text)
    weight: Column = Column(Numeric)
    date_update: Column = Column(DateTime(timezone=True), server_default=func.now())
    enabled: Column = Column(Boolean, server_default='1')

class Prices(Base):
    __tablename__ = "prices"
    id: Column = Column(Integer, primary_key=True)
    good_id: Column = Column(Integer, ForeignKey(Goods.id), nullable=False)
    date: Column = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    price: Column = Column(Numeric)



payers_to_clients = Table('payers_to_clients',
                          Base.metadata,
                          Column('payer_id', Integer, ForeignKey('payers.id'), primary_key=True),
                          Column('client_id', Integer, ForeignKey('clients.id'), primary_key=True))

customers_to_clients = Table('customers_to_clients',
                             Base.metadata,
                             Column('customer_id', Integer, ForeignKey('customers.id'), primary_key=True),
                             Column('client_id', Integer, ForeignKey('clients.id'), primary_key=True))


class Customers(Base):
    __tablename__ = "customers"
    id: Column = Column(Integer, primary_key=True)
    wa_id: Column = Column(Text, index=True)
    name: Column = Column(Text)
    number: Column = Column(Text, index=True)
    short_name: Column = Column(Text)
    push_name: Column = Column(Text)
    clients = relationship(Clients, secondary=customers_to_clients, back_populates='customers')


class Payers(Base):
    __tablename__ = "payers"
    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(Text, index=True)
    card_number: Column = Column(Text, index=True)
    bank_name: Column = Column(Text, index=True)
    comments: Column = Column(Text)
    clients = relationship(Clients, secondary=payers_to_clients, back_populates="payers")


class ClientsLinks(Base):
    __tablename__ = "clients_links"
    client_id: Column = Column(Integer, ForeignKey(Clients.id), nullable=False, primary_key=True)
    customer_id: Column = Column(Integer, ForeignKey(Customers.id), nullable=False, primary_key=True)
    payer_id: Column = Column(Integer, ForeignKey(Payers.id), nullable=False)
    client = relationship(Clients, foreign_keys=client_id)
    customer = relationship(Customers, foreign_keys=customer_id)
    payer = relationship(Payers, foreign_keys=payer_id)


class Messages(Base):
    __tablename__ = "messages"
    id: Column = Column(Integer, primary_key=True)
    wa_id: Column = Column(Text, index=True)
    from_id: Column = Column(Text)
    chat_id: Column = Column(Text)
    customer_id: Column = Column(Integer, ForeignKey(Customers.id), nullable=False)
    for_client_id: Column = Column(Integer, ForeignKey(Clients.id), nullable=True)
    timestamp: Column = Column(DateTime, nullable=False)
    text: Column = Column(Text)
    quoted_id: Column = Column(Integer, ForeignKey(id))
    props: Column = Column(JSON)
    customer = relationship(Customers, foreign_keys=customer_id)
    for_client = relationship(Clients, foreign_keys=for_client_id)
    quoted = relationship("Messages")
    @hybrid_property
    def order_descr(self):
        descr = ''
        for row in self.message_order:
            descr += f"{row.good.name}-{float(row.quantity or 0):g}; "
        return descr
    @order_descr.setter
    def order_descr(self, val):
        pass


class Payments(Base):
    __tablename__ = 'payments'
    id: Column = Column(Integer, primary_key=True)
    sms_id: Column = Column(Integer, index=True)
    operation_code: Column = Column(Text, index=True)
    payer_id: Column = Column(Integer, ForeignKey(Payers.id), index=True)
    for_client_id: Column = Column(Integer, ForeignKey(Clients.id), nullable=True)
    timestamp: Column = Column(DateTime, index=True)
    date_processed: Column = Column(DateTime)
    comment: Column = Column(Text)
    sum: Column = Column(Numeric(15,2))
    not_use: Column = Column(Boolean)
    ost = column_property(func.sum(sum).over(order_by=timestamp))
    payer = relationship(Payers, foreign_keys=payer_id)

@dataclass
class Itog(Base):
    INIT = 0
    CALCULATED = 1
    MANUAL = 2
    __tablename__ = 'itog'
    id: Column = Column(Integer, primary_key=True)
    date: Column = Column(DateTime, index=True)
    client_id: Column = Column(Integer, ForeignKey(Clients.id), nullable=True)
    good_id: Column = Column(Integer, ForeignKey(Goods.id), nullable=True)
    quantity: Column = Column(Numeric(15,2))
    price: Column = Column(Numeric(15,2))
    org: Column = Column(Numeric(15,2))
    sum: Column = Column(Numeric(15,2))
    payed_sum: Column = Column(Numeric(15,2))
    payment_id: Column = Column(Integer, ForeignKey(Payments.id), nullable=True)
    type: Column = Column(Integer)
    client = relationship(Clients, foreign_keys=client_id)

# class Task(Base):
#     id = Column(String(36), primary_key=True)
#     name = Column(String(128), index=True)
#     description = Column(String(128))
#     # user_id = Column(Integer, ForeignKey('user.id'))
#     complete = Column(Boolean, default=False)
#
#     def get_rq_job(self):
#         try:
#             rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
#         except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
#             return None
#         return rq_job
#
#     def get_progress(self):
#         job = self.get_rq_job()
#         return job.meta.get('progress', 0) if job is not None else 100

class MessageOrders(Base):
    __tablename__ = 'message_orders'
    id: Column = Column(Integer, primary_key=True)
    message_id: Column = Column(Integer, ForeignKey(Messages.id), index=True)
    good_id: Column = Column(Integer, ForeignKey(Goods.id), index=True)
    quantity: Column = Column(Numeric(15,2))
    price: Column = Column(Numeric(15,2))
    good = relationship(Goods, foreign_keys=good_id)
    message = relationship(Messages, foreign_keys=message_id, backref='message_order')


class Settings(Base):
    __tablename__ = 'settings'
    START_DATE = 'start_date'
    SHEET_NAME = 'sheet_name'
    WA_CLIENT = 'wa_client'
    TELEGRAMM = 'telegramm'
    MARKET_LOAD = 'market_load'
    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(Text)
    value: Column = Column(JSON)


# https://stackoverflow.com/questions/75457741/dynamically-generating-marshmallow-schemas-for-sqlalchemy-fails-on-column-attrib
configure_mappers()


class ClientsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Clients
        include_fk = True
        include_relationships = True
        load_instance = True

    # payers = fields.Nested('PayersSchema', many=True)
    # customers = fields.Nested('CustomersSchema', many=True)

class ItogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Itog
        include_fk = True
        # include_relationships = True
        load_instance = True
    client = fields.Nested(ClientsSchema())


class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers
        include_fk = True
        # include_relationships = True
        load_instance = True

    clients = fields.Nested(ClientsSchema(), many=True)


class PayersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payers
        include_fk = True
        # include_relationships = True
        load_instance = True

    clients = fields.Nested(ClientsSchema(), many=True)


class PaymentsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payments
        include_fk = True
        unknown = EXCLUDE #исключаем незнакомые поля (ругался на ost)
        # include_relationships = True
        json_module = simplejson
        load_instance = True
    # ost = marshmallow.fields.Decimal()
    payer = fields.Nested(PayersSchema())


class MessagesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Messages
        unknown = EXCLUDE
        json_module = simplejson
        include_fk = True
        include_relationships = True
        load_instance = True

    timestamp = marshmallow.fields.Function(lambda obj: obj.timestamp.isoformat()+'Z' if obj else None)

    order_descr = marshmallow.fields.Str()
    customer = fields.Nested(CustomersSchema)
    for_client = fields.Nested(ClientsSchema, allow_none=True)
    message_order = fields.Nested('MessageOrdersSchema', many=True)


class GoodsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Goods
        json_module = simplejson
        include_fk = True
        # include_relationships = True
        load_instance = True


class MessageOrdersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MessageOrders
        json_module = simplejson
        include_fk = True
        include_relationships = True
        load_instance = True

    # message = fields.Nested(MessagesSchema(exclude=('message_order',)))
    good = fields.Nested(GoodsSchema())


class ClientsLinksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientsLinks
        include_fk = True
        load_instance = True

    customer = fields.Nested(CustomersSchema())
    client = fields.Nested(ClientsSchema())
    payer = fields.Nested(PayersSchema())


class SettingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Settings
        load_instance = True
