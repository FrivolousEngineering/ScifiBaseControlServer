from Server.Database import init_db, createDBSession

from Server.Database import db_session
from Server.models import User, Ability, AccessCard

createDBSession('sqlite:///ScifiControlServer.db')
init_db()
user_one = User('admin_a', engineering_level = 2)
card_one = AccessCard("a")
user_one.access_cards.append(card_one)

user_two = User("admin_b", engineering_level = 1)
card_two = AccessCard("b")
user_two.access_cards.append(card_two)


user_three = User("user")
card_three = AccessCard("c")
user_three.access_cards.append(card_three)

see_user_ability = Ability("see_users")
user_one.abilities.append(see_user_ability)
user_two.abilities.append(see_user_ability)

db_session.add(user_one)
db_session.add(user_two)
db_session.add(user_three)
db_session.commit()

#u2 = User("abcdef", "AnotherAdmin", "admin@notlocalhost")
#u3 = User("123abc", "Normal user!", "normal@localhost")
#see_user_ability = Ability("see_users")
#u.abilities = [see_user_ability]
#u2.abilities = [see_user_ability]
#db_session.add(u)
#db_session.add(u2)
#db_session.add(u3)
#db_session.commit()