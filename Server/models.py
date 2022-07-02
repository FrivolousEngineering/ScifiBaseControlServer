from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from Server.Database import Base


user_ability_table = Table('user_ability', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('ability_id', Integer, ForeignKey('ability.id'))
)


class AccessCard(Base):
    __tablename__ = "access_card"

    id = Column(String(50), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates = "access_cards")

    def __init__(self, card_id):
        self.id = card_id


class User(Base):  # type: ignore
    __tablename__ = 'user'
    id = Column(String(50), primary_key=True)

    abilities = relationship("Ability", secondary = user_ability_table, backref = "user")
    access_cards = relationship("AccessCard", back_populates="user")
    modifiers = relationship("Modifier", back_populates="user")

    def __init__(self, name=None):
        self.id = name

    def __repr__(self):
        return '<User %r>' % self.name


class Modifier(Base):
    __tablename__ = 'modifier'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))  # What is the name of the modifier that was placed?
    node_id = Column(String(100))  # On what node is this placed?
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates = "modifiers")

    def __init__(self, name=None, node_id=None):
        self.name = name
        self.node_id = node_id


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


