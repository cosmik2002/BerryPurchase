import marshmallow_sqlalchemy.schema
from marshmallow_sqlalchemy import fields
from sqlalchemy import func, Column, Integer, String, ForeignKey, LargeBinary, Numeric, DateTime, Time, Text, Table
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship, configure_mappers

from database import Base
import marshmallow_sqlalchemy as ma


# alembic revision --autogenerate -m "card_number_field"
# alembic upgrade head


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
    payers = relationship("Payers", secondary="payers_to_clients", back_populates="clients")
    customers = relationship('Customers', secondary='customers_to_clients', back_populates='clients')


class Goods(Base):
    __tablename__ = "goods"
    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(Text)
    variants: Column = Column(Text)


payers_to_clients = Table('payers_to_clients',
                          Base.metadata,
                          Column('payer_id',Integer, ForeignKey('payers.id'), primary_key=True),
                          Column('client_id',Integer, ForeignKey('clients.id'), primary_key=True))

customers_to_clients = Table('customers_to_clients',
                             Base.metadata,
                             Column('customer_id',Integer, ForeignKey('customers.id'), primary_key=True),
                             Column('client_id',Integer, ForeignKey('clients.id'), primary_key=True))

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
    customer_id: Column = Column(Integer, ForeignKey(Customers.id), nullable=False)
    timestamp: Column = Column(DateTime, nullable=False)
    text: Column = Column(Text)
    customer = relationship(Customers, foreign_keys=customer_id)


class Payments(Base):
    __tablename__ = 'payments'
    id: Column = Column(Integer, primary_key=True)
    sms_id: Column = Column(Integer, index=True)
    operation_code: Column = Column(Text, index=True)
    payer_id: Column = Column(Integer, ForeignKey(Payers.id), index=True)
    timestamp: Column = Column(DateTime, index=True)
    date_processed: Column = Column(DateTime)
    comment: Column = Column(Text)
    sum: Column = Column(Numeric)
    payer = relationship(Payers, foreign_keys=payer_id)


class MessageOrders(Base):
    __tablename__ = 'message_orders'
    id: Column = Column(Integer, primary_key=True)
    message_id: Column = Column(Integer, ForeignKey(Messages.id), index=True)
    good_id: Column = Column(Integer, ForeignKey(Goods.id), index=True)
    quantity: Column = Column(Numeric)
    price: Column = Column(Numeric)
    good = relationship(Goods, foreign_keys=good_id)
    message = relationship(Messages, foreign_keys=message_id, backref='message_order')

#https://stackoverflow.com/questions/75457741/dynamically-generating-marshmallow-schemas-for-sqlalchemy-fails-on-column-attrib
configure_mappers()

class ClientsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Clients
        include_fk = True
        # include_relationships = True
        load_instance = True
    payers = fields.Nested('PayersSchema', many=True)
    customers = fields.Nested('CustomersSchema', many=True)


class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers
        include_fk = True
        # include_relationships = True
        load_instance = True
    clients = fields.Nested(ClientsSchema(exclude=('customers',)), many=True)

class PayersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payers
        include_fk = True
        # include_relationships = True
        load_instance = True
    clients = fields.Nested(ClientsSchema(exclude=('payers',)), many=True)


class PaymentsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payments
        include_fk = True
        # include_relationships = True
        load_instance = True

    payer = fields.Nested(PayersSchema())


class MessagesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Messages
        include_fk = True
        include_relationships = True
        load_instance = True
    customer = fields.Nested(CustomersSchema())
    message_order = fields.Nested('MessageOrdersSchema', many=True)


class GoodsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Goods
        include_fk = True
        # include_relationships = True
        load_instance = True

class MessageOrdersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MessageOrders
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
