x
from django.contrib.sessions.models import Session
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from datetime import datetime
import os
import re
import logging
import random as r
from django.conf import settings
import stripe
import environ
import random
from enduser.models import Card, HelpRequest
from superuser.models import NewsletterSubscription
from .forms import *
from .models import *
from frontend.views import *
from rvt_lvt.models import *
from django.db.models import Q
from enduser.models import Card
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import View
from history.models import LoginHistory
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from rest_framework.authtoken.models import Token
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password,check_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from datetime import timedelta
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
env = environ.Env()
environ.Env.read_env()
stripe.api_key = env('STRIPE_KEY')
db_logger = logging.getLogger('db')


"""
Card Validation
"""
@login_required
def CardValidation(request):
    if request.is_ajax():
        data ={"exists":None}
        card = request.GET.get("card_id")
        try:
            card_number = Card.objects.get(ac_no = card)
            data['exists'] = "1"
        except:
            data['exists'] = "0"
        return JsonResponse(data)

"""
Email Validation
"""
def EmailValidation(request):
    if request.is_ajax():
        data ={"valid":None,"exists":None,"empty":None}
        email = request.GET.get("email_id")
        pat = r'^[a-zA-Z0-9_.+-]+[@]\w+[.]\w{2,3}$'
        match = str(re.search(pat,email))
        try:
            user_email = User.objects.filter(Q(state_id=ACTIVE)|Q(state_id=INACTIVE),email=email).last()
            if email == user_email.email:
                data['exists'] = '1'
        except:
            user_email = None
        if email == '':
            data['empty'] = '1'

        if user_email == None:
            data['exists'] = '0'    
        
        if match == "None":
            data['valid'] = '0'
        else:
            data['valid'] = '1'
        return JsonResponse(data)

"""
RVT Email Validation
"""
def RvtEmailValidation(request):
    if request.is_ajax():
        data ={"valid":None,"exists":None,"empty":None}
        email = request.GET.get("rvt_email_id")
        pat = r'^[a-zA-Z0-9_.+-]+[@]\w+[.]\w{2,3}$'
        match = str(re.search(pat,email))
        try:
            user_email = User.objects.filter(Q(state_id=ACTIVE)|Q(state_id=INACTIVE),email=email).last()
            if email == user_email.email:
                data['exists'] = '1'
        except:
            user_email = None
        if email == '':
            data['empty'] = '1'

        if user_email == None:
            data['exists'] = '0'    
        
        if match == "None":
            data['valid'] = '0'
        else:
            data['valid'] = '1'
        return JsonResponse(data)

"""
User Name Validation
"""
def UsernameValidation(request):
	if request.is_ajax():
		data ={"exists":None}
		username = request.GET.get("username_id")
		user_username = User.objects.filter(username=username)
		if user_username:
			data['exists'] = '1'
		else:
			data['exists'] = '0'
		return JsonResponse(data)

"""
RVT Username Validation
"""
def RvtUsernameValidation(request):
	if request.is_ajax():
		data ={"exists":None}
		username = request.GET.get("rvtusername_id")
		user_username = User.objects.filter(username=username)
		if user_username:
			data['exists'] = '1'
		else:
			data['exists'] = '0'
		return JsonResponse(data)


