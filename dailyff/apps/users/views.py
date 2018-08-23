from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render, redirect
from users.models import User,Address
from goods.models import GoodsSKU
import re

from celery_task.tasks import send_active_email
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TS
from utils import constants
from django_redis import get_redis_connection




# Create your views here.
from utils.commons import LoginRequiredMixin


class RegisterUser(View):
    def get(self, request):
        return render(request,'register.html')
    def post(self, request):
        """
        保存到数据库
        发送邮件

        :param request:
        :return:
        """
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        email = request.POST.get('email')
        check = request.POST.get('allow')

        if not all([username,password,password2,email,check]):
            return redirect(reverse('users:register'))

        if password!=password2:
            return render(request, 'register.html', {"errmsg": "两次密码不一致"})

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
            return render(request, 'register.html', {"errmsg": "邮箱格式不正确"})
        if check != "on":
            return render(request, 'register.html', {"errmsg": "请勾选同意协议"})
        try:
            user = User.objects.create_user(username,email, password)
        except Exception:
            return render(request, 'register.html', {"errmsg": "用户名已存在"})

        user.is_active = False
        user.save()

        # 生成token然后发送邮件
        active_token = user.generate_active_token()

        active_url = "http://127.0.0.1:8000/users/active/%s" % active_token

        send_active_email.delay(username,active_url,email)

        return redirect(reverse("user:login"))


class ActiveUser(View):
    def get(self,request,active_token):
        ts = TS(settings.SECRET_KEY,constants.ACTIVE_TOKEN_EXPIRED)
        try:
            msg = ts.loads(active_token)
        except Exception:
            return HttpResponse("链接已过期")
        id = msg.get('user_id')
        try:
            User.objects.filter(id=id).update(is_active=True)
        except Exception as e:
            return HttpResponse("链接无效")

        return redirect(reverse('users:login'))

class LoginView(View):
    def get(self,request):

        return render(request,'login.html')

    def post(self,request):

        username = request.POST.get('username')
        password = request.POST.get('pwd')

        if not all([username, password]):
            return render(request,'login.html',{'errmsg':"用户名或密码为空"})

        user = authenticate(username=username, password=password)

        if not user:
            return render(request,'login.html', {'errmsg':'用户名或密码错误'})

        if not user.is_active:
            return render(request, 'login.html', {'errmsg': "用户未激活"})
        # 用户登陆
        login(request, user)

        remember = request.POST.get('remember')

        if remember != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)

        return redirect(reverse('goods:index'))


class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect(reverse('users:login'))


class AddressView(LoginRequiredMixin, View):
    def get(self,request):
        user = request.user
        try:
            address = user.address_set.latest('update_time')
            return render(request,'user_center_site.html',{"address":address})
        except Exception as e:
            return render(request,'user_center_site.html',{"address":None})

    def post(self,request):
        receiver_name = request.POST.get('receiver_name')
        detail_addr = request.POST.get('detail_addr')
        zip_code = request.POST.get('zip_code')
        receiver_mobile = request.POST.get('receiver_mobile')

        if not all([receiver_mobile,zip_code, detail_addr, receiver_name]):
            return render(request,'user_center_site.html',{'errmsg':"信息填写不完整"})

        user = request.user
        # 保存数据至数据库中
        # address = Address(user=user,receiver_name=receiver_name,receiver_mobile=receiver_mobile,detail_addr=detail_addr,
        #                   zip_code=zip_code)
        # address.save()
        # 可以直接用create的方法,创建,省略保存的动作
        Address.objects.create(
            user=user,
            receiver_name=receiver_name,
            receiver_mobile=receiver_mobile,
            detail_addr=detail_addr,
            zip_code=zip_code

        )
        return redirect(reverse('users:address'))

class InfoView(LoginRequiredMixin, View):
    def get(self,request):
        user = request.user
        try:
            address = user.address_set.latest('update_time')
        except Exception as e:
            address = None

        redis_conn = get_redis_connection('default')
        history_key = 'history_%s' % user.id
        history = redis_conn.lrange(history_key,0,4)

        sku_list = []
        for i in history:
            sku = GoodsSKU.objects.get(id=i)
            sku_list.append(sku)

        context = {
            'address':address,
            'sku_list': sku_list
        }

        return render(request,'user_center_info.html',context)






