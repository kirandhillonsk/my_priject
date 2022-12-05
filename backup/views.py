x
 
import os
import time
import environ
import logging
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.http.response import HttpResponse
from django.shortcuts import render ,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


db_logger = logging.getLogger('db')

env = environ.Env()
environ.Env.read_env()


@login_required
def backup(request):
	try:
		backup = backups.objects.all().order_by('-create_on')
		page = request.GET.get('page', 1)
		paginator = Paginator(backup, 10)
		try:
			backup = paginator.page(page)
		except PageNotAnInteger:
			backup = paginator.page(1)
		except EmptyPage:
			backup = paginator.page(paginator.num_pages)
	except Exception as e:
		db_logger.exception(e)
		backup = None
	return render(request, "backup/backup.html",{"title":"Backup","backup":backup, 'nbar':'backup','dis':'dis'})


@login_required
def downloadFile(request):
	try:
		BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		path= os.path.join(BASE_DIR)
		backup = backups.objects.get(id=request.GET.get("id"))
		file_name = backup.Name
		file_path = f"{path}/backup/sql_files/{file_name}"
		filepath= file_path
		with open(filepath, 'r') as f:
			response = HttpResponse(f.read(), content_type='application')
			response['Content-Disposition'] = 'inline; filename=' + file_name
	except Exception as e:
		db_logger.exception(e)			
	return backups.Downloadfile(response,file_name)


@login_required
def database_backup(request):
	try:
		username = 'admin' #env('LOCAL_DB_USERNAME')
		password = 'admin@123'#env('LOCAL_DB_PASSWORD')
		database = 'x'#env('LOCAL_DB_NAME')
		BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		path= os.path.join(BASE_DIR)
		BACKUP_PATH = f'{path}/backup/sql_files/'
		DATETIME = time.strftime('%Y%m%d-%H%M%S')
		TODAYBACKUPPATH = BACKUP_PATH + '/' + DATETIME
		dumpcmd = "mysqldump -h " + "localhost" + " -u " + username + " -p" + password + " " + database + " > " + BACKUP_PATH + "/" + database+DATETIME + ".sql"
		os.system(dumpcmd)
		name = database+DATETIME + ".sql"
		size = os.path.getsize(f"{path}/backup/sql_files/"+name)
		DATETIME = time.strftime('%Y-%m-%d %H:%M:%S')
		value = backups.objects.create(Name=name,Size=size,create_on=DATETIME,is_schema=False)

		messages.add_message(request, messages.INFO, 'Database Backup Created Successfully!')
	except Exception as e:
		db_logger.exception(e)
	return redirect('backup:backup')


@login_required
def database_schema(request):	
	try:
		username = 'admin' #env('LOCAL_DB_USERNAME')
		password = 'admin@123'#env('LOCAL_DB_PASSWORD')
		database = 'x'#env('LOCAL_DB_NAME')
		BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		path= os.path.join(BASE_DIR)
		SCHEMA_PATH = f'{path}/backup/sql_files/'
		DATETIME = time.strftime('%Y%m%d-%H%M%S')
		TODAYBACKUPPATH = SCHEMA_PATH + '/' + DATETIME
		dumpcmd = "mysqldump -h " + "localhost" + " -u " + username + " -p" + password + " --no-data " + database + " > " + SCHEMA_PATH + "/" + database+DATETIME + ".sql"
		os.system(dumpcmd)
		name= database+DATETIME + ".sql"
		size = os.path.getsize(f"{path}/backup/sql_files/"+name)
		DATETIME = time.strftime('%Y-%m-%d %H:%M:%S')
		value = backups.objects.create(Name=name,Size=size,create_on=DATETIME,is_schema=True)

		messages.add_message(request, messages.INFO, 'Database Schema Created Successfully!')
	except Exception as e:
		db_logger.exception(e)
	return redirect('backup:backup')


@login_required
def DeleteBackup(request):
	try:
		if request.method == 'GET':
			backup = backups.objects.get(id=request.GET.get("id"))
			if backup:
				backup.delete()
	except Exception as e:
		db_logger.exception(e)
	return render(request, 'backup/backup.html')