from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    # def ready(self):
    #     from User.models import User
    #     User.objects.all().update(socket_id=None)