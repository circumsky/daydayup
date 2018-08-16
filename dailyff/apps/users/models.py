from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.models import BaseModel
from itsdangerous import TimedJSONWebSignatureSerializer as TS
from django.conf import settings
from utils import constants


# Create your models here.


class User(AbstractUser, BaseModel):
    """用户"""
    class Meta:
        db_table = "df_users"

    def generate_active_token(self):
        ts = TS(settings.SECRET_KEY, constants.ACTIVE_TOKEN_EXPIRED)

        active_token = ts.dumps({"user_id": self.id})

        return active_token.decode()


class Address(BaseModel):
    """地址"""
    user = models.ForeignKey(User, verbose_name="所属用户")
    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, verbose_name="邮政编码")

    class Meta:
        db_table = "df_address"