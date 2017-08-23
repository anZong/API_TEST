# coding:utf-8
"""
Created on 2017/8/17
@author:zongan
"""
import json
import random

from django.conf.urls import patterns
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from base.utils import ex, ApiException, unlogin
from base.view import BaseView

from faker import Factory

token = ["F9E60975-CF4D-460A-83D6-CC4B38972EF1"]
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

            global token
            if apiname != 'bindUser' and param["_token"] and param["_token"] not in token:
                res={
                    "code":2001
                }
                return self.api_response(res)
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
MsgList = []
ProductList = []
ShopCart = []
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
                    'id':random.randint(1,100),
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

    @unlogin
    def getMessageList(self, page=1, size=10):
        TOTAL = 20
        global MsgList
        if int(page) == 1:
            fake = Factory.create('zh_CN')
            # raw_data = []
            for _ in range(TOTAL):
                tmp = {
                    'id':random.randint(1,100),
                    'title': fake.text(10),
                    'created':{
                        'date': fake.date(pattern="%Y-%m-%d")
                    },
                    'isreaded':fake.boolean(chance_of_getting_true=80),
                    'content': fake.text(50)
                }
                MsgList.append(tmp)
        _page = int(page)
        _size = int(size)
        data = {
            'total': TOTAL,
            'items': MsgList[(_page-1)*_size:_page*_size],
            'curpage': _page,
            'size':_size
        }
        return data

    @unlogin
    def getDetail(self, id=None):
        fake = Factory.create('zh_CN')
        data = {
            'id':id,
            'title': fake.text(10),
            'created':{
                'date': fake.date(pattern="%Y-%m-%d")
            },
            'isreaded':fake.boolean(chance_of_getting_true=80),
            'content': fake.text(100)
        }
        return data

    @unlogin
    def getUserInfo(self):
        fake = Factory.create('zh_CN')
        data = {
            'icon': fake.image_url(width=None, height=None),
            'name': fake.name(),
            'code': fake.ean(length=8)
        }
        return data

    @unlogin
    def bindUser(self, _token):
        global token
        token.append(_token)
        return {'msg':'綁定成功'}

    @unlogin
    def getProductList(self):
        fake = Factory.create('zh_CN')
        TOTAL = 50
        global ProductList
        if not ProductList:
            for _ in range(TOTAL):
                tmp = {
                    'id':random.randint(1,100),
                    'img':fake.image_url(width=120,height=120),
                    'name':fake.name(),
                    'color':fake.safe_color_name(),
                    'price':random.randint(1,100),
                    'desc':fake.text(50),
                    'stock':random.randint(1,100)
                }
                ProductList.append(tmp)
        data = {
            'total':TOTAL,
            'items':ProductList,
            'size':10,
            'curpage':2
        }
        return data

    @unlogin
    def getShopCart(self):
        global ShopCart
        fake = Factory.create('zh_CN')
        level = ['A','B','C','D']
        color = ['红','粉','紫','蓝','白']
        if not ShopCart:
            for _ in range(10):
                tmp = {
                    'id':random.randint(1,100),
                    'img':fake.image_url(),
                    'name':fake.text(5),
                    'price':random.randint(10,50),
                    'color':color[random.randint(0,4)],
                    'level':level[random.randint(0,3)],
                    'quantity':random.randint(1,10),
                }
                ShopCart.append(tmp)
        return ShopCart


class ApiDocView(BaseView):
    pass
urlpatterns = patterns('',
                       (r'apidoc\.html', ApiDocView.as_view()),
                       (r'(?P<apiname>\S+)', csrf_exempt(MainApiView.as_view()))
                       )