"""
Admin login
"""
class AdminLoginView(TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect('accounts:web_login')


"""
logout view
"""       
class LogOutView(View):
    def get(self,request,*args,**kwargs):
        try:
            user=User.objects.get(id=request.user.id)
            logout(request)
            if  user.is_verified ==VERIFIED or user.applied_for==3:
                user.role_id=RVT_LVT
                user.save()
        except:
            return render(request,"frontend/index.html")
        return redirect('accounts:web_login')

"""
singup view
"""
class WebSignupView(View):
    def get(self,request,*args,**kwargs):
        API_KEY = env('GOOGLE_API_KEY')
        return render(request,'registration/signup.html' , {'change' :'signup',"API_KEY":API_KEY})
    
    def post(self,request,*args,**kwargs):
        if User.objects.filter(Q(state_id=ACTIVE)|Q(state_id=INACTIVE),email=request.POST.get("email")):
            messages.error(request, 'User already exist with same email.')
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        if  (request.POST.get("country")).lower() == "canada":
            default_currency = "cad"
        else:
            default_currency = "usd"
        user = User.objects.create(
            email = request.POST.get("email"),
            first_name = request.POST.get("first_name"),
            last_name = request.POST.get("last_name"),
            password = make_password(request.POST.get("password")),
            username = request.POST.get("email"),
            role_id = USERS,
            address = request.POST.get("address"),
            city = request.POST.get("city"),
            state = request.POST.get("state"),
            country = request.POST.get("country"),
            default_currency = default_currency
        )
        if request.POST.get("latitude"):
            user.latitude = request.POST.get("latitude")
        if request.POST.get("longitude"):
            user.longitude = request.POST.get("longitude")
        user.save()
        try:
            stripe_customer = stripe.Customer.create(
                description = "x User - %s " % user.email,
                email = user.email
            )
            user.customer_id = stripe_customer.id
            user.save()
        except Exception as e:
            pass
        messages.success(request, 'Registration done Successfully. Please check your email to verify your account. Remember to check your Spam / Junk folder.')
        try:
            token = Token.objects.get(user=user)
        except:
            token = Token.objects.create(user=user)
        current_site = get_current_site(request)
        context = {
            'domain':current_site.domain,
            'site_name': current_site.name,
            'protocol': 'https' if USE_HTTPS else 'http',
            'name': user.first_name + ' ' + user.last_name,
            'email':request.POST.get('email'),
            'id':user.id,
            'token':token,
        }
        message = render_to_string('registration/userregistration-confermation-email.html', context)
        mail_subject = 'Registration confirmation'
        to_email = request.POST.get("email")
        email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
        html_email = render_to_string('registration/userregistration-confermation-email.html',context)
        email_message.attach_alternative(html_email, 'text/html')
        email_message.send()
        return redirect('accounts:web_login')


"""
rvt singup view
"""
class RvtSignupView(View):
    def get(self,request,*args,**kwargs):
        API_KEY = env('GOOGLE_API_KEY')
        return render(request,'registration/signup.html' , {'change' :'signup',"API_KEY":API_KEY})
    def post(self,request,*args,**kwargs):
        if User.objects.filter(Q(state_id=ACTIVE)|Q(state_id=INACTIVE),email=request.POST.get("rvt_email")):
            messages.error(request, 'User already exist with same email.')
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        user = User.objects.create(
            email = request.POST.get("rvt_email"),
            first_name = request.POST.get("rvt_first_name"),
            last_name = request.POST.get("rvt_last_name"),
            password = make_password(request.POST.get("rvt_password")),
            year_of_experience = request.POST.get("year_of_experience"),
            registration_no = request.POST.get("registration_no"),
            username = request.POST.get("rvt_email"),
            role_id = USERS,
            applied_for = '3',
            address = request.POST.get("address"),
            city = request.POST.get("city"),
            state = request.POST.get("state"),
            country = request.POST.get("country"),
            expiry_date = request.POST.get("expiry_date")
        )
        if request.POST.get("latitude"):
            user.latitude = request.POST.get("latitude")
        if request.POST.get("longitude"):
            user.longitude = request.POST.get("longitude")                       
        if request.FILES.get("resume"):
            user.resume = request.FILES.get("resume")
        try:
            stripe_customer = stripe.Customer.create(
                description = "x User - %s " % user.email,
                email = user.email
            )
            user.customer_id = stripe_customer.id
            user.save()
        except Exception as e:
            pass
        messages.success(request, 'Registration done Successfully. Please check your email to verify your account. Remember to check your Spam / Junk folder.')
        user.save()
        try:
            token = Token.objects.get(user=user)
        except:
            token = Token.objects.create(user=user)
        current_site = get_current_site(request)
        context = {
            'domain':current_site.domain,
            'site_name': current_site.name,
            'protocol': 'https' if USE_HTTPS else 'http',
            'name': user.first_name + ' ' + user.last_name,
            'id':user.id,
            'token':token,
        }
        message = render_to_string('registration/registration-confermation-email.html', context)
        mail_subject = 'Registration confirmation'
        to_email = request.POST.get("rvt_email")
        email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
        html_email = render_to_string('registration/registration-confermation-email.html',context)
        email_message.attach_alternative(html_email, 'text/html')
        email_message.send()
        return redirect('accounts:web_login')


"""
complete verification
"""
def Completeverification(request):
    token = Token.objects.get(key=request.GET.get('token'))
    user = User.objects.get(id=token.user_id)
    if user:
        user.is_verify_mail = True
        user.save()
        messages.success(request, 'Account verified successfully!')
    return render(request, 'registration/login.html')


"""
Login view
"""
class LoginView(View):
    def get(self,request,*args,**kwargs):
        next_page = request.GET.get('next_page')
        return render(request,'registration/login.html' , {'change' : "login", "next_page":next_page})
    
    def post(self,request,*args,**kwargs):
        if request.method == 'POST':
            agent=request.META['HTTP_USER_AGENT']
            IP=request.META.get("REMOTE_ADDR")
            next_page = request.POST.get('next_page')
            des= request.path
            urls="https://"+IP+des
            email = request.POST.get("email")
            password = request.POST.get("password")
            if not email:
                feed = LoginHistory.objects.create(User_Ip=IP,User_agent=agent,State="Failed",Code=urls)
                return render(request, 'registration/login.html',{"email":email})
            if not password:
                feed = LoginHistory.objects.create(User_Ip=IP,User_agent=agent,State="Failed",Code=urls,user=email)
                return render(request, 'registration/login.html',{"email":email})
            if request.POST.get('remember_me')=='on':    
                request.session.set_expiry(7600) 
            user = authenticate(username=email, password=password)

            if not user:
                feed = LoginHistory.objects.create(User_Ip=IP,User_agent=agent,State="Failed",Code=urls,user=email)
                if User.objects.filter(email=email,state_id=DELETED):
                    messages.add_message(request, messages.INFO, 'Your account has been deleted. Please create a new one.') 
                else:    
                    messages.add_message(request, messages.INFO, 'Incorrect email or password.')     
                return render(request, 'registration/login.html',{"email":email ,"password" : request.POST.get("password"), "bar":'danger','change' : "login"})
            else:
                if not user.customer_id or user.customer_id==None:
                    try:
                        stripe_customer = stripe.Customer.create(
                            description = "x User - %s " % user.email,
                            email = user.email
                        )
                        user.customer_id = stripe_customer.id
                        user.save()
                    except Exception as e:
                        pass
            if user.is_superuser and user.role_id == ADMIN :
                login(request, user)
                feed = LoginHistory.objects.create(User_Ip=IP,User_agent=agent,State="success",Code=urls,user=email)
                user.session_id = request.session.session_key
                user.save()
                return redirect('admin:index')
            elif user.is_superuser and user.role_id == SUB_ADMIN and user.is_verify_mail:
                login(request, user)
                feed = LoginHistory.objects.create(User_Ip=IP,User_agent=agent,State="success",Code=urls,user=email)
                user.session_id = request.session.session_key
                user.save()
                return redirect('admin:index')
            elif user.state_id == INACTIVE:
                messages.add_message(request, messages.INFO, 'Your account has been deactivated. Please contact admin (admin@toxsl.in) to activate your account.')
                return render(request, 'registration/login.html',{"email":email ,"password" : request.POST.get("password"), "bar":'danger','change' : "login"})
            elif user.state_id == DELETED:
                messages.add_message(request, messages.INFO, 'Your account has been deleted. Please create a new one.')
                return render(request, 'registration/login.html',{"email":email ,"password" : request.POST.get("password"), "bar":'danger','change' : "login"})
            elif user.role_id == RVT_LVT and user.is_verified == UNVERIFIED:
                messages.add_message(request, messages.INFO, 'Your Application is not accepted by admin , please wait for approval')     
                return render(request, 'registration/login.html',{"email":email ,"password" : request.POST.get("password"), "bar":'danger','change' : "login"})
            elif user.role_id == USERS and user.is_verify_mail:
                login(request, user)
                feed = LoginHistory.objects.create(User_Ip=IP,User_agent=agent,State="success",Code=urls,user=email)
                user.session_id = request.session.session_key
                user.status = True
                user.save()

                if next_page and next_page != "None":
                    return redirect(next_page)
                messages.add_message(request, messages.INFO, 'Your Successfully Logged In to User Dashboard')
                return redirect('enduser:user_dashboard')
            elif user.role_id == RVT_LVT and user.is_verified == DECLINED:
                messages.add_message(request, messages.INFO, 'Your Application has been declined by admin')     
                return render(request, 'registration/login.html',{"email":email ,"password" : request.POST.get("password"), "bar":'danger','change' : "login"})
            elif user.role_id == RVT_LVT and user.is_verified == VERIFIED and user.is_verify_mail: 
                login(request, user)
                feed = LoginHistory.objects.create(User_Ip=IP,User_agent=agent,State="success",Code=urls,user=email)
                user.session_id = request.session.session_key
                user.status = True
                user.save()
                
                if next_page and next_page != "None":
                    return redirect(next_page)
                messages.add_message(request, messages.INFO, 'Your Successfully Logged In to RVT Dashboard')
                return redirect('rvt_lvt:rvt_dashboard') 
            elif not user.is_verify_mail:
                messages.add_message(request, messages.INFO, 'Email has been sent to you. Please verify your account.') 
                return render(request, 'registration/login.html',{"email":email ,"password" : request.POST.get("password"), "bar":'danger','change' : "login"})    
            login(request, user)
            user.session_id = request.session.session_key
            user.save()
            feed = LoginHistory.objects.create(User_Ip=IP,User_agent=agent,State="success",Code=urls,user=email)
            return redirect('frontend:index')



"""
Forgot Password view
"""
class ForgotPassword(View):
    def get(self,request,*args,**kwargs):
        return render(request,'registration/forgot-password.html')

    def post(self,request,*args,**kwargs):
        if not request.POST.get('email'):
            messages.error(request,'please enter email')
            return render(request,'registration/forgot-password.html')
        try:
            user=User.objects.get(email=request.POST.get('email'))
        except:
            messages.error(request,'User not found')
            return render(request,'registration/forgot-password.html')
        otps=""
        for i in range(6):
            otps+=str(r.randint(1,9))
        user.otp=otps
        user.verify_otp=0
        user.save()
        msg= "Your OTP to reset password is : " + otps + "  ignore, if not done by you "
        messages.success(request, 'OTP send to mail')
        return render(request, 'registration/verification.html', { 'id':user.id ,"message":msg })


def OTPVerfication(request):
    if request.method=='POST':
        id=request.POST.get('id')
        user=User.objects.get(id=id)
        otp=request.POST.get('otp')
        if user.otp == otp and user.otp_verify == 0:
            user.otp=" "
            user.otp_verify=1
            user.save()
            return render(request, 'registration/reset-password.html',{'id':id})
        else:
            messages.error(request,'Invalid Otp')
            return render(request, 'registration/otp-verfication.html',{'id':id})
    return render(request, 'registration/otp-verfication.html')


"""
Reset Password
"""

def ResetPassword(request,token):
    if request.method == 'POST':
        try:
            new_password = request.POST.get("new_password1")
            token = Token.objects.get(key=token)
            user = User.objects.get(id=token.user_id)
            user.set_password(new_password)
            user.save()
            token.delete()
            messages.success(request,'Password reset successfully')
            return redirect('accounts:web_login')
        except:
            messages.success(request,'Your password is already reset, if you want to reset again please go to forgot password. ')
            return redirect('accounts:web_login')
    return render(request,'registration/password_reset_confirm.html',{"token":token})


"""
Delete User
"""
@login_required
def DeleteUser(request):
    if request.GET.get('user_id'):
        user = User.objects.get(id=request.GET.get('user_id'))
    else:
        user=User.objects.get(id=request.user.id)
    if user:
        user.username = user.username + 'DEL-'+str(random.random()) if user.username else ""
        user.state_id = DELETED
        user.status = False
        user.save()
        Token.objects.filter(user=user).delete()
        Session.objects.filter(session_key = user.session_id).delete()
        messages.success(request, 'Account deleted successfully')
        if request.GET.get('user_id'):
            return redirect(reverse('superuser:edit_user_info',) + '?user='+str(user.id))
        else:
            return redirect('accounts:web_login')


"""
View User
"""
@login_required
def ViewUser(request):
    user=User.objects.get(id=request.GET.get('id'))
    return render(request, 'admin/profile.html', {'user':user})

"""
Edit User
"""
class EditUser(View):
    @method_decorator(login_required)
    def get(self,request,*args,**kwargs):
        user=User.objects.get(id=request.GET.get("id"))
        return render(request, 'admin/users/edit-user.html',{"user":user})

    def post(self,request,*args,**kwargs):
        try:
            user=User.objects.get(id=request.GET.get("id"))
            if request.POST.get("username"):
                username=request.POST.get("username")
                if User.objects.filter(username=username).exclude(id=user.id):
                    messages.error(request, 'Other User already exist with same username.')
                    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
                user.username = username

            if request.POST.get("address"):
                user.address = request.POST.get("address")

            if request.FILES.get("profile_pic"):
                ext = os.path.splitext(request.FILES.get("profile_pic").name)[1]
                valid_extensions = ['.jpg', '.png', '.JPEG', '.jpeg']
                if not ext.lower() in valid_extensions:
                    messages.error(request, 'Unsupported FIle Format.')
                    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
                user.profile_pic= request.FILES.get("profile_pic")
            
            user.save()
            messages.success(request, 'User Profile Updated successfully')
        except Exception as e:
            db_logger.exception(e)
        return redirect('frontend:index')


"""
AllUser
"""
@login_required
def Allusers(request):
    users=User.objects.filter(role_id = USER).order_by("-id")
    return render(request,'admin/users/users.html', {"users":users} )


"""
AllUser
"""
@login_required
def RvtLvtUsers(request):
    user=User.objects.filter(role_id = RVT_LVT).order_by("-id")
    user_role = UserRole.objects.filter(role_id = RVT_LVT).order_by("-id")
    new_users = zip(user,user_role)
    return render(request,'admin/users/rvt-lvt-user.html', {"users":new_users} )


"""
Accept RVT Request
"""
@login_required
def Accept_request(request):
    user = User.objects.get(id=request.GET.get("id"))
 
    if  user:
        user.job_status = ACCEPT    
        user.save()
        messages.add_message(request, messages.INFO, 'User Verified Successfully!')
        return redirect("accounts:rvt_lvt_user")
    elif user:
        user.job_status = REJECT
        user.save()
        messages.add_message(request, messages.INFO, 'User rejected Successfully!')
        return redirect("accounts:rvt_lvt_user")
   
"""
Reject RVT Request
"""
@login_required
def Reject_request(request):
    user = User.objects.get(id=request.GET.get("id"))
 
    if  user:
        user.job_status = REJECT    
        user.save()
        messages.add_message(request, messages.INFO, 'User rejected !')
        return redirect("accounts:rvt_lvt_user")


'''
Profile View
'''
@login_required
def ViewUser(request,id):
    try:
        user=User.objects.get(id=id)
    except Exception as e:
        user = None
        db_logger.exception(e)
    return render(request, 'admin/profile.html', {'user':user})


'''
Edit User
'''
class EditUser(View):
    @method_decorator(login_required)
    def get(self,request,*args,**kwargs):
        user=User.objects.get(id=request.GET.get("id"))
        return render(request, 'admin/users/edit-user.html',{"user":user})

    def post(self,request,*args,**kwargs):
        user=User.objects.get(id=request.GET.get("id"))
        if request.POST.get("username"):
            username=request.POST.get("username")
            if User.objects.filter(username=username).exclude(id=user.id):
                messages.error(request, 'Other User already exist with same username.')
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            user.username = username

        if request.POST.get("address"):
            user.address = request.POST.get("address")

        if request.FILES.get("profile_pic"):
            ext = os.path.splitext(request.FILES.get("profile_pic").name)[1]
            valid_extensions = ['.jpg', '.png', '.JPEG', '.jpeg']
            if not ext.lower() in valid_extensions:
                messages.error(request, 'Unsupported FIle Format.')
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            user.profile_pic= request.FILES.get("profile_pic")
        user.save()
        messages.success(request, 'User Profile Updated successfully')
        return redirect('accounts:View_User', id=user.id)





"""
Change State of User
"""
@login_required
def ChangeStatusDelete(request):
    try:
        user = User.objects.get(id=request.GET.get("id"))
        if user:
            user.state_id = 3
            user.is_active = False
            user.save()

    except Exception as e:
        db_logger.exception(e)
    return render(request, 'admin/profile.html' , {"user":user})


"""
User Status Active
"""
@login_required
def ChangeStatusActive(request):
    try:
        user = User.objects.get(id=request.GET.get("id"))
        if user:
            user.state_id = 1
            user.is_active = True
            user.save()

    except Exception as e:
        db_logger.exception(e)
    return render(request, 'admin/profile.html' , {"user":user})

"""
User Status Inactive
"""
@login_required
def ChangeStatusInactive(request):
    try:
        user = User.objects.get(id=request.GET.get("id"))
        if user:
            user.state_id = 2
            user.is_active = False
            user.save()

    except Exception as e:
        db_logger.exception(e)
    return render(request, 'admin/profile.html' , {"user":user})



"""
change password
"""
class PasswordChange(View):
    @method_decorator(login_required)
    def get(self,request,*args,**kwargs):
        return render(request,'admin/change-password.html')
    def post(self,request,*args,**kwargs):
        user=User.objects.get(id=request.user.id)
        user.set_password(request.POST.get("new_password"))
        user.save()
        messages.add_message(request, messages.INFO, 'Password changed successfully')
        return redirect('accounts:web_login')


"""
Download Resume
"""
def download(request,id):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path= os.path.join(BASE_DIR)
    user = User.objects.get(id=id)
    file_name = user.resume
    file_path = f"media/{file_name}"
    with open(file_path,'rb') as f:
        response = HttpResponse(f.read(), content_type='application')
        response['Content-Disposition'] = 'inline; filename=' + str(file_name)
    return User.Downloadfile(response,file_name)


"""
Transaction History
"""   
@login_required 
def TransactionHistory(request):
    transactions = Transactions.objects.all().order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 10)
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    return render(request,'admin/transaction-history.html',{"title":"Transaction History", "nbar" : "transaction_history","transactions":transactions})



