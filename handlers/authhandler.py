from handlers.json_util import JsonHandler
import hashlib
from salt import salt
from database_tools.alchemy import CUsers
import secrets


class AuthHandler(JsonHandler):
    def get(self):
        self.write('GET - Welcome to the AuthHandler!')

    def create_sha(self, string):
        return hashlib.sha256(string.encode() + salt.encode()).hexdigest()

    def put(self):
        login = self.json_data['user']
        passwd = self.json_data['password']
        passwd = self.create_sha(passwd)
        exists = self.db.query(CUsers).filter_by(username=login).all()
        if exists:
            result_db = self.db.query(CUsers.password).filter_by(username=login).first()[0]
            result_sha = self.create_sha(result_db)
            if passwd == result_sha:
                self.write('You logged success\n')
                token = secrets.token_hex(32)
                #  запись token
                self.db.query(CUsers).filter(CUsers.username == login).update({CUsers.token: token},
                                                                           synchronize_session='evaluate')
                self.response['token'] = token
                self.response['response'] = '200'
                self.write_json()
            else:
                self.response['message'] = 'Incorrect password'
                self.response['response'] = '403'
                self.write_json()

        else:
            self.response['message'] = 'Login or password incorrect'
            self.response['response'] = '403'
            self.write_json()
