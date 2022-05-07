from typing import Type

from BaseOrm import BaseORM
from User.models import User, Contacts, ReplyFriend


class UserORM(BaseORM):

    def __init__(self, model: Type[User]):
        super(UserORM, self).__init__(model)
        self.model: Type[User] = model

    def get_user_by_phone_and_password(self, phone: str, password: str):
        result = self.model.objects.get(phone=phone, password=password)
        return result

    def get_user_by_phone(self, phone: str):
        result = self.model.objects.get(phone=phone)
        return result


class ContactsORM(BaseORM):

    def __init__(self, model: Type[Contacts]):
        super(ContactsORM, self).__init__(model=model)
        self.model: Type[Contacts] = model

    def get_contacts_by_primary_user_id_and_deputy_user_id(self, primary_user_id, deputy_user_id):
        result = self.model.objects.get(Primary_User_id=primary_user_id, Deputy_User_id=deputy_user_id)
        return result


class ReplyFriendORM(BaseORM):

    def __init__(self, model: Type[ReplyFriend]):
        super(ReplyFriendORM, self).__init__(model=model)
        self.model = model

    def get_reply_friend_by_accepted_id_and_primary_user_id(self, accepted_id, primary_user_id) -> Type[ReplyFriend]:
        result = self.model.objects.get(accepted_id=accepted_id, Primary_User_id=primary_user_id)
        return result