"""
View Transactions
"""
@login_required 
def View_transactions(request,id):
    transactions = Transactions.objects.filter(id=id)
    return render(request,"admin/view-transaction.html",{ "nbar" : "transaction_history","transaction":transactions,"title":"Transaction Information"})




"""
Search Transactions
"""
def Search_Transactions(request):
    if request.method == "GET":
        if request.GET.get('reset')=='reset':
            return redirect("accounts:transaction_history")
        try:
            search=request.GET.get('search')
            d = {'transaction_id':request.GET.get("search"),"created_on" :request.GET.get("date_filter")}
            syn = "SELECT * FROM tbl_transaction WHERE "
            k =[]
            query = ""
            for i in d.keys():
                if d[i]:
                    k.append('%'+d[i]+"%")
                    query += i + " LIKE %s and "
                if i == 'status':    
                    if d[i]:
                        k.append(d[i])
                        query += i + " = %s and " 
                else:
                    pass
            query = query.rstrip(" and")
            syn += query
            searclist=[]
            for user in Transactions.objects.raw(syn,k):
                searclist.append(user.id)
            transactions = Transactions.objects.filter(id__in = searclist)
            if transactions:
                return render(request,"admin/transaction-history.html",{"title":"Transaction History", "nbar" : "transaction_history","search":search,"transactions":transactions,"transaction_id":request.GET.get("search"),"created_on" :request.GET.get("date_filter")})
            else:
                messages.add_message(request, messages.INFO, 'No Data Found')
                return redirect("accounts:transaction_history")
        except:
            messages.add_message(request, messages.INFO, 'Please Enter Something To Search')
            return redirect('accounts:transaction_history')



