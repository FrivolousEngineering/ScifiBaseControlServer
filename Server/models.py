from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from Server.Database import Base


user_ability_table = Table('user_ability', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.card_id')),
    Column('ability_id', Integer, ForeignKey('ability.id'))
)

user_modifier_table = Table('user_modifier', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.card_id')),
    Column('modifier_id', Integer, ForeignKey('modifier.id'))
)


class User(Base):  # type: ignore
    __tablename__ = 'user'
    card_id = Column(String(50), primary_key=True)

    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    abilities = relationship("Ability", secondary = user_ability_table, backref = "users")
    active_modifiers = relationship("Modifier", secondary = user_modifier_table)

    def __init__(self, card_id=None, name=None, email=None):
        self.card_id = card_id
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.name


class Modifier(Base):
    __tablename__ = 'modifier'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))  # What is the name of the modifier that was placed?
    node_id = Column(String(100))  # On what node is this placed?
    card_id = Column(String(50))  # By which card was this modifier placed?

    def __init__(self, name=None, node_id=None, card_id = None):
        self.name = name
        self.node_id = node_id
        self.card_id = card_id


class Ability(Base):  # type: ignore
    __tablename__ = 'ability'
    id = Column(Integer, primary_key=True)
    name = Column(String(12), unique=True)

    def __init__(self, name):
        self.name = name.lower()

    def __repr__(self):
        return '<Ability {}>'.format(self.name)

    def __str__(self):
        return self.name


