import threading
import traceback
from typing import Type, Any, Dict, Union

from django.db import models
from rest_framework.serializers import ModelSerializer

from utils.public.response_result import ResponseResult


class BaseModel:

    def __str__(self):
        repr_str = 'Object: {}:〔'.format(self.__class__.__name__)
        index = 0
        for k, v in self.__dict__.items():
            index += 1
            if index < len(self.__dict__.items()):
                repr_str += '{}={}, '.format(k, v)
            else:
                repr_str += '{}={}'.format(k, v)
        return repr_str + '〕'

    __repr__ = __str__


class BaseORM:
    """
    数据库模型增、删、改、查基类
    """

    def __init__(self, model: Type[models.Model]):
        self.model = model

    def add(self, add_data: Union[models.Model, Dict]):
        """
        新增数据

        Args:
            add_data:Union[Type[Model], Dict]  新增数据对象

        Returns:

        """
        if isinstance(add_data, models.Model):
            return add_data.save()
        if isinstance(add_data, Dict):
            return self.model.objects.create(**add_data)
        raise Exception('添加数据类型错误')

    def delete_by_id(self, ids: str) -> int:
        """
        根据id删除数据

        Args:
            ids: 数据id

        Returns:

        """
        return self.model.objects.filter(id=ids).delete()[0]

    def update_by_id(self, ids: str, update_data: Dict):
        """
        根据id更新数据

        Args:
            ids: 数据id
            update_data: 更新数据对象

        Returns:

        """
        return self.model.objects.filter(id=ids).update(**update_data)

    def get_query_set_by_id(self, ids: str):
        """
        根据id查询指定数据

        Args:
            ids: id

        Returns:

        """
        return self.model.objects.get(id=ids)

    def get_all(self):
        """
        查询所有数据

        Returns:

        """
        return self.model.objects.all()


# noinspection PyBroadException
class BaseService:
    """
    所有业务逻辑类基类
    """

    def __init__(self, model: Type[models.Model]):
        self.orm = BaseORM(model)

    def add(self, add_data: Union[Dict, models.Model], serializer: Type[ModelSerializer] = None) -> Dict:
        """
        新增数据

        Args:
            add_data:dict  新增数据对象

        Returns:

        """
        try:
            result = self.orm.add(add_data=add_data)
        except Exception:
            return ResponseResult(msg='添加失败')()
        if not serializer:
            result = result.__dict__
            del result['_state']
        else:
            result = serializer(instance=result)
        return ResponseResult(msg='添加成功', code=1, data=result)()

    def delete_by_id(self, ids: str) -> int:
        """
        根据id删除数据

        Args:
            ids: 数据id

        Returns:

        """

        try:
            result = self.orm.delete_by_id(ids=ids)
        except Exception:
            traceback.print_exc()
            return 0
        return result

    def update_by_id(self, ids: str, update_data: Dict) -> int:
        """
        根据id更新数据

        Args:
            ids: 数据id
            update_data: 更新数据对象

        Returns:

        """
        try:
            result = self.orm.update_by_id(ids=ids, update_data=update_data)
        except Exception:
            traceback.print_exc()
            return 0
        return result

    def get_query_set_by_id(self, ids: str) -> Dict:
        """
        根据id查询指定数据

        Args:
            ids: id

        Returns:

        """
        try:
            result = self.orm.get_query_set_by_id(ids=ids)
        except models.Model.DoesNotExist:
            return ResponseResult(msg='查询失败，没有id为[{}]的数据'.format(ids), code=-1)()
        result = result.__dict__
        del result['_state']
        return ResponseResult(msg='查询成功', code=1, data=result)()

    def get_all(self) -> Dict:
        """
        查询所有数据

        Returns:

        """
        try:
            result = self.orm.get_all()
        except Exception:
            traceback.print_exc()
            return ResponseResult(msg='查询失败')()
        result_list = []
        for i in result:
            del i.__dict__['_state']
            result_list.append(i)
        return ResponseResult(msg='查询成功', code=1, data=result_list)()


class Container:
    """
    容器对象，该类为单例模式，确保任何时候获取该对象时都是同意个对象，从而保证放入该容器的对象可以正常获取
    """

    # _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> object:
        if not hasattr(cls, "_instance"):  # 返回Boolean
            with cls._instance_lock:
                instance = super(__class__, cls).__new__(cls)
                setattr(cls, "_instance", instance)  # 设置属性 cls._instance = object  同理
        return getattr(cls, "_instance")

    def __init__(self):
        self.__member_obj = {}

    @classmethod
    def get_instance(cls):
        """
        获取容器对象实例

        Returns:

        """
        if getattr(cls, '_instance', None):
            return getattr(cls, '_instance')
        else:
            return Container()

    def add_obj_to_container(self, key: str, obj: Any):
        """
        添加对象到容器中

        Args:
            key: 键
            obj: 对象

        Returns:

        """
        if key not in self.__member_obj.keys():
            self.__member_obj[key] = obj

    def re_set_obj(self, key: str, obj: Any):
        """
        通过键从新设定已在容器中的对象，如果从新设置容器中不存在的对象，则不进行任何操作

        Args:
            key: 键
            obj: 对象

        Returns:

        """
        if key in self.__member_obj.keys():
            self.__member_obj[key] = obj

    def get_obj_of_key(self, key: str) -> Dict[str, Any]:
        """
        通过键获取容器中的对象，若容器中不存在该键的对象返回None

        Args:
            key: 键

        Returns:

        """
        return self.__member_obj.get(key)

    def del_obj_of_key(self, key: str):
        """
        通过键删除容器中的对象，如果删除容器中不存在的对象，则不进行任何操作

        Args:
            key: 键

        Returns:

        """
        if key in self.__member_obj.keys():
            del self.__member_obj[key]
