import marshmallow_sqlalchemy.schema
from marshmallow_sqlalchemy import fields
from sqlalchemy import func, Column, Integer, String, ForeignKey, LargeBinary, Numeric, DateTime, Time, Text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship

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


class Goods(Base):
    __tablename__ = "goods"
    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(Text)
    variants: Column = Column(Text)


class Customers(Base):
    __tablename__ = "customers"
    id: Column = Column(Integer, primary_key=True)
    wa_id: Column = Column(Text, index=True)
    name: Column = Column(Text)
    number: Column = Column(Text, index=True)
    short_name: Column = Column(Text)
    push_name: Column = Column(Text)


class Payers(Base):
    __tablename__ = "payers"
    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(Text, index=True)
    card_number: Column = Column(Text, index=True)
    comments: Column = Column(Text)


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


class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers
        include_fk = True
        # include_relationships = True
        load_instance = True


class ClientsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Clients
        include_fk = True
        # include_relationships = True
        load_instance = True


class PayersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payers
        include_fk = True
        # include_relationships = True
        load_instance = True


class PaymentsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payments
        include_fk = True
        include_relationships = True
        load_instance = True

    payer = fields.Nested(PayersSchema)


class MessagesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Messages
        # include_fk = True
        include_relationships = True
        load_instance = True

    customer = fields.Nested(CustomersSchema)


class ClientsLinksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientsLinks
        include_fk = True
        load_instance = True

    customer = fields.Nested(CustomersSchema)
    client = fields.Nested(ClientsSchema)
    payer = fields.Nested(PayersSchema)