"""
Help Request
"""  
@login_required
def Helprequest(request):
    helps = HelpRequest.objects.all()
    user = User.objects.filter(role_id = SUB_ADMIN)
    return render(request,'admin/help-request.html',{"title":"Help Request", "nbar" : "help_request","helps":helps,"user":user})


"""
Subscription
"""
@login_required
def UserSubscription(request):
    user  = User.objects.get(email = request.POST.get("news_email"))
    if user:
        user.is_subscribe = True
        user.save()
    return redirect('frontend:career')


@login_required
def SearchByName(request):
    if request.method == 'GET':
        search = request.GET.get("search_by_name")
        if not search:
            messages.error(request, 'Please enter somethings to search')
            return redirect('accounts:help_request')
        elif request.GET.get("reset")=='reset':
            messages.error(request, 'Please enter somethings to search')
            return redirect('accounts:help_request')
        if search:
            helps = HelpRequest.objects.filter(created_by__first_name__icontains = search)
            user = User.objects.all().exclude(role_id = RVT_LVT)
            return render(request, 'admin/help-request.html',{'nbar':'help_request',"title":"Help Request","search":search,"helps":helps,"user":user})


"""
Custome decorator
"""
def user_is_entry_author(function):
    def wrap(request, *args, **kwargs):
        try:
            entry = User.objects.get(id=request.user.id)
            if entry.role_id== request.user.role_id:
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        except:
            return redirect("accounts:web_login")
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


