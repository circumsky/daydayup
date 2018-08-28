import json

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection

# Create your views here.
from utils.constants import CART_INFO_EXPIRED


class AddCartView(View):
    def post(self,request):
        sku_id = request.POST.get('sku_id')
        sku_count = request.POST.get('sku_count')
        # 校验参数
        if not all([sku_id, sku_count]):
            return JsonResponse({"code":"1","errmsg": "参数不完整"})
        try:
            sku_count = int(sku_count)
        except Exception:
            return JsonResponse({"code": "2", "errmsg": "参数有误"})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception:
            return JsonResponse({"code":"3","errmsg":"商品不存在"})

        if sku_count > sku.stock:
            return JsonResponse({"code":"4","errmsg":"库存不足"})

        #业务处理
        if request.user.is_authenticated():
            user = request.user
            # 添加redis

            conn = get_redis_connection("default")

            cart_count = conn.hget("cart_%s" % user.id,sku_id)
            if cart_count:
                sku_count += int(cart_count)

            conn.hset("cart_%s" % user.id,sku_id,sku_count)


            cart_info = conn.hgetall("cart_%s" % user.id)
            cart_num = 0
            for num in cart_info.values():

                cart_num += int(num)

            return JsonResponse({"code":0,"msg":"加入购物车成功","cart_num":cart_num})
        else:
            cart_info_str = request.COOKIES.get('cart_info')
            if cart_info_str:
                cart_info = json.loads(cart_info_str)
            else:
                cart_info = {}

            cart_count = cart_info.get(sku_id)
            if cart_count:
                sku_count += int(cart_count)

            cart_info[sku_id] = sku_count

            new_cart_info_str = json.dumps(cart_info)
            cart_num = 0

            for num in cart_info.values():
                cart_num += num
            ret = JsonResponse({"code":0,"msg":"加入购物车成功","cart_num":cart_num})

            ret.set_cookie("cart_info",new_cart_info_str,max_age=CART_INFO_EXPIRED)


            return ret


