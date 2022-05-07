from datetime import datetime
from typing import Union, Dict, List, Any
from utils.public.onlineTime import getBeijinTime


class ResponseResult:

    def __init__(self, msg: str = '', data: Union[Dict, List] = None, code: int = -1, **kwarg):
        self.__result = {'msg': msg, 'data': data, 'code': code}
        self.__result.update(kwarg)

    def __call__(self, *args, **kwargs):
        return self.__result


def response_result(msg: str = '', data: Dict = None, code: int = -1, **kwargs) -> Dict[str, Union[str, Dict, int]]:
    """
    返回给前端整理返回数据函数

    Args:
        msg: 返回信息
        data: 返回数据
        code: 返回状态
        **kwargs: 可选参数

    Returns:

    """
    result = {'code': code, 'msg': msg, 'data': data}
    result.update(kwargs)
    return result


class BaseSocketData:

    def __init__(self, tip: int, sender: Union[int, str], recipient: Union[int, str] = 0, group_id: int = 0,):
        self.data = {'tip': tip,
                     'data': {
                         'group_id': group_id,
                         'send': sender,
                         'to': recipient
                     }}

    def __call__(self, *args, **kwargs):
        return self.data


class BaseSocketDataBody:

    def __init__(self, *args, **kwargs):
        self.__data_body = {}

    def __call__(self, *args, **kwargs):
        return self.__data_body


class SocketAddFriendDataBody(BaseSocketDataBody):

    def __init__(self, tip: int, apply: int):
        super(SocketAddFriendDataBody, self).__init__(tip, apply)
        self.__data_body = {'tip': tip, 'apply': apply}

    def __call__(self, *args, **kwargs):
        return self.__data_body

class Sockettaskbody(BaseSocketDataBody):
    def __init__(self, tip: int, apply: int):
        super(Sockettaskbody, self).__init__(tip, apply)
        self.__data_body = {'tip': tip, '工单': apply}

    def __call__(self, *args, **kwargs):
        return self.__data_body

class SocketDataBuild:

    def __init__(self):
        self._result_data = {}
        self._main_data = {}
        self._data_body = {}

    def create_data(self, main_data: BaseSocketData):
        self._main_data = main_data()
        return self

    def create_data_body(self, data_body: BaseSocketDataBody):
        self._data_body = data_body()
        return self

    def build_socket_data(self, **kwargs):
        self._main_data['data']['data'] = self._data_body
        self._result_data.update(self._main_data)
        self._result_data.update(kwargs)
        return self._result_data

"""
def socket_send(tip: int,
                data: Any,
                data_type: str,
                sender: Union[str, int] = None,
                recipient: Union[str, int] = 0,
                group_id: Union[str, int] = 0,
                client_msg_id: Union[str, int] = 0):
    socket消息发送格式

    Args:
        client_msg_id: 客户端消息id
        group_id: 群id
        tip: 发送消息的类型 0-回执给客户端消息 1-聊天消息收发标识 2-好友添加通知 3-对方成功收到消息回执
        sender: 消息发送者
        recipient: 消息接受者
        data: 发送数据体
        data_type: 发送数据类型

    Returns:
    now = datetime.strptime(getBeijinTime()[1], '%Y-%m-%d %H:%M:%S')
    date = int(datetime.timestamp(now))

    if not data_type:
        data_type = 'txt'
        data = ''

    if not sender:
        return {
            'tip': tip,
            'data':
                {
                    'to': recipient,
                    'group_id': group_id,
                    'data':
                        {
                            'tip': data_type,
                            data_type: data,
                            'date': date,
                            'client_msg_id': client_msg_id
                        }
                }
        }
    result = {
        'tip': tip,
        'data':
            {
                'send': sender,
                'to': recipient,
                'group_id': group_id,
                'data':
                    {
                        'tip': data_type,
                        data_type: data,
                        'date': date,
                        'client_msg_id': client_msg_id
                    }
            }
    }
    return result
"""

if __name__ == '__main__':
    main_data = BaseSocketData(tip=1, sender=1, recipient=1)
    body = SocketAddFriendDataBody(tip=1, apply=1)
    task = Sockettaskbody(tip=3,apply=-1)
    build = SocketDataBuild()
    data = build.create_data(main_data).create_data_body(task).build_socket_data()
    print('1111111111', data)