"""
News Letter
"""
def NewsletterSubscriptions(request):
    if request.method == 'GET':
        subscribed_user=NewsletterSubscription.objects.all().order_by('-created_on')
        return render(request,'admin/newsletter-subscription.html',{"title":"Newsletter Subscriptions", "nbar" : "newsletter_subscription","subscribed_user":subscribed_user})

    if request.method == 'POST':
        if request.POST.get('subscription_email'):
            selected_email = request.POST.get('subscription_email')
        elif request.POST.get('subscription_email_career'):
            selected_email = request.POST.get('subscription_email_career')
        elif request.POST.get('subscription_email_blog'):
            selected_email = request.POST.get('subscription_email_blog')
        elif request.POST.get('subscription_email_contact'):
            selected_email = request.POST.get('subscription_email_contact')

        if NewsletterSubscription.objects.filter(email = selected_email):
            messages.add_message(request, messages.INFO, 'You have already subscribed for the Newsletter.')
        else:
            NewsletterSubscription.objects.create(email = selected_email)
            messages.add_message(request, messages.INFO, 'You have subscribed for the newsletter successfully!')

        if request.POST.get('subscription_email'):
            return redirect('frontend:about')
        elif request.POST.get('subscription_email_career'):
            return redirect('frontend:career')
        elif request.POST.get('subscription_email_blog'):
            return redirect('blog:blog')
        elif request.POST.get('subscription_email_contact'):
            return redirect('frontend:contact')
        else:
            return redirect('frontend:index')


