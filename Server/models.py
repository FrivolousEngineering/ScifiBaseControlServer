from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float
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

    engineering_level = Column(Integer)

    abilities = relationship("Ability", secondary = user_ability_table, backref = "user")
    access_cards = relationship("AccessCard", back_populates="user")
    modifiers = relationship("Modifier", back_populates="user")
    faction = Column(String(100))  # What faction does the user belong to?

    def __init__(self, name, faction, engineering_level = 0):
        self.id = name
        self.faction = faction
        self.engineering_level = engineering_level

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


class PerformanceChangeLog(Base):  # type: ignore
    __tablename__ = "performance_change"

    id = Column(Integer, primary_key=True)
    node_id = Column(String(100))
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")
    original_target_performance = Column(Float)
    new_target_performance = Column(Float)
    tick_number = Column(Integer)

    def __init__(self, user, node_id, original_target_performance, new_target_performance, tick_number):
        self.user = user
        self.node_id = node_id
        self.original_target_performance = original_target_performance
        self.new_target_performance = new_target_performance
        self.tick_number = tick_number