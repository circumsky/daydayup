from celery import Celery


app = Celery("dailynew",broker="redis://127.0.0.1:6379/0")

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "dailyff.settings"

# import django
# django.setup()

from django.core.mail import send_mail
from django.conf import settings

@app.task
def send_active_email(username,active_url,email):
    msg_html = """
    <h1>%s您好</h1>
    <p>欢迎注册XX视频网站,请点击以下链接进行激活:</p>
    <a href="%s">%s</a>
    """ % (username, active_url, active_url)

    send_mail("XX视频网站激活", "", settings.EMAIL_HOST_USER, [email], html_message=msg_html)
