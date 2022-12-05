from datetime import datetime, timedelta
from accounts.constants import SCHEDULED
from accounts.models import Device
from rvt_lvt.models import Appointments
from rvt_lvt.models import Appointments
from datetime import datetime, timedelta
from pyfcm import FCMNotification
import environ
env = environ.Env()
environ.Env.read_env()

def early_notiifcation():
    appointment = Appointments.objects.filter(status = SCHEDULED)
    for app in appointment:
        date = app.date - timedelta(days=1)
        current_date = datetime.now().date()
        difference = date - current_date
        if '-1' in str(difference):
            push_service = push_service = FCMNotification(api_key=env('FCM_KEY'))
            device = Device.objects.filter(created_by_id = app.created_by_id)
            list_data =[]
            for dvc in device:
                list_data.append(dvc.device_token)
            msg = {
                "title":"Appointment Reminder",
                "description":"Your appointment is scheduled on {}".format(app.date),
                "type":'Reminder',
            }
            message_title = msg['title']
            message_body = msg['description']
            result = push_service.notify_multiple_devices(
                        registration_ids = list_data, 
                        message_title = message_title, 
                        message_body = message_body,
                        data_message={"message_title" :msg['title'],"message_body" : msg['description'], "type" : msg['type'],
                    })
        else:
            pass    