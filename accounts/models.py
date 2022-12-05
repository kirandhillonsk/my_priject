x
 

from distutils.command.upload import upload
import os
from .constants import *
from django.db import models
from django.utils.encoding import smart_str
from django.http.response import HttpResponse
from django.contrib.auth.models import AbstractUser


"""
Bedge 
"""
class Badge(models.Model):
    title = models.CharField(max_length=255,blank=True,null=True)
    image=models.ImageField(upload_to='badge',null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tbl_badge' 


"""
User Model
"""
class User(AbstractUser):
    username = models.CharField(max_length=150,blank=True, null=True,unique=True)
    full_name = models.CharField(max_length=150,null=True,blank=True)
    first_name = models.CharField(max_length=150,null=True,blank=True)
    last_name = models.CharField(max_length=150,null=True,blank=True)
    email = models.EmailField("email address", null=True, blank=True)
    mobile_no = models.CharField(max_length=100, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pic/', blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=255,blank=True,null=True)
    state = models.CharField(max_length=255,blank=True,null=True)
    role_id = models.PositiveIntegerField(default=USERS,choices=USER_ROLE,null=True, blank=True)
    state_id = models.PositiveIntegerField(default=ACTIVE, choices=USER_STATUS,null=True, blank=True)
    status = models.BooleanField(default=True)
    job_status= models.PositiveIntegerField(default=0, choices=JOB_APPLY_STATUS,null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    year_of_experience = models.CharField(max_length=2,blank=True,null=True)
    resume = models.FileField(upload_to='resume',blank=True,null=True)
    registration_no = models.CharField(max_length=60,blank=True,null=True,)
    is_verified = models.PositiveIntegerField(default=0,choices=IS_VERIFIED,null=True, blank=True)
    about_me = models.TextField()
    average_rating = models.CharField(max_length=10,blank=True, null =True)
    otp = models.CharField(max_length=255,blank=True,null=True)
    verify_otp = models.BooleanField(default=0)
    is_subscribe = models.BooleanField(default=0)
    applied_for = models.CharField(max_length=10,null=True,blank=True)
    user_to_rvt=models.BooleanField(default=0)
    features_approval = models.BooleanField(default=0)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    country = models.CharField(max_length=255,blank=True,null=True)
    session_id = models.CharField(max_length=500,blank=True,null=True)
    badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, blank=True, null=True)
    customer_id = models.CharField(max_length=255,blank=True,null=True)
    bank_account_id = models.CharField(max_length=255,blank=True,null=True)
    social_id = models.CharField(max_length=255,blank=True,null=True)
    userId = models.CharField(max_length=255,blank=True,null=True)
    social_type = models.PositiveIntegerField(null=True, blank=True, choices=SOCIAL_TYPE)
    expiry_date = models.CharField(max_length=50,blank=True,null=True,)
    is_push = models.BooleanField(default=True)
    is_email =  models.BooleanField(default=True)
    is_text =  models.BooleanField(default=True)
    is_direct_message =  models.BooleanField(default=True)
    is_location_tracking =  models.BooleanField(default=True)
    is_verify_mail = models.BooleanField(default=False)
    email_sent_on = models.DateTimeField(auto_now_add=False,null=True, blank=True)
    default_currency = models.CharField(max_length=50,blank=True,null=True, default="cad")
    
    @classmethod
    def Downloadfile(zips,path,upload):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path= os.path.join(BASE_DIR)
        
        file_path = f"media/{upload}"
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(),content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(upload)
            response['X-Sendfile'] = smart_str(path)
        return response

    class Meta:
        managed = True;
        db_table = 'tbl_user'

    def __str__(self):
        return str(self.username)


"""
device model
"""
class Device(models.Model):
    created_by = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='created_by')
    device_type = models.PositiveIntegerField(choices=DEVICE_TYPE,null=True,blank=True)
    device_name = models.CharField(max_length=500,null=True,blank=True)
    device_token = models.CharField(max_length=500,null=True,blank=True)
    
    class Meta:
        managed = True
        db_table = 'tbl_device'

    def __str__(self):
        return str(self.device_name)


"""
apply for job
"""
class JobApply(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    mobile_no = models.CharField(max_length=255, blank=True, null=True)
    upload_resume = models.FileField(upload_to='resumes')
    status = models.CharField(max_length=255,choices=JOB_APPLY_STATUS,default=0)


    class Meta:
        managed = True
        db_table = 'tbl_job_apply'



"""
Become RVT
"""
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    role_id = models.PositiveIntegerField(default=3,choices=USER_ROLE,null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    class Meta:
        managed = True;
        db_table = 'user_role'


"""
subscription
"""
class Subscription(models.Model):
    email = models.CharField(max_length=255,blank=True,null=True) 
    created_on = models.DateTimeField(auto_now_add=True)
    class Meta:
        managed = True;
        db_table = 'tbl_subscription'

