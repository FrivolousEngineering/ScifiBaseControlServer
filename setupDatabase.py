from Server.Database import init_db


from Server.Database import db_session
from Server.models import User, Ability, AccessCard

init_db()
user_one = User('admin')
card_one = AccessCard("8666529cc")
user_one.access_cards.append(card_one)

user_two = User("AnotherAdmin")
card_two = AccessCard("abcdef")
user_two.access_cards.append(card_two)


user_three = User("Normal User!")
card_three = AccessCard("123abc")
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