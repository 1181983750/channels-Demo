from typing import Type

from BaseOrm import BaseORM
from Message.models import Message


class MessageORM(BaseORM):

    def __init__(self, model: Type[Message]):
        super(MessageORM, self).__init__(model=model)
        self.model = model

