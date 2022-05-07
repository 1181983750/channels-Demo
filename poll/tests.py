from django.test import TestCase

# Create your tests here.

class A():

    def __init__(self, name):
        self.name = name
        self.config = {'batch_size': self.bs}

    @classmethod
    def set_bs(cls, bs):
        cls.bs = bs

    def print_config(self):
        print(self.config)


A.set_bs(4)
a = A('test')
a.print_config()
