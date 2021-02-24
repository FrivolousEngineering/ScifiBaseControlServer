from Server.Database import init_db


from Server.Database import db_session
from Server.models import User, Ability

init_db()
u = User('8666529cc', 'admin', 'admin@localhost')
u2 = User("abcdef", "AnotherAdmin", "admin@notlocalhost")
u3 = User("123abc", "Normal user!", "normal@localhost")
see_user_ability = Ability("see_users")
u.abilities = [see_user_ability]
u2.abilities = [see_user_ability]
db_session.add(u)
db_session.add(u2)
db_session.add(u3)
db_session.commit()