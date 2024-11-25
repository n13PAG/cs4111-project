from flask_login import LoginManager, UserMixin


class User(UserMixin):
    def __init__(self, uid, sid, pid, name, email):
        self.uid = uid
        self.sid = sid
        self.pid = pid
        self.name = name
        self.email = email

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.uid)

    def is_student(self):
        if self.sid != None:
            return True
        else:
            return False

    def __eq__(self, other):
        '''
        Checks the equality of two `UserMixin` objects using `get_id`.
        '''
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        '''
        Checks the inequality of two `UserMixin` objects using `get_id`.
        '''
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

        if sys.version_info[0] != 2:  # pragma: no cover
            # Python 3 implicitly set __hash__ to None if we override __eq__
            # We set it back to its default implementation
            __hash__ = object.__hash__
