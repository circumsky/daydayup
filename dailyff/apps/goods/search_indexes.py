from haystack import indexes
from .models import GoodsSKU

class GoodsSKUIndex(indexes.SearchIndex,indexes.Indexable):
    """
    创建一个索引声明类
    get_mdel 指定建立索引的模型
    index_queryset对返回的结果进行过率
    定义的text字段:
        这个有点相簿清楚具体是指什么,我理解的话就是建立索引的字段设置,类似模型类的字段,其中可使用木板的意思就是我们可以在
        模板中设置这个索引字段要根据模板中声明的模型类的字段来设置.
    """
    text = indexes.CharField(document=True,use_template=True)

    def get_model(self):
        return GoodsSKU

    def index_queryset(self, using=None):
        return self.get_model().objects.all()