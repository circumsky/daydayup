from celery import Celery
from django.template import RequestContext
from django.template import loader

app = Celery("dailynew",broker="redis://127.0.0.1:6379/0")

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "dailyff.settings"
#
# import django
# django.setup()

from django.core.mail import send_mail
from django.conf import settings
from goods.models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner



@app.task
def send_active_email(username,active_url,email):
    msg_html = """
    <h1>%s您好</h1>
    <p>欢迎注册XX视频网站,请点击以下链接进行激活:</p>
    <a href="%s">%s</a>
    """ % (username, active_url, active_url)

    send_mail("XX视频网站激活", "", settings.EMAIL_HOST_USER, [email], html_message=msg_html)

@app.task
def generate_static_index():
    goods_categories = GoodsCategory.objects.all()
    # 论波图
    index_goods_banner = IndexGoodsBanner.objects.all().order_by('index')[:4]
    # 广告
    index_promotion_banner = IndexPromotionBanner.objects.all().order_by('index')[:2]
    # 首页展示的商品
    for goods_category in goods_categories:
        img_banner = IndexCategoryGoodsBanner.objects.filter(category=goods_category, display_type=1).order_by('index')[:4]
        title_banner = IndexCategoryGoodsBanner.objects.filter(category=goods_category, display_type=0).order_by('index')[:4]
        goods_category.img_banner = img_banner
        goods_category.title_banner = title_banner
    # 购物车数量
    cart_num = 0
    content = {
        'categories': goods_categories,
        'goods_banner': index_goods_banner,
        'promotion_banner': index_promotion_banner,
        'cart_num': cart_num
    }


    template = loader.get_template('index_forstatic.html')

    html = template.render(content)
    file_path = os.path.join(settings.BASE_DIR,'static/index.html')
    with open(file_path,'w') as f:
        f.write(html)

