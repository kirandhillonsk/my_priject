x
from urllib.request import urlopen
import stripe
import environ
import datetime
from django.db.models.query_utils import Q
from django.contrib.auth import login,logout
from rvt_lvt.models import Transactions
from .serializer import *
from rating.models import *
from accounts.models import *
from rest_framework_jwt.views import *
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate , logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from rest_framework import status , permissions
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from page.models import Page
from page.serializer import PageSerializer
import random
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives

env = environ.Env()
environ.Env.read_env()
stripe.api_key = env('STRIPE_KEY')


class GenerateCalenderLink(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        user = User.objects.get(id=request.user.id)
        login(request, user, backend='accounts.backend.EmailLoginBackend')
        if user.role_id == RVT_LVT:
            link = request.build_absolute_uri('/rvt/my-appointments/?id='+str(user.id))
        else:
            link = request.build_absolute_uri('/enduser/user-appointments/?id='+str(user.id))
        return Response({"link":link,"status": status.HTTP_200_OK})


"""
User registration
""" 
class NormalSignUpViews(APIView):
    def post(self,request,*args,**kwargs):
        if not request.data.get("first_name"):
            return Response({"message":"Please enter First name.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get("last_name"):
            return Response({"message":"Please enter Last name.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get("email"):
            return Response({"message":"Please enter email id.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get("password"):
            return Response({"message":"Please enter the password.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
        if request.data.get("registration_no"):
            if User.objects.filter(registration_no=request.data.get("registration_no")):
                return Response({"message":"There is already a registered user with this registration number",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST}) 
        if User.objects.filter(email=request.data.get("email"),state_id = ACTIVE):
            return Response({"message":"User Already Exists",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get("confirm_password"):
            return Response({"message": "Please confirm your password","url":request.path,"status":status.HTTP_400_BAD_REQUEST}) 
        if request.data.get("password") != request.data.get("confirm_password"):
            return Response({"message":"Password did not match. Please try again! ","url":request.path,"status":status.HTTP_400_BAD_REQUEST}) 
        
        user = User.objects.create(
            email=request.data.get("email"),
            role_id=request.data.get("role_id"),
            first_name = request.data.get("first_name"),
            last_name = request.data.get("last_name"),
        )
        user.password = make_password(request.data.get("password")) 
        if request.data.get("year_of_experience"):
            user.year_of_experience = request.data.get("year_of_experience")
        if request.data.get("registration_no"):
            user.registration_no = request.data.get("registration_no")
        if request.data.get("expiry_date"):
            user.expiry_date = request.data.get("expiry_date")
        if request.FILES.get("resume"):
            user.resume = request.FILES.get("resume")
        if request.data.get("applied_for"):
            user.applied_for = request.data.get("applied_for")
        if request.data.get("latitude"):
            user.latitude = request.data.get("latitude")
        if request.data.get("longitude"):
            user.longitude = request.data.get("longitude")  
        if request.data.get("address"):
            user.address = request.data.get("address")
        if request.data.get("city"):
            user.city = request.data.get("city")
        if request.data.get("state"):
            user.state = request.data.get("state")
        if request.data.get("country"):
            user.country = request.data.get("country")
        
        if (request.data.get("country")).lower() == "canada":
            user.default_currency = "cad"
        else:
            user.default_currency = "usd"
        try:
            stripe_customer = stripe.Customer.create(
                description = "x User - %s " % user.email,
                email = user.email
            )
            user.customer_id = stripe_customer.id
            user.save()
        except Exception as e:
            pass
        user.save()
        try:
            token = Token.objects.get(user = user)
        except:
            token = Token.objects.create(user = user) 
        if not request.data.get("applied_for"):
            current_site = get_current_site(request)
            context = {
                'domain':current_site.domain,
                'site_name': current_site.name,
                'protocol': 'https' if USE_HTTPS else 'http',
                'name': user.first_name + ' ' + user.last_name,
                'email':user.email,
                'id':user.id,
                'token':token,
            }         
            message = render_to_string('registration/userregistration-confermation-email.html', context)
            mail_subject = 'Registration confirmation'
            to_email = user.email
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            html_email = render_to_string('registration/userregistration-confermation-email.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
        else:
            current_site = get_current_site(request)
            context = {
                'domain':current_site.domain,
                'site_name': current_site.name,
                'protocol': 'https' if USE_HTTPS else 'http',
                'name': user.first_name + ' ' + user.last_name,
                'email':user.email,
                'id':user.id,
                'token':token,
            }
            message = render_to_string('registration/registration-confermation-email.html', context)
            mail_subject = 'Registration confirmation'
            to_email = user.email
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            html_email = render_to_string('registration/registration-confermation-email.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
        data = UserSerializer(user,context = {"request":request}).data
        data.update({"token":token.key})  
        return Response({"message":"User Registered Successfully! An Email has been sent to you. Please verify your account.","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
user login
"""
class LoginView(ObtainJSONWebToken):
    serializer_class = LoginSerializer    
    def post(self, request, *args, **kwargs):
        data={}
        if not request.data.get("password",None):
            return Response({"message":"Please enter the password.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get("email",None):
            return Response({"message":"Please enter the email.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})

        user = authenticate(username = request.data.get("email",None), password = request.data.get("password",None))

        if not User.objects.filter(email=request.data.get("email",None)).exclude(Q(role_id=ADMIN)|Q(role_id=SUB_ADMIN)):
            return Response({"message":"You have entered wrong email.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
            
        if not user:
            if User.objects.filter(Q(username=request.data.get("email"))|Q(email=request.data.get("email")), Q(state_id=str(ACTIVE))|Q(state_id=str(INACTIVE))):
                return Response({"message":"You have entered wrong password.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
            else:
                return Response({"message":"Please enter a valid email or password.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})
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

        if not user.is_verify_mail:
            return Response({"message":"Email has been sent to you. Please verify your account.",'url' : request.path, "status":status.HTTP_400_BAD_REQUEST})

        if user.state_id == INACTIVE:
            return Response({"status":status.HTTP_400_BAD_REQUEST,"message":"Your account has been deactivated. Please contact admin to activate your account.",'url':self.request.path}, status=status.HTTP_200_OK)
        elif user.state_id == DELETED:
            return Response({"status":status.HTTP_400_BAD_REQUEST,"message":"Your account has been deleted. Please create a new one.",'url' : self.request.path}, status=status.HTTP_200_OK)
        elif user.state_id == ACTIVE:
            try:
                token = Token.objects.get(user = user)
                token.delete()
                token = Token.objects.create(user = user)
            except:
                token = Token.objects.create(user = user)        
            try:
                device = Device.objects.get(created_by = user)
            except Device.DoesNotExist:
                device = Device.objects.create(created_by = user,device_type = 1)
            device.device_type = request.data['device_type']
            device.device_name = request.data['device_name']
            device.device_token = request.data['device_token']
            device.save()
            data = UserSerializer(user,context = {"request":request}).data
            data.update({"token":token.key})       
            return Response({"data":data,"token":token.key,"status":status.HTTP_200_OK,"message":"Login Successfully",'url' : self.request.path}, status=status.HTTP_200_OK)


"""
Social Login
"""
class SocialSignInView(APIView):
    serializer_class = UserSerializer

    def post(self,request,*args,**kwargs):
        all_users = User.objects.filter(userId__isnull=False,role_id=USERS)
        users_list = [i.userId for i in all_users]
        if request.data.get('userId') in users_list:
            try:
                user = User.objects.filter(userId=request.data.get('userId')).last()
                if user.status == INACTIVE:
                    return Response({
                        "message":"Your account has been deactivated by the admin!",
                        "status":status.HTTP_400_BAD_REQUEST, 
                        'url' : self.request.path
                    }, status=status.HTTP_200_OK)
                elif user.status == DELETED:
                    return Response({
                        "message":"Your account has been deleted by the admin!",
                        "status":status.HTTP_400_BAD_REQUEST, 
                        'url' : self.request.path
                    }, status=status.HTTP_200_OK)
            except:
                return Response({"message":"User Does not exist","url":request.path},status=status.HTTP_400_BAD_REQUEST)
            login(request, user)
            if request.data.get("profile_pic"):
                img_temp = NamedTemporaryFile(delete = True)
                img_temp.write(urlopen(request.data.get("profile_pic")).read())
                img_temp.flush()
                user.profile_pic.save("image_%s" % user.pk, File(img_temp))
            if request.data.get('first_name'):
                user.first_name = request.data.get('first_name')
            if request.data.get('last_name'):
                user.last_name = request.data.get('last_name')
            if request.data.get('first_name') and request.data.get('last_name'):
                user.full_name = request.data.get('first_name') + " " + request.data.get('last_name')
            user.save()
            try:
                token = Token.objects.get(user = user)
                token.delete()
                token = Token.objects.create(user = user)
            except:
                token = Token.objects.create(user = user)    
            try:
                device = Device.objects.get(created_by = user)
            except Device.DoesNotExist:
                device = Device.objects.create(created_by = user)
            device.device_type = request.data['device_type']
            device.device_name = request.data['device_name']
            device.device_token = request.data['device_token']
            device.save()

            data = UserSerializer(user,context={"request":request}).data
            data.update({"token":token.key})
            return Response({
                "message":"Login Successful",
                "data":data,
                "status":status.HTTP_200_OK,
                'url' : self.request.path
            }, status=status.HTTP_200_OK)
        else:
            try:
                user = User.objects.filter(Q(state_id=ACTIVE)|Q(state_id=INACTIVE),email=request.data.get('email')).last()
                message = "Login Successfully"
                user.userId = request.data.get('userId')
                user.social_type = request.data.get('social_type')
            except:
                user = User.objects.create(
                    userId = request.data.get('userId'),
                    email = request.data.get('email'),
                    social_type = request.data.get('social_type'),
                    role_id = USERS
                )
                message = "New Account Created Successfully!"
            if request.data.get('first_name'):
                user.first_name = request.data.get('first_name')
            if request.data.get('last_name'):
                user.last_name = request.data.get('last_name')
            if request.data.get('first_name') and request.data.get('last_name'):
                user.full_name = request.data.get('first_name') + " " + request.data.get('last_name')
            if request.data.get("profile_pic"):
                img_temp = NamedTemporaryFile(delete = True)
                img_temp.write(urlopen(request.data.get("profile_pic")).read())
                img_temp.flush()
                user.profile_pic.save("image_%s" % user.pk, File(img_temp))
            user.save()
            try:
                token = Token.objects.get(user = user)
            except:
                token = Token.objects.create(user = user)     

            try:
                device = Device.objects.get(created_by = user)
            except Device.DoesNotExist:
                device = Device.objects.create(created_by = user)
            device.device_type = request.data['device_type']
            device.device_name = request.data['device_name']
            device.device_token = request.data['device_token']
            device.save()
            data = UserSerializer(user,context={"request":request}).data
            data.update({"token":token.key})
            return Response({
                "message":message,
                "data":data,
                "status":status.HTTP_200_OK, 
                'url' : self.request.path
            }, status=status.HTTP_200_OK)


"""
check Api
"""
class UserCheckView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        user = request.user
        try:
            token = Token.objects.get(user = user)
        except:
            token = Token.objects.create(user = user)
        data = UserSerializer(user,context = {"request":request}).data
        data.update({"token":token.key})
        response = {
            "data":data,
            "status": status.HTTP_200_OK,
            'url' : request.path
        }  
        return Response(response)


"""
Reset Password  
"""
class ResetPassword(APIView):
    def post(self, request, *args, **kwargs):
        if not User.objects.filter(email = request.data.get("email")):
            return Response({"message": "There is no account available with this email","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)  
        else:
            user = User.objects.get(email= request.data.get("email"))

            if user.check_password(request.data.get("current_password")) == False:
                return Response({"message": "Current Password Doesn't match","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK) 

            new_password = request.data.get("new_password", None)
            if not new_password:
                return Response({"message": "Please set new password","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK) 

            confirm_password = request.data.get("confirm_password", None)
            if not confirm_password:
                return Response({"message": "Please confirm your password","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK) 

            if new_password != confirm_password:
                return Response({"message":"Password did not match. Please try again! ","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK) 

            else:
                user.password = make_password(request.data.get("new_password")) 
                user.is_verify_mail = True
                user.save()
                try:
                    user.auth_token.delete()
                    Token.objects.get(user = user).delete()
                except Exception as e:
                    pass
            return Response({"message": "Password updated successfully","url":request.path,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


"""
logout
"""
class LogoutView(APIView): 
    permission_classes = (permissions.IsAuthenticated,) 
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        token=Token.objects.get(user=user).delete()
        logout(request)       
        response = {
            'message':'Successfully logout.',
            'status' : 200,  
            'url' : request.path,
            }
        return Response(response)


"""
Edit profile
"""
class EditProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
        except:
            return Response({"message":"User not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        if  request.data.get("first_name",None):
            user.first_name = request.data.get('first_name')
        if  request.data.get("last_name",None):
            user.last_name = request.data.get('last_name')
        if  request.data.get("email",None):
            user.email = request.data.get('email')
        if  request.data.get("mobile_no",None):
            user.mobile_no = request.data.get('mobile_no')
        if  request.data.get("about_me",None):
            user.about_me = request.data.get('about_me')
        if  request.data.get("profile_pic",None):
            user.profile_pic = request.FILES.get('profile_pic')
        if  request.data.get("year_of_experience",None):
            user.year_of_experience = request.data.get('year_of_experience')
        if  request.data.get("registration_no",None):
            user.registration_no = request.data.get('registration_no')
          
        if request.data.get("expiry_date"):
            user.expiry_date = request.data.get("expiry_date")
        
        if request.data.get("latitude"):
            user.latitude = request.data.get("latitude")
        
        if request.data.get("longitude"):
            user.longitude = request.data.get("longitude")  
         
        if request.data.get("address"):
            user.address = request.data.get("address")
        
        if request.data.get("city"):
            user.city = request.data.get("city")
        
        if request.data.get("state"):
            user.state = request.data.get("state")
        
        if request.data.get("country"):
            user.country = request.data.get("country")
        user.save()
        return Response({"data":UserSerializer(user, many=False, context={"request":request}).data,"messagae":"Profile updated successfully","url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
User Profile
"""
class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id = request.user.id)
            return Response({"data":UserSerializer(user, many=False, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)
        except:
            return Response({"message": "User not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST}) 


"""
Forget Password  
"""
class ForgetPassword(APIView):
    def post(self, request, *args, **kwargs):
        if not User.objects.filter(email = request.data.get("email")):
            return Response({"message": "Email id not exist in record","url":request.path,"status":status.HTTP_400_BAD_REQUEST})  
        else:
            user = User.objects.get(email= request.data.get("email")) 
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
            mail_subject = 'Reset Password '
            to_email = request.data.get('email')
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            html_email = render_to_string('registration/password_confirmation_email.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
            user.email_sent_on = datetime.now()
            user.save()
            return Response({"message": "A link has been sent on your email to reset your password.","url":request.path,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


"""
Add Card
"""
class AddCardView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if not request.data.get('card_number'):
            return Response({"message": "Please enter the card number","status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('name'):
            return Response({"message": "Please enter the card holder name","status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('cvc'):
            return Response({"message": "Please enter the card cvv","status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('exp_year'):
            return Response({"message": "Please enter the card expiry year","status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('exp_month'):
            return Response({"message": "Please enter the card expiry month","status":status.HTTP_400_BAD_REQUEST})
        try:
            token = stripe.Token.create(
                card={
                    "number": request.data.get('card_number'),
                    "exp_month": int(request.data.get('exp_month')),
                    "exp_year": int(request.data.get('exp_year')),
                    "cvc": request.data.get('cvc'),
                    "name": request.data.get('name')
                },
            )
            stripe.Customer.create_source(request.user.customer_id,source=token.id)
            return Response({"message":"Card added successfully!","status":status.HTTP_200_OK})
        except Exception as e:
            try:
                message = str(e).split(': ')[1]
            except:
                message = str(e)
            return Response({"message":message,"status":status.HTTP_400_BAD_REQUEST}) 


"""
User Cards List
"""
class UserCardsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        cards_data = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
        customer = stripe.Customer.retrieve(request.user.customer_id)
        data = []
        for card in cards_data.data:
            data.append({
                "id":card.id,
                "card_type":card.brand,
                "country":card.country,
                "customer":card.customer,
                "cvc_check":card.cvc_check,
                "exp_month":card.exp_month,
                "exp_year":card.exp_year,
                "ac_no":card.last4,
                "card_holder_name":card.name,
                "default": True if customer.default_source == card.id else False,
                "funding":card.funding,
                "image": request.build_absolute_uri("admin-assets/images/visa.png") if card.brand == 'Visa' else request.build_absolute_uri("admin-assets/images/mastercard.png")  
            })
        return Response({"data":data,"url":request.path,"status":status.HTTP_200_OK})


"""
Delete Card
"""
class DeleteCardView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('card_token_id'):
            return Response({"message": "Please enter the card token id","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        try:
            stripe_card = stripe.Customer.delete_source(
                request.user.customer_id,
                request.query_params.get('card_token_id'),
            )
            message = "Card deleted successfully!"
        except Exception as e:
            message = str(e)
            message = message.split(": ")[1]
        return Response({"message":message,"url":request.path,"status":status.HTTP_200_OK})


"""
Set Default Card
"""
class SetDefaultCard(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('card_token_id'):
            return Response({"message": "Please enter the card token id","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        try:
            stripe_user = stripe.Customer.modify(request.user.customer_id,default_source=request.query_params.get('card_token_id'))
            if stripe_user.default_source == request.query_params.get('card_token_id'):
                return Response({"message":"Default card set successfully!","url":request.path,"status":status.HTTP_200_OK}) 
            else:
                return Response({"message":"There is Some issue in your card details","url":request.path,"status":status.HTTP_400_BAD_REQUEST}) 
        except Exception as e:
            message = str(e)
            return Response({"message":message,"url":request.path,"status":status.HTTP_400_BAD_REQUEST}) 


"""
Transactions List
"""
class TransactionsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        transactions = Transactions.objects.filter(created_by=request.user.id)
        if request.query_params.get('start_date') and request.query_params.get('end_date'):
            start_date = datetime.strptime(request.query_params.get('start_date'),'%Y-%m-%d')
            end_date = datetime.strptime(request.query_params.get('end_date'),'%Y-%m-%d')
            transactions = transactions.filter(created_on__date__range=[start_date,end_date])
            
        data = TransactionsSerializer(transactions,many=True,context = {"request":request}).data
        return Response({"data":data,"url":request.path,"status":status.HTTP_200_OK}) 


"""
Transactions Details
"""
class TransactionDetails(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('transaction_id'):
            return Response({"message": "Please enter the transaction id","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        try:
            transaction = Transactions.objects.get(id=request.query_params.get('transaction_id'))
        except:
            return Response({"message": "Transaction does not exist.","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        data = TransactionsSerializer(transaction,context = {"request":request}).data
        return Response({"data":data,"url":request.path,"status":status.HTTP_200_OK}) 


"""
Add Bank Account
"""
class AddBankAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('account_code'):
            return Response({"message": "Please enter the code","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        user = User.objects.get(id=request.user.id)
        try:
            response = stripe.OAuth.token(
                grant_type = 'authorization_code',
                code = request.query_params.get('account_code'),
            )
            connected_account_id = response['stripe_user_id']
            user.bank_account_id = connected_account_id
            user.save()
            return Response({"message":"Stripe details added successfully","url":request.path})
        except Exception as e:
            return Response({"message":str(e),"url":request.path,"status":status.HTTP_400_BAD_REQUEST}) 
            

"""
Get Bank Account
"""
class GetBankAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            stripe_bank_account = stripe.Account.list_external_accounts(request.user.bank_account_id, object="bank_account",limit=1)
            for account_data in stripe_bank_account:
                data = {
                    "id":account_data.id,
                    "account_id":account_data.account,
                    "bank_name":account_data.bank_name,
                    "currency":account_data.currency,
                    "routing_number":account_data.routing_number,
                    "account_holder_name":account_data.account_holder_name,
                    "last4":account_data.last4
                }
            return Response({"data":data,"url":request.path})
        except Exception as e:
            return Response({"data":{},"url":request.path})


"""
Delete Bank Account
"""
class DeleteBankAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('account_id'):
            return Response({"message": "Please enter the account id","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        try:
            stripe_account = stripe.Account.delete(request.query_params.get('account_id'))
            user = User.objects.get(id=request.user.id)
            user.bank_account_id = ""
            user.save()
            return Response({"message":"Stripe Deleted Successfully!","url":request.path})
        except Exception as e:
            return Response({"message":str(e),"url":request.path,"status":status.HTTP_400_BAD_REQUEST}) 


"""
Change User Settings
"""
class ChangeUserSettings(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        if request.query_params.get('is_push'):
            user.is_push = request.query_params.get('is_push')
        if request.query_params.get('is_email'):
            user.is_email = request.query_params.get('is_email')
        if request.query_params.get('is_text'):
            user.is_text = request.query_params.get('is_text')
        if request.query_params.get('is_direct_message'):
            user.is_direct_message = request.query_params.get('is_direct_message')
        if request.query_params.get('is_location_tracking'):
            user.is_location_tracking = request.query_params.get('is_location_tracking')
        user.save()
        return Response({"message":"User settings updated successfully!","data":UserSerializer(user, context={"request":request}).data,"url":request.path})



"""
Deactivate user
"""
class ActiveInactiveUserAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        try:
            user=User.objects.get(id=request.user.id)
        except:
            return Response({"message":"user not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        if str(user.state_id) == str(ACTIVE):
            user.state_id = INACTIVE
            user.status = False
            user.save()
            return Response({"message":"Account deactivated successfully",'url':request.path,"status":status.HTTP_200_OK})
        if str(user.state_id) == str(INACTIVE):     
            user.state_id = ACTIVE
            user.status = True
            user.save()
            return Response({"message":"User activated successfully",'url':request.path,"status":status.HTTP_200_OK})


"""
Pages
"""
class FlatPages(APIView):
    def get(self, request, *args, **kwargs):
        if not request.query_params.get("type_id"):
            return Response({"message":"Please enter the page id ",'url':request.path,"status":status.HTTP_200_OK})
        try:
            page = Page.objects.get(type_id = request.query_params.get("type_id"))
        except:
            page = None
        return Response({"data":PageSerializer(page,context={"request":request}).data,"url":request.path},status=status.HTTP_200_OK)


"""
Take a break
"""
class TakeBreak(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        try:
            user=User.objects.get(id=request.user.id)
        except:
            return Response({"message":"Rvt not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
            
        if user.state_id == ACTIVE:
            user.state_id = INACTIVE
            user.save()
            return Response({"message":"Break applied successfully,No user will able to book new appointment ",'url':request.path,"status":status.HTTP_200_OK})
        if user.state_id == INACTIVE:     
            user.state_id = ACTIVE
            user.save()
            return Response({"message":"Break removed successfully,User's will able to book appointment ",'url':request.path,"status":status.HTTP_200_OK})

"""
Delete Account
"""
class DeleteAccount(APIView):
    def get(self,request,*args,**kwargs):
        user=User.objects.get(id=request.user.id)
        if user:
            user.state_id=DELETED
            Token.objects.filter(user=user).delete
            user.username = user.username + 'DEL-'+str(random.random()) if user.username else 'DEL-'+str(random.random())
            user.save()
            return Response({"message":"Account deleted successfully ",'url':request.path,"status":status.HTTP_200_OK})
        return Response({"message":"User not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})


class UserDetails(APIView):
    def get(self,request,*args,**kwargs):
        user_id=User.objects.get(id=request.query_params.get('user_id'))
        if user_id:
            return Response({"data":UserSerializer(user_id, many=False, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)
        else:
            return Response({"message":"User not found","status":status.HTTP_400_BAD_REQUEST})


