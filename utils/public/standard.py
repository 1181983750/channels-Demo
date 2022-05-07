
"""
 上面和下面功能一样 都是判断对象的键或值是否存在，
 使用方法:
 self.send_receive(object=message, checkarr=['tip', {'data':['to',{'data':['tip','txt',{'d':['dx']}]}]}])
 self.check(message, {'1':['tip', 'data'], '2-data':['to', 'data'], '3-data':['tip', 'txt','file']})
 """
class Standard:
    def __init__(self):
        print('进来了，要super（）类继承续写')
    def send_receive(self,object,checkarr):
        for i in checkarr:
            if type(i) is dict:
                key = next(i.keys().__iter__())
                self.send_receive(i, key)
            else:
                if i not in object:
                    print(i,'不在里面')
                    raise Exception(i,'不在里面')

    # def send_receive(self,object,checkarr):
    #     for i in checkarr:
    #         if type(i) is dict:
    #             key1 = next(i.keys().__iter__())
    #             for j in i[key1]:
    #                 if type(j) is dict:
    #                     key2 = next(j.keys().__iter__())
    #                     for z in j[key2]:
    #                         if type(z) is dict:
    #                             key3 = next(z.keys().__iter__())
    #                             for x in z[key3]:
    #                                 if type(x) is dict:
    #                                     key4 = next(x.keys().__iter__())
    #                                     for c in x[key4]:
    #                                         if type(c) is dict:
    #                                             print('还没做呢')
    #                                         else:
    #                                             if c not in object[key1][key2][key3][key4]:
    #                                                 print(c, '不在里面')
    #                                                 raise Exception(c,'不在里面')
    #                                 else:
    #                                     if x not in object[key1][key2][key3]:
    #                                         print(x,'不在里面')
    #                                         raise Exception(x,'不在里面')
    #                         else:
    #                             if z not in object[key1][key2]:
    #                                 print(z, '不在里面')
    #                                 raise Exception(z,'不在里面')
    #                 else:
    #                     if j not in object[key1]:
    #                         print(j,'不在里面')
    #                         raise Exception(j,'不在里面')
    #         else:
    #             if i not in object:
    #                 print(i,'不在里面')
    #                 raise Exception(i,'不在里面')


    """
    上面和下面功能一样 都是判断对象的键或值是否存在，
    使用方法:
    self.send_receive(object=message, checkarr=['tip', {'data':['to',{'data':['tip','txt',{'d':['dx']}]}]}])
    self.check(message, {'1':['tip', 'data'], '2-data':['to', 'data'], '3-data':['tip', 'txt','file']})
    """
    def check(self,dict_obj, dict_check):
        def check__(dict_, key):
            if not isinstance(dict_, dict):
                return False
            if key in dict_ and dict_[key] is not None:
                return True
            else:
                return False
        starts = []
        for i in range(10):
            starts.append(str(i))

        for key, value in dict_check.items():
            for index in starts:
                if key.startswith(index):
                    if key == '1':
                        for c_item in value:
                            if not check__(dict_obj, c_item):
                                print(key)
                                print(dict_obj, c_item)
                                print(c_item + '不在里面')
                                raise Exception(c_item + '不在里面')
                    else:
                        dict_key = key.split('-').pop()
                        dict_obj = dict_obj[dict_key]
                        for c_item in value:
                            if not check__(dict_obj, c_item):
                                print(key)
                                print(c_item + '不在里面')
                                raise Exception(c_item + '不在里面')


