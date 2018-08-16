from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render, redirect
from users.models import User
import re
from celery_task.tasks import send_active_email
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TS
from utils import constants




# Create your views here.

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
            return redirect(reversed('users:register'))

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

        return HttpResponse('这个是首页')


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

        return HttpResponse('登陆页面')