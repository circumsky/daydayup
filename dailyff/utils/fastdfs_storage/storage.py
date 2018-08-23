from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings

class MyStorage(Storage):
    def __init__(self,client_conf=None,nginx_url=None):
        if not client_conf:
            client_conf = settings.STORAGE_CLIENT_CONF
        self.client_conf = client_conf
        if not nginx_url:
            nginx_url = settings.FASTDFS_NGINX_URL

        self.nginx_url = nginx_url

    def _open(self,name, mode='rb'):
        pass

    def _save(self,name,content):
        client = Fdfs_client(self.client_conf)
        file_data = content.read()

        ret = client.upload_by_buffer(file_data)

        status = ret.get('Status')

        if status != 'Upload successed.':
            raise Exception('文件保存错误')
        else:
            file_id = ret.get('Remote file_id')

            return file_id

    def exists(self, name):
        return False

    def url(self,name):
        path = self.nginx_url + name

        return path





