from Nodes.Database import init_db


from Nodes.Database import db_session
from Nodes.models import User

init_db()
#u = User('admin', 'admin@localhost')
#db_session.add(u)
#db_session.commit()