"""
Search Newsletter Subscription
"""
def Search_Newsletter_subscription(request):
    search=request.POST.get('search')
    if not search:
        messages.add_message(request,messages.INFO,"Please Enter Something To Search")
        return redirect('accounts:newsletter_subscription')
    if search:
        subscribed_user=NewsletterSubscription.objects.filter(email__icontains=search)
        return render(request,'admin/newsletter-subscription.html',{"search":search,"subscribed_user":subscribed_user})


"""
Delete Subscription
"""
def DeleteSubscription(request):
    NewsletterSubscription.objects.filter(id=request.GET.get('id')).delete()
    return redirect('accounts:newsletter_subscription')


"""
Forgot Password
"""
def Forgot_password_mail(request):
    if request.method=='POST':
        email = request.POST.get("email")
        if not User.objects.filter(email=email).exists():
            messages.error(request,'User does not exist ')
            return redirect('accounts:forgot_password_mail')
        else:
            user = User.objects.get(email=email,state_id=ACTIVE)
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)
            current_site = get_current_site(request)
            context = {
                'domain':current_site.domain,
                'site_name': current_site.name,
                'protocol': 'https' if USE_HTTPS else 'http',
                'token':token.key,
            }
            message = render_to_string('registration/password_confirmation_email.html', context)
            mail_subject = 'Reset Password'
            to_email = request.POST.get('email')
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            html_email = render_to_string('registration/password_confirmation_email.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
            user.email_sent_on = datetime.now()
            user.save()
            messages.success(request,'A link has been sent on your email to reset your password.')
            return redirect('accounts:web_login') 
    return render(request,'registration/forgot-password.html') 


def Reset_password(request,token):
    if request.method =='GET':
        try:
            token = Token.objects.get(key=token)
            user = User.objects.get(id=token.user_id)
            sent_time = user.email_sent_on
            expire_time = sent_time + timedelta(minutes=10)
            if datetime.now() < expire_time:
                return render(request,'registration/password_reset_confirm.html',{"token":token})
            else:
                messages.success(request,'Reset password link is expired')
                return redirect('accounts:web_login')
        except:
            messages.success(request,'Reset password link is expired')
            return redirect('accounts:web_login')
    if request.method == 'POST':
        try:
            token = Token.objects.get(key=token)
            user = User.objects.get(id=token.user_id)
            new_password = request.POST.get("new_password1")
            user = User.objects.get(id=token.user_id)
            user.set_password(new_password)
            user.is_verify_mail = True
            user.save()
            token.delete()
            messages.success(request,'Password reset successfully')
            return redirect('accounts:web_login')
        except:
            messages.success(request,'Reset password link is expired.')
            return redirect('accounts:web_login')


"""
Search Newsletter Subscription
"""
def Search_Newsletter_subscription(request):
    search=request.POST.get('search')
    if not search:
        messages.add_message(request,messages.INFO,"Please Enter Something To Search")
        return redirect('accounts:newsletter_subscription')
    else:
        subscribed_user=NewsletterSubscription.objects.filter(email__icontains=search)
        return render(request,'admin/newsletter-subscription.html',{"title":"Newsletter Subscriptions", "nbar" : "newsletter_subscription","search":search,"subscribed_user":subscribed_user})


def password_confirmation(request):
    return render(request,"registration/password_confirmation_email.html")

def activate_account(request):
    return render(request,"registration/activate_account_email.html")


"""
add bank
"""
def AddBank(request):
    response_code = request.GET.get("code")
    try:
        user = User.objects.get(id = request.user.id)
        if response_code:
            response = stripe.OAuth.token(grant_type='authorization_code',code=response_code)
            connected_account_id = response['stripe_user_id']
            user.bank_account_id = connected_account_id
            user.save()
            messages.add_message(request, messages.INFO, 'Stripe Account Added Successfully')
            if user.role_id == 3:
                return redirect(reverse('rvt_lvt:rvt_profile',) + '?thirdTab='+'True')
            else:
                return redirect(reverse('enduser:user_profile',) + '?thirdTab='+'True')
        else:
            messages.add_message(request, messages.INFO, 'Something Went Wrong!, Please Try Again')
            if user.role_id == 3:
                return redirect(reverse('rvt_lvt:rvt_profile',) + '?thirdTab='+'True')
            else:
                return redirect(reverse('enduser:user_profile',) + '?thirdTab='+'True')
    except:
        return redirect(reverse('accounts:bank_message',) + '?success=Bank_Added&code='+response_code)


"""
Delete bank
"""
def DeleteBank(request,web="1"):
    account_id = request.GET.get("bank_id")
    stripe_account = stripe.Account.delete(account_id)
    messages.add_message(request, messages.INFO, 'Your Bank Deleted Successfully')
    if request.user.role_id == 3:
        return redirect(reverse('rvt_lvt:rvt_profile',) + '?thirdTab='+'True')
    else:
        return redirect(reverse('enduser:user_profile',) + '?thirdTab='+'True')


def BankMessage(request):
    return HttpResponse("Bank Added")

    
"""
Assign Help Request
"""
def AssignHelpRequest(request):
    try:
        user=User.objects.get(id=request.GET.get('user_id'))
    except:
        messages.add_message(request, messages.INFO, 'User id not found')
    helprequest = HelpRequest.objects.get(id=request.GET.get('help_id'))
    helprequest.assign_to_id = user.id
    helprequest.save()
    messages.add_message(request, messages.INFO, 'Help request assigned successfully')
    return redirect('accounts:help_request')


"""
Delte Help Request
"""
def DleteHelpRequest(request):
    HelpRequest.objects.filter(id=request.GET.get('id')).delete()
    messages.add_message(request, messages.INFO, 'Help Request Deleted Successfully')
    return redirect('accounts:help_request')


"""
Edit Help Request
"""
def EditHelpRequest(request):
    user=User.objects.get(id=request.GET.get('user_id'))
    helprequest=HelpRequest.objects.get(id=request.GET.get('edit_help_id'))
    helprequest.assign_to_id=user.id
    helprequest.save()
    messages.add_message(request, messages.INFO, 'Help Request updated Successfully')
    return redirect('accounts:help_request')