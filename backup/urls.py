x
from . import views
from django.conf.urls import url
from django.contrib import admin

admin.autodiscover()

app_name = 'backup'

urlpatterns = [
    url(r'^$', views.backup, name='backup'),
    url(r'^database-backup/$', views.database_backup, name='database_backup'),
    url(r'^database-schema/$', views.database_schema, name='database_schema'),
    url(r'^download-file/$', views.downloadFile, name='downloadFile'),
    url(r'^delete-backup/$', views.DeleteBackup, name='delete_backup'),
]