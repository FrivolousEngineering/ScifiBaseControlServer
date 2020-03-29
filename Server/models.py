from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from Server.Database import Base


user_role_table = Table('user_role', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
)


role_ability_table = Table('role_ability', Base.metadata,
    Column('role_id', Integer, ForeignKey('role.id')),
    Column('ability_id', Integer, ForeignKey('ability.id'))
)


class User(Base):  # type: ignore
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)

    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    roles = relationship("Role", secondary = user_role_table, backref = "users")
    #role = relationship("Role")
    #roles = relationship("Role", back_populates='user', cascade = "all, delete, delete-orphan")

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)


class Ability(Base): # type: ignore
    __tablename__ = 'ability'
    id = Column(Integer, primary_key=True)
    name = Column(String(12), unique=True)

    def __init__(self, name):
        self.name = name.lower()

    def __repr__(self):
        return '<Ability {}>'.format(self.name)

    def __str__(self):
      return self.name


class Role(Base): # type: ignore
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    abilities = relationship("Ability", secondary = role_ability_table, backref = "roles")

    #user_id = Column(Integer, ForeignKey('users.id'))
    #user = relationship("User", back_populates = "roles")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<ROLE %s>" %self.name


