# coding:utf-8
"""
Created on 2017/8/17
@author:zongan
"""
def asapi(logined=True, userrole=None, args=None):
    def _func(func):
        def __func(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        import inspect
        setattr(__func, 'argspec', inspect.getargspec(func))
        setattr(__func, 'doc', inspect.getdoc(func))
        return __func

    return _func


unlogin = asapi(logined=False)
logined = asapi(logined=True)
admin = asapi(userrole='admin')


class ApiException(BaseException):
    pass


def ex(e, c=-1):
    return ApiException({"code": c, "msg": e})