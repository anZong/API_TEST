# coding:utf-8
"""
Created on 2017/8/17
@author:zongan
"""
import json

from django.conf.urls import patterns
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from base.utils import ex, ApiException, unlogin
from base.view import BaseView

from faker import Factory


class ApiView(BaseView):
    def api_response(self, v):
        res = HttpResponse(json.dumps(v), content_type="text/json")
        return res

    def get(self, request, apiname, *args, **kwargs):
        try:
            if not apiname:
                raise ex('接口不能为空')
            apifun = None
            try:
                apifun = getattr(self, apiname)
            except:
                raise ex('不存在接口%s' % apiname)

            # 存放函数参数键值对
            kvargs = {}

            # 提交的参数
            param = {}
            param.update(request.GET.items())
            param.update(request.POST.items())

            # api函数的参数
            argspec = getattr(apifun, 'argspec')
            funcargs = argspec.args
            defaults = argspec.defaults

            if defaults:
                for i, v in enumerate(funcargs[-len(defaults):]):
                    kvargs[v] = defaults[i]

            if len(funcargs):
                argslen = len(funcargs) - (len(defaults) if defaults else 0) - 1
                missargs = []
                for i, k in enumerate(funcargs[1:]):
                    if k in param:
                        kvargs[k] = param[k]
                    elif i < argslen:
                        missargs.append(k)

                if missargs:
                    raise ex('缺失参数:%s' % (','.join(missargs)))

            res = apifun(**kvargs)

            if res != None:
                res = {'code':0,'data':res}

            return self.api_response(res)
        except ApiException, e:
            return self.api_response(e.args[0])

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

ListData = []
class MainApiView(ApiView):

    @unlogin
    def getNewsList(self, id=None, page=1, size=10):
        TOTAL = 20
        global ListData
        if page == 1:
            fake = Factory.create('zh_CN')
            # raw_data = []
            for _ in range(TOTAL):
                tmp = {
                    'title': fake.text(10),
                    'img':fake.image_url(width=None, height=None),
                    'city': fake.city(),
                    'created':{
                        'date': fake.date(pattern="%Y-%m-%d")
                    },
                    'address': fake.address(),
                    'intro': fake.text(50)
                }
                ListData.append(tmp)
        _page = int(page)
        _size = int(size)
        data = {
            'total': TOTAL,
            'items': ListData[(_page-1)*_size:_page*_size],
            'curpage': _page,
            'size':_size
        }
        return data


class ApiDocView(BaseView):
    pass


urlpatterns = patterns('',
                       (r'apidoc\.html', ApiDocView.as_view()),
                       (r'(?P<apiname>\S+)', csrf_exempt(MainApiView.as_view()))
                       )
