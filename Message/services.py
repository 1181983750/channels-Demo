from typing import Type

from BaseOrm import BaseService
from Message.messageORM import MessageORM
from Message.models import Message


class MessageService(BaseService):

    def __init__(self, model: Type[Message]):
        super(MessageService, self).__init__(model=model)
        self.orm = MessageORM(model=model)
