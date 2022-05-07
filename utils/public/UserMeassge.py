from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



class Ser_Msg:
    def serializer_msg(self, message, channel_name):
        channel_layer = get_channel_layer()
        event = None
        if message.get('tip') == 1:

            event = {
                "type": "chat.message",
                "tip": message['tip'],
                "message": message.get('message'),
                "data": message['data'],
            }

        elif message.get('tip') == 2:
            event = {
                "type": "add.friends",
                "tip": message['tip'],
                "message": message.get('message'),
                "data": message['data']
            }
        if event:
            async_to_sync(channel_layer.send)(channel_name, event)
        else:
            raise Exception('序列化消息失败')