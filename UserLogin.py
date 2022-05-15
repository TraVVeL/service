from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return str(self.__user['name'])

    def get_mail(self):
        return str(self.__user['email'])

    def get_cash(self):
        return str(self.__user['cash'])

    def get_cart(self):
        return str(self.__user['cart'])
