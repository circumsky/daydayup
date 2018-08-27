from django.contrib import admin
from goods.models import GoodsCategory, Goods, GoodsSKU,GoodsImage, IndexGoodsBanner
from goods.models import IndexCategoryGoodsBanner, IndexPromotionBanner
from django.core.cache import cache


# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        from celery_task.tasks import generate_static_index
        generate_static_index.delay()
        # 删除主页的缓存数据
        cache.delete('index_data')
        obj.save()

    def delete_model(self, request, obj):
        from celery_task.tasks import generate_static_index
        generate_static_index.delay()
        cache.delete('index_data')
        obj.delete()

class GoodsCategoryAdmin(BaseAdmin):
    pass

class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass
class IndexPromotionBannerAdmin(BaseAdmin):
    pass
class IndexGoodsBannerAdmin(BaseAdmin):
    pass

admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexCategoryGoodsBanner, IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)