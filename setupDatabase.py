from Server.Database import init_db


from Server.Database import db_session
from Server.models import User, Role, Ability

init_db()
u = User('admin', 'admin@localhost')
u2 = User("AnotherAdmin", "admin@notlocalhost")
u3 = User("Normal user!", "normal@localhost")
admin_role = Role("superadmin")
see_user_ability = Ability("see_users")
admin_role.abilities = [see_user_ability]
u.roles = [admin_role]
u2.roles = [admin_role]
db_session.add(u)
db_session.add(u2)
db_session.add(u3)
db_session.add(admin_role)
db_session.add(see_user_ability)
db_session.commit()