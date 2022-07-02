from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from Server.Database import Base


user_ability_table = Table('user_ability', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.card_id')),
    Column('ability_id', Integer, ForeignKey('ability.id'))
)


class User(Base):  # type: ignore
    __tablename__ = 'user'
    card_id = Column(String(50), primary_key=True)

    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    abilities = relationship("Ability", secondary = user_ability_table, backref = "users")

    def __init__(self, card_id=None, name=None, email=None):
        self.card_id = card_id
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.name


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


