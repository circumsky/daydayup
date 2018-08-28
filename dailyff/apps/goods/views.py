from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from .models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner, GoodsSKU
from django.core.cache import cache
from utils.constants import INDEX_DATA_EXPIRED,DETAIL_DATA_EXPIRED
from orders.models import OrderGoods
from django_redis import get_redis_connection


class IndexView(View):
    def get(self, request):
        # 需要获取的内容
        # 全部商品分类
        context = cache.get('index_data')
        if context == None:
            goods_categories= GoodsCategory.objects.all()
            # 论波图
            index_goods_banner = IndexGoodsBanner.objects.all().order_by('index')[:4]
            # 广告
            index_promotion_banner = IndexPromotionBanner.objects.all().order_by('index')[:2]
            # 首页展示的商品
            for goods_category in goods_categories:
                img_banner = IndexCategoryGoodsBanner.objects.filter(category=goods_category,display_type=1).order_by('index')[:4]
                title_banner = IndexCategoryGoodsBanner.objects.filter(category=goods_category,display_type=0).order_by('index')[:4]
                goods_category.img_banner = img_banner
                goods_category.title_banner = title_banner
            # 购物车数量

            context = {
                'categories': goods_categories,
                'goods_banner': index_goods_banner,
                'promotion_banner': index_promotion_banner,

            }
            cache.set('index_data',context,INDEX_DATA_EXPIRED)

        cart_num = 0
        context['cart_num'] = cart_num


        return render(request,'index.html', context)

class GoodDetailView(View):
    def get(self,request,sku_id):
        # 商品类别
        context = cache.get('detail_%s' % sku_id)
        if context == None:

            categories = GoodsCategory.objects.all()
            # 商品sku
            sku = GoodsSKU.objects.get(id=sku_id)
            # 同spu的其他商品
            other_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku_id)
            # 新品推荐
            new_goods = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[:2]
            # 评论
            comments = OrderGoods.objects.filter(sku=sku).order_by('-create_time')[:20]

            context = {
                'categories': categories,
                'sku': sku,
                'other_skus':other_skus,
                'new_goods':new_goods,
                'comments':comments
            }
            cache.set('detail_%s' % sku_id,context,DETAIL_DATA_EXPIRED)
        cart_num = 0
        context['cart_num'] = cart_num
        user = request.user
        if user.is_authenticated:
            conn = get_redis_connection('default')
            key = "history_%s" % user.id
            conn.lrem(key,0,sku_id)
            conn.lpush(key,sku_id)
            conn.ltrim(key,0,4)


        return render(request,'detail.html',context)

class ListView(View):
    def get(self,request,category_id,page):
        # 排序方式
        sort = request.GET.get('sort','default')
        page = int(page)


        categories = GoodsCategory.objects.all()
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            return redirect(reverse('goods:index'))

        # 新品推荐
        new_goods = GoodsSKU.objects.filter(category=category).order_by('-create_time')[:2]

        # 排序方式返回结果
        if sort == 'price':
            skus = GoodsSKU.objects.filter(category=category).order_by('price')
            # print(skus)
        elif sort == 'sale':
            skus = GoodsSKU.objects.filter(category=category).order_by('-sales')
            # print(skus)
        else:
            skus = GoodsSKU.objects.filter(category=category).order_by('-create_time')
            # print(skus)

        # 创建分页器对象
        paginator = Paginator(skus,1)
        # 获取当前页面的全部内容
        try:
            page_skus = paginator.page(page)
        except Exception:
            page = 1
            page_skus = paginator.page(page)
        # 显示页面列表

        if paginator.num_pages <= 5:
            print(paginator.page_range)
            page_num = paginator.page_range
        else:
            if page <= 3:
                page_num = list(range(1,6))
            elif page >= (paginator.num_pages-2):
                page_num = list(range(paginator.num_pages-4,paginator.num_pages+1))
            else:
                page_num = list(range(page-2,page+3))

        cart_num = 0
        context = {
            'categories':categories,
            'category':category,
            'new_goods':new_goods,
            'page_skus':page_skus,
            'page_num':page_num,
            'cart_num':cart_num,
            'sort':sort
        }

        return render(request,'list.html',context)





