#!/usr/bin/python
# -*- coding: utf-8 -*-
# cython: language_level=3
import argparse
import bcrypt
from common.database import Base, Session
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, and_

import datetime
from cerberus import Validator

import logging
logger = logging.getLogger("TMI.models")


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

    def user_has_role(user, role_name):
        """ Check if user has any of the role_name(s) in its roles
        :param role_name: string or list of strings
        :return: True/False


        NOTE: checked with from timeit import default_timer as timer
              and this function is very fast, 2-5ms, not worth switching to sql
        """

        if user.username == "admin": return True

        s = Session()
        user_roles = s.query(RolesUsers.role_id).filter(RolesUsers.user_id == user.id).all()
        if isinstance(role_name, list):
            role_id = []
            for name in role_name:
                try:
                    id = s.query(Role.id).filter(Role.name == name).one()
                except:
                    id = None

                if id: role_id.append(id)
        else:
            role_id = s.query(Role.id).filter(Role.name == role_name).all()

        s.close()
        has_role = any(x in user_roles for x in role_id)
        logger.info("Required {} -> {} User's (any one of) == {}".format(role_id, user_roles, has_role))
        return has_role

    def user_enabled(user):
        return RolesUsers.user_has_role(user, "ENABLED")


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    def get_all():
        s = Session()
        _roles = [[r.id, r.name, r.description] for r in s.query(Role).all()]
        s.close()
        return _roles


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    fname = Column(String(64))
    lname = Column(String(64))
    username = Column(String(64), unique=True)
    password = Column(String(64))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    login_count = Column(Integer)
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    value = Column(String(64))  # this is encryption of roles, to detect hacks
    roles = relationship('Role', secondary='roles_users', lazy='joined', backref=backref('users', lazy='joined'))

    # https://nicolaiarocci.com/validating-user-objects-cerberus/
    schema = {
        "tin_fname":
            {'type': 'string', 'required': False, 'minlength': 1},
        "tin_lname":
            {'type': 'string', 'required': False, 'minlength': 1},
        "tin_uname":
            {'type': 'string', 'required': False, 'minlength': 4, "unique_user": True},
        "tin_uname_only":
            {'type': 'string', 'required': False, 'minlength': 4},
        "tin_lpw":
            {'type': 'string', 'required': False, 'minlength': 4},
        "tin_lpw_confirm":
            {'type': 'string', 'required': False, 'minlength': 4, "match_value": "tin_lpw"},
        "tin_email":
            {'type': 'string', 'required': False, 'minlength': 7, "unique_email": True,
             'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'},
        "tin_email_only":
            {'type': 'string', 'required': False, 'minlength': 7,
             'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'},
    }

    schema_error = {
        "tin_fname": {
            "errors": [
                {'err': ["min length"],
                 "msg": "Name too short, please enter a valid name.",
                 "css": {'input': {'background-color': '#F08080'}},
                 }
            ]
        },
        "tin_lname": {
            "errors": [
                {'err': ["min length"],
                 "msg": "Name too short, please enter a valid name.",
                 "css": {'input': {'background-color': '#F08080'}},
                 }
            ]
        },
        "tin_uname": {
            "errors": [
                {'err': ["min length"],
                 "msg": "Name too short, please enter a valid name.",
                 "css": {'input': {'background-color': '#F08080'}},
                 },
                {'err': ["duplicate"],
                 "msg": "Username already exist, please pick a new username.",
                 "css": {'input': {'background-color': '#F08080'}},
                 }
            ]
        },
        "tin_uname_only": {
            "errors": [
                {'err': ["min length"],
                 "msg": "Name too short, please enter a valid name.",
                 "css": {'input': {'background-color': '#F08080'}},
                 },
            ]
        },
        "tin_lpw": {
            "errors": [
                {'err': ["min length"],
                 "msg": "Password too short, please enter a valid password.",
                 "css": {'input': {'background-color': '#F08080'}},
                 }
            ]
        },
        "tin_lpw_confirm": {
            "errors": [
                {'err': ["min length"],
                 "msg": "Password too short, please enter a valid password.",
                 "css": {'input': {'background-color': '#F08080'}},
                 },
                {'err': ["Field doesn't match field"],
                 "msg": "Passwords do not match!",
                 "css": {'input': {'background-color': '#F08080'}},
                 }
            ]
        },
        "tin_email": {
            "errors": [
                {'err': ["min length", "value does not match regex"],
                 "msg": "Email is invalid, please enter a valid email.",
                 "css": {'input': {'background-color': '#F08080'}},
                 }
            ]
        },
        "tin_email_only": {
            "errors": [
                {'err': ["min length", "value does not match regex"],
                 "msg": "Email is invalid, please enter a valid email.",
                 "css": {'input': {'background-color': '#F08080'}},
                 },
            ]
        }
    }

    def get_hashed_password(plain_text_password):
        # Hash a password for the first time
        #   (Using bcrypt, the salt is saved into the hash itself)
        return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

    def check_password(plain_text_password, hashed_password):
        # Check hashed password. Using bcrypt, the salt is saved into the hash itself
        return bcrypt.checkpw(plain_text_password, hashed_password)

    def get_form_error_handle_from_err(key, err):
        if not User().schema_error.get(key, False):
            logger.error("{} not found in schema_error".format(key))
            return None

        for error in User().schema_error[key]['errors']:
            for err_type in error['err']:
                if err_type in err:
                    return error

        logger.error("{} error {} not found in schema_error".format(key, err))
        return {'err': [],
                "msg": "!UNKNOWN ERROR!",
                "css": {},
                }

    def validate(args, originalRecordExists=False):
        # TODO: rename this to validate_user_account, because this validates all fields

        class ExtendValidator(Validator):

            def __init__(self, *args, **kwargs):
                self.originalRecordExists = False
                if kwargs.get('kwargs', {}).get('additional_context', False):
                    self.additional_context = kwargs['kwargs']['additional_context']
                    self.originalRecordExists = self.additional_context.get("originalRecordExists", False)
                super(ExtendValidator, self).__init__(*args, **kwargs)

            def _validate_match_value(self, other, field, value):
                if other not in self.document: return False
                if value != self.document[other]:
                    self._error(field, "Field doesn't match field %s." % other)

            def _validate_unique_user(self, other, field, value):
                if not other: return  # other == True if unique user is required
                # value -> username
                users = User.get_username([value])
                if self.originalRecordExists:
                    # this user original record exist, so a match against original username is allowed,
                    # but no other is allowed to exist because that would be a clash
                    if len(users) > 1: self._error(field, "duplicate")
                else:
                    if len(users) > 0: self._error(field, "duplicate")

            def _validate_unique_email(self, other, field, value):
                if not other: return  # other == True if unique user is required
                # value -> email
                users = User.get_username([value])
                if self.originalRecordExists:
                    # this user original record exist, so a match against original email is allowed,
                    # but no other is allowed to exist because that would be a clash
                    if len(users) > 1: self._error(field, "duplicate")
                else:
                    if len(users) > 0: self._error(field, "duplicate")

        v = ExtendValidator(User().schema, kwargs={'additional_context': {'originalRecordExists': originalRecordExists}})
        v.allow_unknown = True
        validated = v.validate(args)
        return validated, v.errors

    def add(first, last, username, password, email):
        session = Session()
        user = User(fname=first,
                    lname=last,
                    username=username,
                    password=User.get_hashed_password(password),
                    email=email,
                    current_login_at=datetime.datetime.now())
        session.add(user)
        try:
            session.commit()
        except Exception as e:
            logger.error(e)
            return False
        session.close()
        logger.info("User {} added".format(username))
        return True

    def update(original_username, first, last, username, password, email):
        session = Session()

        try:
            user_update = session.query(User).filter(User.username == original_username).one()
        except Exception as e:
            logger.error(e)
            user_update = None

        if user_update is None:
            logger.error("User is None, cannot update, something bad happened")
            session.close()
            return False

        user_update.fname =first
        user_update.lname = last
        user_update.username = username
        user_update.password = User.get_hashed_password(password)
        user_update.email = email

        session.commit()
        session.close()
        logger.info("User {} updated".format(username))
        return True

    def update_roles(user, roles):
        """
        :param roles: names of roles
        :return:
        """
        session = Session()

        try:
            user_update = session.query(User).filter(User.username == user.username).one()
        except Exception as e:
            logger.error(e)
            user_update = None

        if user_update is None:
            session.close()
            return False

        logger.info(roles)
        new_roles = []
        for role in roles:
            # check to see if the role is in this db, if not, just skip it, its not
            # important to us
            r = session.query(Role).filter(Role.name == role).scalar()
            if r:
                new_roles.append(session.query(Role).filter(Role.name == role).one())
            else:
                logger.warning("Skipping unknown role: {}".format(role))


        def sorter(e): return e.id

        new_roles.sort(key=sorter)

        user_update.roles = new_roles
        session.commit()
        logger.info("User {} updated".format(User.username))

        # make a hash of the sorted roles to detect db hacking
        r = ""
        for role in new_roles: r += role.name

        user_update.value = User.get_hashed_password(r)

        session.commit()
        session.close()
        return True

    def login(username, password):
        session = Session()
        enabled = False
        try:
            user = session.query(User).filter(User.username == username).one()
            if User.check_password(password, user.password):
                enabled = RolesUsers.user_enabled(user)
            else:
                logger.error("{} Failed password check".format(User.username))
        except Exception as e:
            logger.error(e)
            return None

        finally:
            session.close()

        # check if database was hacked...
        roles = user.roles

        def sorter(e): return e.id

        roles.sort(key=sorter)

        r = ""
        for role in roles: r += role.name
        hacked = not User.check_password(r, user.value)

        if hacked:
            logger.error("DB Hacked detected".format(User.username))
            return None

        if enabled:
            logger.info("{} {}".format(user.username, enabled))
            return user
        else:
            logger.error("{} is not enabled".format(User.username))
            return None

    def get_username(username, all=False):
        """ get users by username, or get all users
        :param username: string, or list of strings
        :param all: if set, all the users are returned
        :return: list of users found
        """
        session = Session()
        users = []
        logger.info("get_username: {}".format(username))
        try:
            if not all and isinstance(username, str):
                users = session.query(User).filter(User.username == username).one()
            elif not all and isinstance(username, list):
                users = session.query(User).filter(User.username.in_(username)).all()
            elif all:
                users = session.query(User).order_by(User.username).all()
            else:
                logger.error("Bad request")  # should never get here
        except Exception as e:
            logger.error("ERROR: called parms: {} {}".format(username, all))
            logger.error(e)

        session.close()
        return users

    def exist_email(email):
        session = Session()
        try:
            user = session.query(User).filter(User.email == email).one()
        except:
            user = None
        session.close()
        return user != None

    def exist_username(username):
        session = Session()
        try:
            user = session.query(User).filter(User.username == username).one()
        except:
            user = None
        session.close()
        return user != None

    def get_by_id(id):
        session = Session()
        try:
            user = session.query(User).filter(User.id == id).one()
        except:
            user = None
        session.close()
        logger.debug("{} -> {}".format(id, user.username))
        return user

    def get_all_users_by_role(role_name):
        session = Session()
        try:
            users = session.query(User).filter(User.roles.any(Role.name == role_name)).all()
        except Exception as e:
            logger.error(e)
            users = []
        session.close()
        user_list = []
        for user in users:
            d = {
                "fname": user.fname,
                "lname": user.lname,
                "username": user.username,
                "password": user.password,
                "email": user.email,
                "role_names": [r.name for r in user.roles]
            }
            user_list.append(d)
        return user_list


def q_users_last_active():
    session = Session()
    users = session.query(User).all()
    session.close()
    return users


def parse_args():
    """
    :return: args
    """
    epilog = """
    Usage examples:
    TBD
    """
    parser = argparse.ArgumentParser(description='TMI',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=epilog)

    parser.add_argument("-v", '--verbose', dest='verbose', default=0, action='count', help='Increase verbosity')
    parser.add_argument("--version", dest="show_version", action='store_true', help='Show version and exit')
    parser.add_argument("-c", "--create",
                        dest="create",
                        action="store_true",
                        default=False,
                        help="Create/Recreate database")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    if args.create:
        pass