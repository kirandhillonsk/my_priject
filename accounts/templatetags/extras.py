from datetime import datetime
from django import template
from requests import request
from accounts.models import *
from enduser.models import HelpRequest
from history.models import *
from notification.models import Notification
from rvt_lvt.models import *
from accounts.constants import *
from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

register = template.Library()


@register.filter(name='total_users')
def total_users(key):
    return User.objects.filter(role_id = USER).count()

"""
Users
"""
@register.filter(name='users')
def users(key):
    return User.objects.filter(role_id = 2).count()

@register.filter(name='active_users')
def active_users(key):
    return User.objects.filter(state_id = ACTIVE,role_id = USER).count()

@register.filter(name='inactive_users')
def inactive_users(key):
    return User.objects.filter(state_id = INACTIVE,role_id = USER).count()


@register.filter(name='rvt_users')
def rvt_users(key):
    return User.objects.filter(role_id = RVT_LVT).count()

@register.filter(name='active_rvt_users')
def active_rvt_users(key):
    return User.objects.filter(role_id = RVT_LVT,state_id = ACTIVE).count()

@register.filter(name='inactive_rvt_users')
def inactive_rvt_users(key):
    return User.objects.filter(role_id = RVT_LVT,state_id = INACTIVE).count()


@register.filter(name='total_appointment')
def total_appointment(key):
    return Appointments.objects.all().count()


@register.filter(name='total_login_history')
def total_login_history(key):
	return LoginHistory.objects.all().count()

@register.filter(name='total_rvt_users')
def total_rvt_users(key):
	rvt_user =  User.objects.filter(role_id = RVT_LVT).order_by('-id')[:5]
	return rvt_user

@register.filter(name='custom_request')
def custom_request(Key):
  return CustomService.objects.all().count()

@register.filter(name='regular_request')
def regular_request(key):
    return Services.objects.all().count()


"""
Total appointments on admin dashboard
"""
@register.filter(name='total_appointments')
def total_appointments(key):
    appointments = Appointments.objects.all().order_by('-created_on')[:10]
    return appointments
"""
Appointment Count
"""
@register.filter(name='appointments_count')
def appointments_count(key):
    appointments=Appointments.objects.all().count()
    return appointments


"""
Payment Status 
"""
@register.filter(name='payment_status')
def payment_status(key):
    transaction=Transactions.objects.all()
    return transaction

"""
Help Requests
"""
@register.filter(name='help_request')
def help_request(key):
    help_request=HelpRequest.objects.all().order_by('-created_on')[:4]
    return help_request
    
"""
Help request count
"""
@register.filter(name='help_request_count')
def help_request_count(key):
    help_request_count=HelpRequest.objects.all().count()
    return help_request_count

"""
Payouts status
"""
@register.filter(name='payout_status')
def payout_status(key):
    date=datetime.now().month
    transactions=Transactions.objects.filter(payment_type=PAYMENT)
    return transactions

"""
Total Revenue
"""
@register.filter(name='total_transactions')
def total_transactions(key):
    total_payments = sum([float(i.amount if i.amount else 0) for i in Transactions.objects.filter(payment_type=PAYMENT)])
    total_credits = sum([float(i.amount if i.amount else 0) for i in Transactions.objects.filter(payment_type=CREDIT)])
    total_refunds = sum([float(i.amount if i.amount else 0) for i in Transactions.objects.filter(payment_type=REFUND)])
    total_amount = float( total_payments - (total_credits + total_refunds))
    return total_amount


"""
Total Revenue for the month
"""
@register.filter(name='total_transactions_month')
def total_transactions_month(key):
    total_payments = sum([float(i.amount if i.amount else 0) for i in Transactions.objects.filter(payment_type=PAYMENT,created_on__month=datetime.now().month)])
    total_credits = sum([float(i.amount if i.amount else 0) for i in Transactions.objects.filter(payment_type=CREDIT,created_on__month=datetime.now().month)])
    total_refunds = sum([float(i.amount if i.amount else 0) for i in Transactions.objects.filter(payment_type=REFUND,created_on__month=datetime.now().month)])
    total_amount = float( total_payments - (total_credits + total_refunds))
    return total_amount


    

    
    

