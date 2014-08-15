import cherrypy
from cherrypy.process import plugins
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from social.utils import setting_name, module_member
from social.actions import do_auth, do_complete, do_disconnect
from social.apps.cherrypy_app.utils import strategy


Base = declarative_base()

AUTH_DB_PATH = 'sqlite:////data/auth.db'

def BuildAuthSession():
    engine = create_engine(AUTH_DB_PATH, echo=False)
    session = scoped_session(sessionmaker(autoflush=True, autocommit=False))
    session.configure(bind=engine)
    return session

class FuckUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    password = Column(String(200), default='')
    name = Column(String(100))
    email = Column(String(200))
    active = Column(Boolean, default=True)
    admin = Column(Boolean, default=False)

    def is_active(self):
        return self.active

    def is_admin(self):
        return self.admin

class AuthServer(object):
    def add_routes(self, connect):
        connect( '/auth/done', self.done)
        connect( '/auth/login/{backend}', self.login)
        connect( '/auth/complete/{backend}', self.complete)
        connect( '/auth/disconnect/{backend}', self.disconnect)

    def done(self):
        u = cherrypy.request.user
        return "Hello, %s" % u.username

    @cherrypy.expose
    @strategy('/auth/complete/%(backend)s')
    def login(self, backend):
        ret = do_auth(self.strategy)
        cherrypy.log.error("session=" + repr(cherrypy.session.items()) )
        return ret

    @cherrypy.expose
    @strategy('/auth/complete/%(backend)s')
    def complete(self, backend, *args, **kwargs):
        login = cherrypy.config.get(setting_name('LOGIN_METHOD'))
        do_login = module_member(login) if login else self.do_login
        user = getattr(cherrypy.request, 'user', None)
        return do_complete(self.strategy, do_login, user=user, *args, **kwargs)

    @cherrypy.expose
    def disconnect(self, backend, association_id=None):
        user = getattr(cherrypy.request, 'user', None)
        return do_disconnect(self.strategy, user, association_id)

    def do_login(self, strategy, user, social_user):
        strategy.session_set('user_id', user.id)

if __name__ == '__main__':
    cherrypy.config.update({
        'SOCIAL_AUTH_USER_MODEL': 'auth.FuckUser',
    })
    engine = create_engine(AUTH_DB_PATH)
    Base.metadata.create_all(engine)

    from social.apps.cherrypy_app.models import SocialBase
    SocialBase.metadata.create_all(engine)

