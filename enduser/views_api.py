x
 
import pytz
import stripe
import environ
from django.utils import timezone
from enduser.constants import OTHER
from global_utils import *
from superuser.models import Announcements, Banners, Mileage, Tax
from superuser.serializer import BannerSerializer
from .serializer import *
from enduser.models import *
from accounts.models import *
from rating.models import Rating
from rest_framework.views import APIView 
from api.serializer import UserSerializer
from rest_framework.response import Response 
from rating.serializer import RatingSerializer
from rest_framework import views,status , permissions
from rvt_lvt.models import Applied_by, Appointments, CustomService, Notes, Payouts, RefundTransaction, ServiceAvailability, ServiceCategory, Services, Transactions
from rvt_lvt.serializer import AppointmentSerializer, AvailabilitySerializer, CategorySerializer, CustomServiceSerializer, ServiceSerializer
from django.db.models.query_utils import Q 
from datetime import date
from faq.models import Faq
from faq.serializer import FaqSerializer
from notification.models import Notification
from notification.serializer import NotificationSerializer
from pyfcm import FCMNotification
from datetime import datetime
from datetime import timedelta
env = environ.Env()
environ.Env.read_env()
stripe.api_key = env('STRIPE_KEY')
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


"""
Add Pet API
"""
class AddPet(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if not request.data.get('name'):
            return Response({"message":"Please enter pet name","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not request.data.get('vet_name'):
            return Response({"message":"Please enter vet name","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
       
        pet = Pets.objects.create(
            name = request.data.get('name'),
            description = request.data.get('description'),
            age = request.data.get('age'),
            breed = request.data.get('breed'),
            size = request.data.get('weight'),
            vet_name = request.data.get('vet_name'),
            vet_email = request.data.get('vet_email'),
            vet_profile = request.data.get('profile_pic'),
            created_by_id = request.user.id,
            vet_number = request.data.get('vet_number'),
            vet_adrress = request.data.get('vet_adrress'),
            vaccines = request.data.get('vaccines'),

        )
        if request.data.get('gender'):
            pet.pet_gender = request.data.get('gender')

        image =[]
        for i in range(0,int(request.data.get("image_count",'0'))+1):
            if request.FILES.get("image{}".format(i),None):
                image.append(Images.objects.create(file=request.FILES.get("image{}".format(i)),created_by_id = request.user.id))

        if image:
            for img in image:
                pet.image.add(img)
        pet.save()
        pets = PetType.objects.get(id = request.data.get('pet_type'))
        pet.pet_type_id = pets.id
        pet.save()            
        return Response({"data":PetSerializer(pet, many=False, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Remove/Delete Pet information
"""
class DeletePetInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('pet_id'):
             return Response({"message":"Pet id not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        try:
            pet = Pets.objects.filter(id = request.query_params.get('pet_id'),created_by_id = request.user.id)
        except:
            return Response({"message":"Pet id not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if pet:
            pet.delete()
        
        return Response({"message":"Pet information deleted successfully","url":request.path,"status": status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Edit Pet Information
"""
class EditPetInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):

        if not request.data.get('pet_id'):
             return Response({"message":"Pet id not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        try:
            pet = Pets.objects.get(id = request.data.get('pet_id'), created_by_id = request.user.id)
        except:
            return Response({"message":"pet id not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})

        if  request.data.get("name",None):
            pet.name = request.data.get('name')
        if  request.data.get("description",None):
            pet.description = request.data.get('description')
        if  request.data.get("age",None):
            pet.age = request.data.get('age')
        if  request.data.get("gender",None):
            pet.pet_gender = request.data.get('gender')
        if  request.data.get("breed",None):
            pet.breed = request.data.get('breed')

        if  request.data.get("weight",None):
            pet.size = request.data.get('weight')
        if  request.data.get("vet_name",None):
            pet.vet_name = request.data.get('vet_name')
        if  request.data.get("vet_email",None):
            pet.vet_email = request.data.get('vet_email')
        if  request.data.get("profile_pic",None):
            pet.vet_profile = request.data.get('profile_pic')
        if  request.data.get("vet_number",None):
            pet.vet_number = request.data.get('vet_number')
        if  request.data.get("vet_adrress",None):
            pet.vet_adrress = request.data.get('vet_adrress')
        if  request.data.get("vaccines",None):
            pet.vaccines = request.data.get('vaccines')

        image =[]
        for i in range(0,int(request.data.get("image_count",'0'))+1):
            if request.FILES.get("image{}".format(i),None):
                image.append(Images.objects.create(file=request.FILES.get("image{}".format(i)),created_by_id = request.user.id))
        pet.image.set(image) 
        
        pettype = PetType.objects.get(id=pet.pet_type_id)
        pettype.name = request.POST.get('pet_type')
        pettype.save()
        
        pet.save()
        type = PetType.objects.get(id=request.data.get('pet_type'))            
        pet.pet_type =  type
        pet.save()

        return Response({"data":PetSerializer(pet, many=False, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Pet profile
"""
class PetProfile(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('pet_id'):
            return Response({"message":"Pet id not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        try:
            pet = Pets.objects.get(id = request.query_params.get('pet_id'))
            return Response({"data":PetSerializer(pet, many=False, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)
        except:
            return Response({"message":"pet id not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
            
"""
Pet listing
"""
class Petlisting(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        try:
            pet = Pets.objects.filter(created_by = request.user).order_by('-created_on')
            return Response({"data":PetSerializer(pet, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)
        except:
            return Response({"message":"user id not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})


"""
Pet list by Admin
"""
class PetlistingAdmin(APIView):
    def get(self, request, *args, **kwargs):
        try:
            pet = PetType.objects.all()
            return Response({"data":PettypeSerializer(pet, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)
        except:
            return Response({"message":"pets type not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})


"""
Create Help Request
"""
class HelpRequestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if not request.data.get('title'):
            return Response({"message":"Please fill the title","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not request.data.get('description'):
            return Response({"message":"Please fill the decription","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        help_request = HelpRequest.objects.create(
            title = request.data.get("title"),
            complain = request.data.get("description"),
            created_by_id = request.user.id
        )
        admin = User.objects.filter(is_superuser=True,role_id=ADMIN).first()
        current_site = get_current_site(request)
        context = {
            'domain':current_site.domain,
            'site_name': current_site.name,
            'protocol': 'https' if USE_HTTPS else 'http',
            'help_request':help_request,
            'admin':admin
        }
        message = render_to_string('admin/helprequest_mail.html', context)
        mail_subject = 'New Help Request'
        try:
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [admin.email])
            html_email = render_to_string('admin/helprequest_mail.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
        except:
            pass
        return Response({"message":"Message has been sent successfully","url":request.path,"status": status.HTTP_200_OK},status=status.HTTP_200_OK)



"""
Becone an RVT
"""
class BecomeAnRVT(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if not request.data.get('year_of_experience'):
            return Response({"message":"Please enter your experience","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not request.data.get('registration_no'):
            return Response({"message":"Please enter your registration number","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not request.data.get('resume'):
            return Response({"message":"Please attach the resume","url":request.path,"status": status.HTTP_400_BAD_REQUEST}) 
        if not request.data.get('expiry_date'):
            return Response({"message":"Please enter your license expiry date","url":request.path,"status": status.HTTP_400_BAD_REQUEST}) 
        
        user = request.user 
        if User.objects.filter(id=request.user.id, applied_for=RVT_LVT, is_verified = VERIFIED):
            return Response({"message":"You already have verified RVT profile","url":request.path,"status": status.HTTP_200_OK})

        elif User.objects.filter(id=request.user.id,applied_for=RVT_LVT):
            return Response({"message":"Your request has been submitted successfully.Please wait for the admin approval","url":request.path,"status": status.HTTP_200_OK})
     
        else:
            if request.data.get('year_of_experience'):
                user.year_of_experience = request.data.get("year_of_experience")
            if request.data.get('registration_no'):
                user.registration_no=request.data.get('registration_no')
            if request.FILES.get('resume'):
                user.resume=request.FILES.get('resume')
            if request.data.get("expiry_date"):
                user.expiry_date = request.data.get("expiry_date")
            user.applied_for=request.data.get('applied_for')
            user.save()
            if user.is_push:
                Notification.objects.create(
                    title = "Become an rvt",
                    description = "Your request has been successfully submitted..Please wait for admin approval",
                    created_by =request.user,
                    created_for_id =ADMIN
                )
                push_service = FCMNotification(api_key=env('FCM_KEY'))            
                device = Device.objects.get(created_by_id = request.user.id)
                msg = {
                    "title":"Become an rvt",
                    "description":"Your request has been successfully submitted..Please wait for admin approval",
                    "type":BECOME_RVT,
                }
                message_title = msg['title']
                message_body = msg['description']
                result = push_service.notify_single_device(
                            registration_id = device.device_token, 
                            message_title = message_title, 
                            message_body = message_body,
                            data_message={"message_title" :msg['title'],"message_body" : msg['description'],"type" : msg['type']
                        })
            
            return Response({"data":UserSerializer(user, many=False, context={"request":request}).data,"message":"Your request submited successfully..please wait for the admin approval","url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Service category list
"""
class ServiceCategoryList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        category = ServiceCategory.objects.all()
        return Response({"data":CategorySerializer(category, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)

"""
RVT User List CategoryWise
"""
class RVTCategoryWiseList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('category_id'):
            return Response({"message":"category_id not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        user = User.objects.all().values_list('id',flat=True)
        services = Services.objects.filter(category_id = request.query_params.get('category_id'), created_by__in = user)
        return Response({"data":ServiceSerializer(services, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Hire Me View
"""
class HireMeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('user_id'):
            return Response({"message":"User  not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)
        if not request.query_params.get('category'):
            return Response({"message":"Category not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)

        try:
            user_id= User.objects.get(id = request.query_params.get('user_id'))
        except:
            return Response({"message":"User  not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)

        try:
            category = ServiceCategory.objects.get(id = request.query_params.get('category'))
        except:
            return Response({"message":"Category not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)
        hirme_datail = Services.objects.filter(category = category, created_by = user_id)
        return Response({"data":ServiceSerializer(hirme_datail, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)

"""
Appointments list
"""
class UserAppointmentListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        today = date.today()
        appointment_list = Appointments.objects.filter(Q(status=PENDING)|Q(status=SCHEDULED),created_by = request.user).order_by('-date')
        return Response({"data":AppointmentSerializer(appointment_list,many = True,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class FilterAppointmentList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        today = date.today()
        appointment_list = Appointments.objects.filter(status=SCHEDULED,created_by = request.user,date__gte = today).order_by('-date')
        if request.query_params.get("latitude") and request.query_params.get("longitude"):
            q=''
            rvt_list = []
            for u in User.objects.raw('''
                        SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                        cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                        sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id=1 Having distance < {3} ORDER BY id ;  
                    '''.format(request.query_params.get('latitude'),request.query_params.get('longitude'),q,env('MILES_RADIUS'))):
                user = User.objects.get(id=u.id)
                if str(user.is_verified) == str(VERIFIED):
                    rvt_list.append(u.id)
            appointment_list = appointment_list.filter(created_for_id__in=rvt_list)

        if request.query_params.get("service_type"):
            service_type = request.query_params.get("service_type").split(",")
            services = Services.objects.filter(category_id__in = service_type).values_list('id',flat=True)
            s_entities = Appointments.service.through.objects.filter(services_id__in = services).values_list("appointments_id",flat=True).distinct()
            appointment_list = appointment_list.filter(id__in=s_entities)

        if request.query_params.get("other") == 3 or request.query_params.get("other") == '3':
            appointment_list=appointment_list.all()
        
        if request.query_params.get("pet_type"):
            pet_type = request.query_params.get("pet_type").split(",")
            s_entities = Appointments.pet.through.objects.filter(pets_id__pet_type_id__in = pet_type).values_list("appointments_id",flat=True)
            appointment_list = appointment_list.filter(id__in=s_entities)

        if request.query_params.get("start_price") and request.query_params.get("end_price"):
            app_list = []
            for s in appointment_list:
                if int(float(s.amount)) in range(int(request.query_params.get('start_price')), int(request.query_params.get('end_price'))):
                    app_list.append(s.id)
            appointment_list = appointment_list.filter(id__in=app_list)
        data=AppointmentSerializer(appointment_list,many = True,context = {"request":request}).data
        return Response({"data":data , "status":status.HTTP_200_OK ,"url" : self.request.path} , status.HTTP_200_OK)


"""
Appointments detail view
"""
class AppointmentDetailsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('appointment_id'):
            return Response({"message":"Appointment Id not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        appointment_detail = Appointments.objects.get(id = request.query_params.get('appointment_id'))
        return Response({"data":AppointmentSerializer(appointment_detail,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

"""
customService list
"""
class CustomServiceListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        custom_service = CustomService.objects.filter(created_by = request.user).order_by('-date')
        return Response({"data":CustomServiceSerializer(custom_service,many = True,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

"""
Custom Service detail view
"""
class CustomServiceDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('custom_id'):
            return Response({"message":"Custom_service_id Id not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)
        try:
            custom_service = CustomService.objects.get(id = request.query_params.get('custom_id'),created_by = request.user)
        except:
            return Response({"message":"Custom_service not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)

        return Response({"data":CustomServiceSerializer(custom_service,many = False,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)



"""
Search Service
"""
class SearchService(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('service_cat_id'):
            return Response({"message":"service category not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)
        
        if not request.query_params.get('pet_type'):
            return Response({"message":"pet_type not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)
        
        low=request.query_params.get('low_price')
        high=request.query_params.get('high_price')

        service = Services.objects.filter(category__in = request.query_params.get('service_cat_id').split(",") , price__range =(low,high), pet = request.query_params.get('pet_type') ).order_by('price')
        return Response({"data":ServiceSerializer(service, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)



"""
Save Card
"""
class SaveCard(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        save_card = Card.objects.create(
                ac_no = request.data.get("card_number"),
                created_by = request.user,
                cvv = request.data.get("cvv"),
                card_holder_name = request.data.get("name"),
                expire_date = request.data.get("valid_untill")
                )
        save_card.save()
        return Response({"message":"Card details saved successfully","url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
RVT Profile details
"""
class RVTProfileDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        try:
            service = Services.objects.filter(created_by = request.query_params.get('rvt_id'),is_active=True)
            service =ServiceSerializer(service,many= True,context={"request":request}).data
            custom_service = CustomService.objects.filter(created_by = request.query_params.get('rvt_id'),is_active=True)
            custom_service =CustomServiceSerializer(custom_service,many= True,context={"request":request}).data
            data = service+custom_service
            return Response({"data":data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except:
            return Response({"message":"User not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})


"""
RVT Profile details for anonymous
"""
class RVTProfileDetailViewAnonymous(APIView):
    def get(self, request, *args, **kwargs):
        try:
            service = Services.objects.filter(created_by = request.query_params.get('rvt_id'))
            service =ServiceSerializer(service,many= True,context={"request":request}).data
            custom_service = CustomService.objects.filter(created_by = request.query_params.get('rvt_id'))
            custom_service =CustomServiceSerializer(custom_service,many= True,context={"request":request}).data
            data = service+custom_service
            return Response({"data":data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except:
            return Response({"message":"User not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})



"""
RVT Availability list
"""
class RVTAvailabilitylist(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        availability = ServiceAvailability.objects.filter(user = request.query_params.get('rvt_id'))
        return Response({"data":AvailabilitySerializer(availability,many = True,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)



"""
Booking view
"""
class BookingView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        data = {}
        
        local_tz = pytz.timezone("UTC")
        if request.query_params.get('timezone'):
            UTC_tz = pytz.timezone(request.query_params.get('timezone'))
        else:
            UTC_tz = pytz.timezone('Asia/Kolkata')
        current_time = str(UTC_tz.normalize(local_tz.localize(datetime.now()).astimezone(UTC_tz))).split(".")[0]
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        availability = ServiceAvailability.objects.filter(user = request.query_params.get('rvt_id'), date = request.query_params.get('date'),end_date_time__gte=current_time)
        appointment_availabilty = Appointments.objects.filter(availability__isnull=False).values_list('availability_id',flat=True)
        if appointment_availabilty:
            availability = availability.exclude(id__in=appointment_availabilty)
        data['availability'] =AvailabilitySerializer(availability,many= True,context={"request":request}).data
        service = Services.objects.filter(created_by = request.query_params.get('rvt_id'))
        data['service'] =ServiceSerializer(service,many= True,context={"request":request}).data
        custom_service = CustomService.objects.filter(created_by = request.query_params.get('rvt_id'))
        data['custom_service'] =CustomServiceSerializer(custom_service,many= True,context={"request":request}).data
        pet = Pets.objects.filter(created_by = request.user)
        data['pet'] =PetSerializer(pet,many= True,context={"request":request}).data
        return Response({"data":data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)




class BookRVTAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if not request.data.get('appointment_date'):
            return Response({"message":"Please enter the date","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('select_slot'):
            return Response({"message":"Please select the time slot","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('rvt_id'):
            return Response({"message":"User not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('amount'):
            return Response({"message":"Please enter the amount","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('description'):
            return Response({"message":"Please enter the description","url":request.path,"status":status.HTTP_400_BAD_REQUEST})             
        try:
            service_availbility = ServiceAvailability.objects.get(date = request.data.get('appointment_date'),user = request.data.get('rvt_id'),id = request.data.get('select_slot'))
        except:
            return Response({"message":"Service availability not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)             
        
        if Appointments.objects.filter(Q(start_time__range=[service_availbility.start_time,service_availbility.end_time])|Q(end_time__range = [service_availbility.start_time,service_availbility.end_time]),created_by = request.user, date = request.data.get('appointment_date'),status=SCHEDULED):
            return Response({"message":"Appointment has been already made for this timeslot","url":request.path,"status":status.HTTP_400_BAD_REQUEST})             
        else:
            try:
                percentage = Tax.objects.filter().last()
                tax_percentage = percentage.tax_percentage
            except:
                tax_percentage = 0
            if request.data.get('timezone'):
                booking_timezone = request.data.get('timezone')
            else:
                booking_timezone = 'Asia/Kolkata'
            try:
                try:
                    stripe_card = stripe.Customer.retrieve_source(request.user.customer_id,request.data.get('card_token_id'))
                    stripe_payment = stripe.Charge.create(
                        amount = int(float(request.data.get('total_amount')) * 100),
                        currency = request.user.default_currency,
                        card = stripe_card if stripe_card else request.data.get('card_token'),
                        customer = request.user.customer_id,
                        description = "Appointment payment for RVT {0} {1} ({2})".format(service_availbility.user.first_name, service_availbility.user.last_name, service_availbility.user.email),
                    )
                    charge_id = stripe_payment["id"]
                except:
                    token = stripe.Token.create(
                        card={
                            "number": request.data.get('card_number'),
                            "exp_month": int(request.data.get('exp_month')),
                            "exp_year": int(request.data.get('exp_year')),
                            "cvc": request.data.get('cvc'),
                            "name": request.data.get('name')
                        },
                    )
                    stripe_payment = stripe.Charge.create(
                        amount = int(float(request.data.get('total_amount')) * 100),
                        currency = request.user.default_currency,
                        source = token.id,
                        description = "Appointment payment for RVT {0} {1} ({2})".format(service_availbility.user.first_name, service_availbility.user.last_name, service_availbility.user.email),
                    )
                    charge_id = stripe_payment["id"]
                transaction = Transactions.objects.create(
                    amount = stripe_payment.amount/100,
                    currency = stripe_payment.currency,
                    receipt_url = stripe_payment.receipt_url,
                    transaction_id = stripe_payment.balance_transaction,
                    payment_status = stripe_payment.paid,
                    value = stripe_payment,
                    created_by = request.user,
                    charge_id = charge_id
                )
                if transaction:
                    payout = Payouts.objects.create(
                        amount = stripe_payment.amount/100,
                        user =service_availbility.user,
                        charge_id = stripe_payment.id,
                    )
            except Exception as e:
                return Response({"message":"Something went wrong with the payment!","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
            
            appointment = Appointments.objects.create(
                created_by = request.user,
                created_for = service_availbility.user,
                description = request.data.get('description'),
                date = request.data.get('appointment_date'),
                start_time = service_availbility.start_time,
                end_time = service_availbility.end_time,
                amount = request.data.get('total_amount'),
                actual_amount=request.data.get('total_services_price'),
                tax_amount = request.data.get('tax_amount'),
                tax_percentage = tax_percentage,
                mileage_fee = request.data.get('travelling_fee'),
                mileage_rate = request.data.get('mileage_rate'),
                availability = service_availbility,
                charge_id = charge_id,
                timezone = convert_timezone_to_short_form(service_availbility.rvt_timezone)
            )
            text_sent = False
            error = ""
            availability_timezone = convert_timezone_to_short_form(service_availbility.rvt_timezone)
            if service_availbility.user.is_text == 1:
                if service_availbility.user.mobile_no:
                    try:
                        send_twilio_message(env('TWILIO_NUMBER'), service_availbility.user.mobile_no, "New x Appointment Booking by {0} {1} for {2} from {3} to {4} ({5})".format(request.user.first_name,request.user.last_name, service_availbility.date, convert_time(service_availbility.start_time),convert_time(service_availbility.end_time), availability_timezone))  
                        text_sent = True
                    except Exception as e:
                        error = e
                else:
                    error = "User is missing mobile number"
            else:
                error = "User doesnt have text enabled"
            #####################   
            try:
                custom = CustomService.objects.get(service_id=request.data.get('custom_id'))
                if custom:
                    custom.is_appointment=SCHEDULED
                    custom.save()
            except:
                custom=None
            payout.appointment = appointment
            payout.save()
            transaction.appointment = appointment
            transaction.save()
            if request.data.get('service_id',None):
                services = Services.objects.filter(id__in = request.data.get('service_id').split(","), created_by_id =request.data.get('rvt_id'))
                if services:
                    for service in services:
                        appointment.service.add(service.id)
            
            if request.data.get('custom_id',None):
                services = CustomService.objects.filter(service_id__in = request.data.get('custom_id').split(","), created_by_id =request.data.get('rvt_id'))
                if services:
                    for service in services:
                        appointment.custom.add(service.id)
        
            if request.data.get('pet_id',None):
                pets = Pets.objects.filter(id__in = request.data.get('pet_id').split(","), created_by_id =request.user.id)
                if pets:
                    for pet in pets:
                        appointment.pet.add(pet)
            if service_availbility.user.is_push:
                Notification.objects.create(
                    title = "Appointment Confirmed",
                    description = "Your appointment has confirmed with {}".format(request.user.first_name),
                    created_by =request.user,
                    created_for_id=service_availbility.user.id,
                )
                try:
                    push_service = FCMNotification(api_key=env('FCM_KEY'))            
                    device = Device.objects.get(created_by_id = service_availbility.user.id)
                    msg = {
                        "title":"Appointment Confirmed",
                        "description":"Your appointment has confirmed with {}".format(request.user.first_name),
                        "type":BOOKING,
                    }
                    message_title = msg['title']
                    message_body = msg['description']
                    result = push_service.notify_single_device(
                        registration_id = device.device_token, 
                        message_title = message_title, 
                        message_body = message_body,
                        data_message={"message_title" :msg['title'],"message_body" : msg['description'],"type" : msg['type']}
                    )            
                except:
                    pass    
            if service_availbility.user.is_email:
                appointment_pet = Appointments.pet.through.objects.filter(appointments_id = appointment).values_list("pets_id",flat=True)
                current_site = get_current_site(request)
                customservices = Appointments.custom.through.objects.filter(appointments_id = appointment.id).values_list("customservice_id",flat=True)
                c_services = [i.title + '('+ i.pet_type.name +')' for i in CustomService.objects.filter(id__in=customservices)]
                allservices = Appointments.service.through.objects.filter(appointments_id = appointment.id).values_list("services_id",flat=True)
                services = [i.category.title + '('+ i.pet.name +')' for i in Services.objects.filter(id__in=allservices)]
                pets = [i.name for i in Pets.objects.filter(id__in=appointment_pet)]
                context = {
                    'domain':current_site.domain,
                    'site_name': current_site.name,
                    'protocol': 'https' if USE_HTTPS else 'http',
                    'appointment':appointment,
                    'custom':", ". join(c_services),
                    'services':", ". join(services),
                    'pets' :", ". join(pets),
                    'timezone': convert_timezone_to_short_form(booking_timezone)
                }
                message = render_to_string('registration/booking_confirmed.html', context)
                mail_subject = 'Appointment booked successfully'
                to_email =  appointment.created_for.email
                email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
                html_email = render_to_string('registration/booking_confirmed.html',context)
                email_message.attach_alternative(html_email, 'text/html')
                email_message.send()
                return Response({"data":AppointmentSerializer(appointment,many= False, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)
            return Response({"message":"Appointment booked successfully","appointment_id":appointment.id,"url":request.path,"status":status.HTTP_200_OK})


"""
Custom Service Request by end user
"""
class CustomServiceRequest(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if not request.data.get('title'):
            return Response({"message":"Please enter the title","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not request.data.get('pet_type'):
            return Response({"message":"Please enter the pet_type","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not request.data.get('description'):
            return Response({"message":"Please enter the description","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not request.data.get('location'):
            return Response({"message":"Please enter the location","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not request.data.get('date'):
            return Response({"message":"Please enter valid date","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        if not PetType.objects.filter(id = request.data.get('pet_type')):
            return Response({"message":"Pet type not found","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        elif CustomService.objects.filter(date = request.data.get('date'), pet_type =request.data.get('pet_type'),created_by_id = request.user.id):
             return Response({"message":"Service request for entered pet already raised by you on this date","url":request.path,"status": status.HTTP_400_BAD_REQUEST})
        custom_service = CustomService.objects.create(
            title = request.data.get('title'),
            description = request.data.get('description'),
            location = request.data.get('location'),
            date = request.data.get('date'),
            created_by_id = request.user.id,
            city = request.data.get('city'),
            state =request.data.get('state'),
            country =request.data.get('country'),
        )
        if request.data.get('latitude'):
            custom_service.latitude =request.data.get('latitude')
        else:
            custom_service.latitude =request.user.latitude

        if request.data.get('latitude'):
            custom_service.longitude =  request.data.get('longitude')
        else:
            custom_service.longitude =request.user.longitude

        pets = PetType.objects.get(id = request.data.get('pet_type'))
        custom_service.pet_type_id = pets.id
        custom_service.save() 
        q='' 
        user =  User.objects.raw('''
                        SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                        cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                        sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE role_id=2 or role_id=3 Having  distance < {3};  
                        '''.format(request.user.latitude,request.user.longitude,q,env('MILES_RADIUS')))
        user_id=[]
        for i in user:
            user_id.append(i.id)
        all_user = User.objects.filter(id__in= user_id).values_list('id',flat=True).exclude(id=request.user.id)
        push_service = FCMNotification(api_key=env('FCM_KEY'))            
        device_token_list = []
        [device_token_list.append(i.device_token) for i in Device.objects.filter(created_by__in = all_user)]
        print(device_token_list)

        msg = {
            "title":"Custom Service Request",
            "description":"Your have a custom request from {}".format(request.user.first_name),
            "type":BOOKING,
            }
        message_title = msg['title']
        message_body = msg['description']
        try:
            result = push_service.notify_multiple_devices(
                registration_ids = device_token_list, 
                message_title = message_title, 
                message_body = message_body,
                data_message={"message_title" :msg['title'],"message_body" : msg['description'], "type" : msg['type'],
            })
        except:
            pass



        return Response({"data":CustomServiceSerializer(custom_service, many=False, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)



"""
Custom service list created by user
"""
class UserCustomServiceList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        custom_service=CustomService.objects.filter(created_by = request.user, is_appointment = PENDING)
        return Response({"data":CustomServiceSerializer(custom_service, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Custom service applicants list
"""
class CustomServiceApplicants(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        custom_service=CustomService.objects.filter(service_id = request.query_params.get('custom_id'))
        return Response({"data":CustomServiceSerializer(custom_service, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)



"""
Custom Service status/ Accept-Reject
"""
class CustomServiceStatus(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):    
        try:
            user = User.objects.get(id = request.query_params.get('rvt_user'))
        except:
            return Response({"message":"RVT not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST},status.HTTP_200_OK)
        try:
            custom_service = Applied_by.objects.get(custom__service_id=request.query_params.get("custom_id"), applied_by = user.id)     
        except:
            return Response({"message":"custom service not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST},status.HTTP_200_OK)

        if request.query_params.get("status") == str(ACCEPTED):
            custom_service.is_applied = ACCEPTED
            custom_service = CustomService.objects.get(id =custom_service.custom_id)
            custom_service.assigend_to = user
            custom_service.save()
            appoint=Appointments.objects.create(
                created_for = user,
                created_by = request.user,
                amount = custom_service.price,
                description = custom_service.description,
                date = custom_service.date
            )
            return Response({"message":"Service is confirmed",'url':request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)
        elif request.query_params.get("status") == str(REJECTED):
            custom_service.is_applied = REJECTED
            custom_service = CustomService.objects.get(id =custom_service.custom_id)
            custom_service.assigend_to = user
            custom_service.save()
            return Response({"message":"Service is rejected",'url':request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)

"""
Past appointment list
"""
class UserPastAppointment(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        today = date.today()
        appointment = Appointments.objects.filter(Q(status=COMPLETED)|Q(status=CANCELLED),created_by = request.user)
        return Response({"data":AppointmentSerializer(appointment, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Commonly asked question
"""
class CommonlyAskedQuestion(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        faqs = Faq.objects.filter(user_type = 2).order_by('-count')[:5]
        return Response({"data":FaqSerializer(faqs, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
FAQ Description
"""
class FaqDescription(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if not request.data.get('faq_id'):
            return Response({"message":"Faq id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('count'):
            return Response({"message":"count not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        try:
            faqs = Faq.objects.get(id=request.data.get('faq_id'))
            if faqs:
                faqs.count = int(faqs.count)+int(request.data.get("count"))   
                faqs.save()
                return Response({"data":FaqSerializer(faqs, many=False, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)
        except:
             return Response({"message":"Faq id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        

"""
FAQ list
"""
class FAQList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        faqs = Faq.objects.filter(user_type = 1).order_by('-id')
        return Response({"data":FaqSerializer(faqs, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)



"""
Notification list
"""
class UserNotification(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        notification = Notification.objects.filter(created_for = request.user).order_by('-id')
        return Response({"data":NotificationSerializer(notification, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


 
"""
Marked read notification
"""
class MarkReadNotification(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        notification = Notification.objects.get(id = request.query_params.get('id'),created_for = request.user)
        if notification:
            notification.is_read = True
            notification.save()
        return Response({"data":NotificationSerializer(notification, many=False, context={"request":request}).data,"message":"Marked as read","url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)

"""
Unread Count
"""
class UnreadCount(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):        
        notification = Notification.objects.filter(created_for = request.user,is_read = False).count()
        return Response({"Count":notification})

"""
RVT availabilities
"""
class RVTAvailabilities(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('rvt_id'):
             return Response({"message":"rvt id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        availabilities = ServiceAvailability.objects.filter(user = request.query_params.get('rvt_id'))
        return Response({"data":AvailabilitySerializer(availabilities, many=True, context={"request":request}).data,"message":"Marked as read","url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)

"""
Custom appointment
"""
class UserCustomAppointment(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if not request.data.get('slot_id'):
             return Response({"message":"Availability id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('cus_id'):
             return Response({"message":"Custom id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.data.get('rvt_id'):
             return Response({"message":"Rvt id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})    
        availability= ServiceAvailability.objects.get(id =request.data.get('slot_id'))
        c_s = CustomService.objects.get(service_id = request.data.get("cus_id"))
        assigned_to = Applied_by.objects.get(applied_by_id = request.data.get("rvt_id"),custom_id=c_s.id)
        custom_service = CustomService.objects.get(id=assigned_to.custom_id.id)
        if custom_service:
            custom_service.assigend_to_id = request.data.get("rvt_id")
            custom_service.is_appointment = ACCEPT
            custom_service.save()  
        user=User.objects.get(id =request.data.get("rvt_id"))
        app=Appointments.objects.create(
                created_by = request.user,
                created_for = user,
                description = custom_service.description,
                date = custom_service.date,
                start_time = availability.start_time,
                end_time = availability.end_time,
                address = custom_service.location,
                custom_title = custom_service.title,
                availability = availability
                     )
        app.custom.add(custom_service.id)
        if user.is_push:
            Notification.objects.create(
                    title = "Appointment Confirmed",
                    description = "Your appointment has confirmed by {}".format(user.first_name),
                    created_by =request.user,
                    created_for_id=user.id,
            )
            push_service = FCMNotification(api_key=env('FCM_KEY'))
            device = Device.objects.get(created_by_id = user.id)
            msg = {
                "title":"Custom request",
                "description":"Your custom request is applied by  {}".format(request.user.first_name),
                "type":BOOKING,
            }
            message_title = msg['title']
            message_body = msg['description']
            result = push_service.notify_single_device(
                        registration_id = device.device_token if device else "", 
                        message_title = message_title, 
                        message_body = message_body,
                        data_message={"message_title" :msg['title'],"message_body" : msg['description'], "type" : msg['type'],
                    })
        return Response({"data":AppointmentSerializer(app, many=False, context={"request":request}).data,"message":"Appointment created","url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Reject applicant request
"""
class RejectApplicantRequest(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('rvt_id'):
             return Response({"message":"Rvt id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.query_params.get('cus_id'):
             return Response({"message":"Custom id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        applied_by = Applied_by.objects.get(applied_by =request.query_params.get('rvt_id'), custom_id__service_id =request.query_params.get('cus_id'))
        users=User.objects.get(id=request.user.id)
        if applied_by:
            applied_by.status = REJECTED
            applied_by.save()
        if applied_by.applied_by.is_email:
            current_site = get_current_site(request)
            context = {
                'domain':current_site.domain,
                'site_name': current_site.name,
                'protocol': 'https' if USE_HTTPS else 'http',
                'name':applied_by.applied_by.first_name,
                'user':users.first_name
            }
            message = render_to_string('user/reject_rvt_mail.html', context)
            mail_subject = 'Application  Rejected'
            to_email =  applied_by.applied_by.email
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            html_email = render_to_string('user/reject_rvt_mail.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
        return Response({"message":"Application is rejected",'url':request.path,"status":status.HTTP_200_OK})


"""
Mark cancel appointment
"""
class MarkCancelAppointmentView(APIView):
    permission_classes=(permissions.IsAuthenticated),
    def get(self,request,*args,**kwargs):
        if not request.query_params.get("cancel_remarks"):
            return Response({"message":"Please share your remarks to cancel the appointmnets",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        try:
            appointment = Appointments.objects.get(id=request.query_params.get("appointment_id"), created_by = request.user)
        except:
            return Response({"message":"Appointment id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})
        if appointment:
            appointment.status=CANCELLED
            appointment.past_appointment=True
            
        if appointment.created_for.is_push:
            Notification.objects.create(
                title = "Appointment Cancellation",
                description = "Your appointment is cancelled with {}".format(appointment.created_by.first_name),
                created_by = request.user,
                created_for_id= appointment.created_for.id,
                appointment = appointment
            )
            try:
                push_service = FCMNotification(api_key=env('FCM_KEY'))            
                device = Device.objects.get(created_by_id = appointment.created_for.id)
                msg = {
                    "title":"Appointment Cancelled",
                    "description":"Your appointment has cancel with {}".format(request.user.first_name),
                    "type":BOOKING,
                }
                message_title = msg['title']
                message_body = msg['description']
                result = push_service.notify_single_device(
                            registration_id = device.device_token, 
                            message_title = message_title, 
                            message_body = message_body,
                            data_message={"message_title" :msg['title'],"message_body" : msg['description'],"type" : msg['type']
                        })
            except:
                pass 
        appointment.save()
        now_utc = timezone.now()  
        refund_percentage = 0
        refund_amount = 0
        appointment_created_date_utc = appointment.created_on
        appointment_date = appointment.date
        appointment_time = appointment.start_time
        appointment_datetime = datetime.combine(appointment_date, appointment_time)
        appointment_timezone = get_timezone_from_coordinates(appointment.created_for.latitude,appointment.created_for.longitude)
        pytz_timezone=pytz.timezone(appointment_timezone)
        aware_combo_date = pytz_timezone.localize(appointment_datetime)
        appointment_scheduled_date = aware_combo_date.astimezone(pytz.UTC)
        time_until_appointment_in_hours = round((datetime.timestamp(appointment_scheduled_date) - datetime.timestamp(now_utc))/3600)
        time_since_booking = round((now_utc - appointment_created_date_utc).seconds/3600,1)
        print(now_utc)
        print(appointment_created_date_utc)
        print((now_utc - appointment_created_date_utc))
        print((now_utc - appointment_created_date_utc).seconds/3600)
        mileage_fee = appointment.mileage_fee
        payout_object = Payouts.objects.filter(appointment=appointment).last()     
        print(time_since_booking,"time_since_booking")
        print(time_until_appointment_in_hours,"time_until_appointment_in_hours")

        if time_since_booking <= 1:
            refund_percentage = 100
        elif time_until_appointment_in_hours <= 12:
            refund_percentage = 0
        elif time_until_appointment_in_hours <24 and time_until_appointment_in_hours > 12:
            refund_percentage = 50
        elif time_until_appointment_in_hours >= 24:
            refund_percentage = 100
        print(refund_percentage)
        refundamount = (float(payout_object.appointment.amount)-float(mileage_fee))*(refund_percentage/100)+float(mileage_fee)
        print(refundamount)
        if refundamount:
            try:
                refund = stripe.Refund.create(
                    charge=payout_object.charge_id,
                    amount = int(refundamount) * 100
                )
                if refund:
                    Transactions.objects.create(
                        amount = refund.amount/100,
                        currency = refund.currency,
                        transaction_id = refund.balance_transaction,
                        created_by = appointment.created_by,
                        payment_type =3,
                        payment_status=refund.status,
                        appointment=appointment
                    )
                    appointment.refund_amount=refundamount
            except Exception as e:
               return Response({"message":"Something went wrong with the payment!","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
            rvt_user=User.objects.get(id=appointment.created_for.id)
            appointment.save()
            if rvt_user.is_email: 
                current_site = get_current_site(request)
                context = {
                    'domain':current_site.domain,
                    'site_name': current_site.name,
                    'protocol': 'https' if USE_HTTPS else 'http',
                    'name':appointment.created_for.first_name,
                    'date':appointment.date,
                    'start_time':appointment.start_time,
                    'service':appointment.service.all,
                    'custom_service':appointment.custom.all,
                    'end_time':appointment.end_time,
                }
                message = render_to_string('registration/booking_cancelled.html', context)
                mail_subject = 'Appointment Cancellation'
                if request.user.role_id == USERS:
                    to_email =  appointment.created_for.email
                else:
                    to_email = appointment.created_by.email
                email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
                html_email = render_to_string('registration/booking_cancelled.html',context)
                email_message.attach_alternative(html_email, 'text/html')
                email_message.send()
            availability_timezone = convert_timezone_to_short_form(appointment.timezone)
            if appointment.created_for.is_text:
                if appointment.created_for.mobile_no:
                    try:
                        send_twilio_message(env('TWILIO_NUMBER'), appointment.created_for.mobile_no, "x Appointment Cancelation by {0} {1} for {2} from {3} to {4} ({5}) [{6}]".format(request.user.first_name,request.user.last_name, appointment.date, convert_time(appointment.start_time),convert_time(appointment.end_time), availability_timezone, appointment.cancel_remarks))  
                        text_sent = True
                    except Exception as e:
                        error = e
                else:
                    error = "User is missing mobile number"
            else:
                error = "User doesnt have text enabled"
            message = 'Appointment cancelled successfully. {0} refund will be processed to your account.'.format(refundamount)
        else:
            message = 'Appointment cancelled. Refunded({0})'.format(refundamount)
        return Response({"data":AppointmentSerializer(appointment,many = False,context={"request":request}).data,"message":message,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Mark notification as read 
"""
class MarkNotificationRead(APIView):
    permission_classes=(permissions.IsAuthenticated),
    def get(self,request,*args,**kwargs):
        notification = Notification.objects.filter(created_for = request.user)
        if notification:
           notification.update(is_read = True)
        return Response({"data":NotificationSerializer(notification,many = True,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

 

"""
Mark as favourite
"""
class MarkFavourite(APIView):
    permission_classes=(permissions.IsAuthenticated),
    def post(self,request,*args,**kwargs):
        try:
            favourite=Favourite.objects.get(created_for = request.data.get('rvt_id'), created_by = request.user)    
            if favourite:
                favourite.is_favourite = True
                favourite.save()
                return Response({"data":FavouriteSerializer(favourite,many = False,context={"request":request}).data,"message":"Liked","url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except:
            favourite=Favourite.objects.create(
                created_for_id = request.data.get('rvt_id'),
                created_by = request.user,
                is_favourite = True
            )
            return Response({"data":FavouriteSerializer(favourite,many = False,context={"request":request}).data,"message":"Liked","url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)



"""
Mark as Un-favourite
"""
class MarkUnFavourite(APIView):
    permission_classes=(permissions.IsAuthenticated),
    def get(self,request,*args,**kwargs):
        if not request.query_params.get('rvt_id'):
            return Response({"message":"Rvt not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        try:
            favourite = Favourite.objects.get(created_for = request.query_params.get('rvt_id'), created_by = request.user)
        except:
            return Response({"message":"Rvt id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})

        if favourite:
            favourite.delete()
            return Response({"data":FavouriteSerializer(favourite,many = False,context={"request":request}).data,"message":"Disliked","url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        else:
            return Response({"message":"Rvt id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})


"""
Favourite RVT listing
"""
class FavouriteRVTListing(APIView):
    permission_classes=(permissions.IsAuthenticated),
    def get(self,request,*args,**kwargs):
        favourite = Favourite.objects.filter(is_favourite = True, created_by = request.user)
        return Response({"data":FavouriteSerializer(favourite,many = True,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

"""
Chat user profile 
"""
class ChatUserProfile(APIView):
    permission_classes=(permissions.IsAuthenticated),
    def get(self,request,*args,**kwargs):
        user = User.objects.get(id = request.query_params.get('user_id'))
        return Response({"data":UserSerializer(user,many = False,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Near By RVT
"""
class NearByRVTView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request ,*args, **kwargs):
        q=''
        user_list = []
        for user in User.objects.raw('''
                    SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                    cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                    sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id=1 Having  distance < {3} ORDER BY id ;  
                '''.format(request.user.latitude,request.user.longitude,q,env('MILES_RADIUS'))):
            if str(user.is_verified) == str(VERIFIED):
                user_list.append(user.id)
            user_list.append(user.id)
        users = User.objects.filter(id__in=user_list,state_id=ACTIVE)
        data = UserSerializer(users,many = True,context = {"request":self.request}).data
        return Response({"data": data},status = status.HTTP_200_OK)
        


"""
Near By RVT list for anonymous user
"""
class AnonymousNearByRVTView(views.APIView):
    def get(self, request ,*args, **kwargs):
        ids=[]
        if not request.query_params.get('latitude'):
            return Response({"message":"latitude not found.","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.query_params.get('longitude'):
            return Response({"message":"longitude not found.","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        q=''
        user=User.objects.raw('''
                    SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                    cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                    sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id = 1 Having  distance < {3} ORDER BY id ;  
                '''.format(request.query_params.get('latitude'),request.query_params.get('longitude'),q,env('MILES_RADIUS')))

        for i in user:
            user = User.objects.get(id=i.id)
            if str(user.is_verified) == str(VERIFIED):
                ids.append(i.id)
        services_distinct = Services.objects.filter(created_by_id__in = ids).values_list('created_by_id', flat=True).distinct()
        services = []
        for user in services_distinct:
            s = Services.objects.filter(created_by_id = user).first()
            services.append(s)
        data = ServiceSerializer(services,many = True,context = {"request":self.request}).data
        data = data[::-1]
        return Response({"data": data,"status": status.HTTP_200_OK},status = status.HTTP_200_OK)




"""
RVT List Service Category Wise
"""
class CategoryWiseRVTListAPI(APIView):
    def get(self, request, *args, **kwargs):
        ids=[]
        if not request.query_params.get('category'):
            return Response({"message":"Please select the category","url":request.path,"status": status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)
        q=''
        user=User.objects.raw('''
                    SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                    cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                    sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id = 1 Having  distance < {3} ORDER BY id ;  
                '''.format(request.query_params.get('latitude'),request.query_params.get('longitude'),q,env('MILES_RADIUS')))
        for i in user:
            if str(i.is_verified) == str(VERIFIED):
                ids.append(i.id)
        rvt_user = Services.objects.filter(created_by_id__in= ids, category = request.query_params.get('category'),created_by__role_id = RVT_LVT).values_list('id','created_by_id')
        user_id =[]
        service = []
        for i,j in rvt_user:
            if j in user_id:
                continue
            else:
               user_id.append(j)
               service.append(i) 

        rvt_user = Services.objects.filter(id__in =service )
        return Response({"data":ServiceSerializer(rvt_user, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Admin service list for anonymous user 
"""
class AnonymousServiceList(views.APIView):
    def get(self, request ,*args, **kwargs):
        service_list = ServiceCategory.objects.all()
        return Response({"data":CategorySerializer(service_list,many = True,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status = status.HTTP_200_OK)


"""
RVT Rating list View
"""
class RVTRatingList (APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('rvt_user'):
            return Response({"message":"RVT  not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_200_OK)

        rating = Rating.objects.filter(created_for = request.query_params.get('rvt_user'))
        return Response({"data":RatingSerializer(rating, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
rating filter 
"""
class Ratingfilter(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('rvt_id'):
            return Response({"message":"RVT  not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        if not request.query_params.get('rating'):
            return Response({"message":"rating  not found","url":request.path,"status":status.HTTP_400_BAD_REQUEST})
        rating = Rating.objects.filter(created_for = request.query_params.get('rvt_id'), rating =request.query_params.get('rating'))
        return Response({"data":RatingSerializer(rating, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Banner list
"""
class Bannerlisting(APIView):
    def get(self, request, *args, **kwargs):
        banner = Announcements.objects.filter(Q(target=TARGET_USER)|Q(target=TARGET_ALL),status=1).order_by('-id')
        return Response({"data":BannerSerializer(banner, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Filter API
"""
class SearchFilter(APIView):
    def post(self, request, *args, **kwargs):
        services = Services.objects.all().order_by('-id')
        if request.data.get('latitude') and request.data.get('longitude'):
            rvt_ids=[]
            q=''
            for i in User.objects.raw('''
                        SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                        cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                        sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id = 1 Having  distance < {3} ORDER BY id ;  
                    '''.format(request.data.get('latitude'),request.data.get('longitude'),q,env('MILES_RADIUS'))):
                user = User.objects.get(id=i.id)
                if str(user.is_verified) == str(VERIFIED):
                    rvt_ids.append(i.id)
            services = services.filter(created_by_id__in=rvt_ids)

        if request.data.get('service_id'):
            services = services.filter(category__in=request.data.get('service_id').split(","))
        
        if request.data.get("other") == 3 or request.data.get("other") == '3':
            services=services.all().exclude(pet__created_by=ADMIN)

        if request.data.get('pet_type') and not request.data.get('pet_type')=='0':
            services = services.filter(pet__in = request.data.get('pet_type').split(","))

        if str(request.data.get('start_price')) and str(request.data.get('end_price')):
            s_list = []
            for s in services:
                if int(float(s.price)) in range(int(request.data.get('start_price')), int(request.data.get('end_price'))):
                    s_list.append(s.id)
            services = services.filter(id__in=s_list)
        services_distinct = services.values_list('created_by_id', flat=True)
        unique_rvt_id=set(services_distinct)
        services_=list(unique_rvt_id)
        services_list = []
        for user in services_:
            service = Services.objects.filter(created_by_id = user).first()
            services_list.append(service)
        return Response({"data":ServiceSerializer(services_list, many=True, context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status.HTTP_200_OK)


"""
Push notification ON/OFF
"""
class NotificationsStatusPush(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_push:
            user.is_push = False
            user.save()
            return Response({"message":"Push notification turned OFF","url":request.path,"status":status.HTTP_200_OK})
        elif not user.is_push:
            user.is_push = True
            user.save()
            return Response({"message":"Push notification turned ON","url":request.path,"status":status.HTTP_200_OK})



"""
Email notification ON/OFF
"""
class NotificationsStatusEmail(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_email:
            user.is_email = False
            user.save()
            return Response({"message":"Email notification turned OFF","url":request.path,"status":status.HTTP_200_OK})
        elif not user.is_email:
            user.is_email = True
            user.save()
            return Response({"message":"Email notification turned ON","url":request.path,"status":status.HTTP_200_OK})


"""
Text notification ON/OFF
"""
class NotificationsStatusText(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_text:
            user.is_text = False
            user.save()
            return Response({"message":"Text notification turned OFF","url":request.path,"status":status.HTTP_200_OK})
        elif not user.is_text:
            user.is_text = True
            user.save()
            return Response({"message":"Text notification turned ON","url":request.path,"status":status.HTTP_200_OK})


"""
Direct Message notification ON/OFF
"""
class NotificationsStatusDirectMessage(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_direct_message:
            user.is_direct_message = False
            user.save()
            return Response({"message":"Direct Message notification turned OFF","url":request.path,"status":status.HTTP_200_OK})
        elif not user.is_direct_message:
            user.is_direct_message = True
            user.save()
            return Response({"message":"Direct Message turned ON","url":request.path,"status":status.HTTP_200_OK})


"""
Location Tracking notification ON/OFF
"""
class NotificationsStatusLocationTracking(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_location_tracking:
            user.is_location_tracking = False
            user.save()
            return Response({"message":"Location Tracking  notification turned OFF","url":request.path,"status":status.HTTP_200_OK})
        elif not user.is_location_tracking:
            user.is_location_tracking = True
            user.save()
            return Response({"message":"Location Tracking notification turned ON","url":request.path,"status":status.HTTP_200_OK})


"""
Mark mail to vet
"""
class mailToVets(APIView):
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('appointment_id'):
            return Response({"message":"Appointment id not found",'url':request.path,"status":status.HTTP_400_BAD_REQUEST}) 
        appointments = Appointments.objects.get(id=request.query_params.get('appointment_id'))
        pets = Appointments.pet.through.objects.filter(appointments_id=request.query_params.get('appointment_id')).values_list('pets_id',flat=True)
        vet_emails = [i.vet_email if i.vet_email else '' for i in Pets.objects.filter(id__in=pets,vet_email__isnull=False)]
        notes = Notes.objects.filter(appointment=appointments.id)
        if vet_emails and notes:
            for i in vet_emails:
                if i != '':
                    current_site = get_current_site(request)
                    context = {
                        'domain':current_site.domain,
                        'site_name': current_site.name,
                        'protocol': 'https' if USE_HTTPS else 'http',
                        'notes':notes,
                        'name':appointments.created_by.first_name,
                        'user':appointments.created_for.first_name,
                        'start_time':appointments.start_time,
                        'end_time':appointments.end_time,
                        'service':appointments.service.all,
                        'custom_service':appointments.custom.all,
                        'date':appointments.date,
                        'pet_name':appointments.pet.all,
                    }
                    message = render_to_string('rvt/mail_to_vet.html', context)
                    mail_subject = 'Notes And Appointment Details'
                    try:
                        email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [i])
                        html_email = render_to_string('rvt/mail_to_vet.html',context)
                        email_message.attach_alternative(html_email, 'text/html')
                        email_message.send()
                    except:
                        pass
            return Response({"message":"Email Sent Successfully!",'url':request.path,"status":status.HTTP_200_OK}) 
        else:
            if not vet_emails:
                message = "No Vet Email Found"
            else:
                message = "No Notes Found"
            return Response({"message":message,'url':request.path,"status":status.HTTP_400_BAD_REQUEST}) 


"""
User Pet appointment
"""
class PetAppointment(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        app_id = Appointments.pet.through.objects.filter(pets_id=request.query_params.get('pet_id')).values_list('appointments_id',flat=True)
        appointments=Appointments.objects.filter(id__in=app_id )
        return Response({"data":AppointmentSerializer(appointments,many = True,context={"request":request}).data,"url":request.path,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Cancel Custom Appointment
"""
class CancelCustomApp(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        try:
            custom=CustomService.objects.get(service_id = request.query_params.get('cus_id'))
            if custom:
                custom.delete()
            return Response({"message":"Custom request has been cancelled.",'url':request.path,"status":status.HTTP_200_OK}) 

        except:
            return Response({"message":"Custom id not found.",'url':request.path,"status":status.HTTP_400_BAD_REQUEST})



class FilterPastAppointmentList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        today = date.today()
        appointment_list = Appointments.objects.filter(Q(status=CANCELLED)|Q(status=COMPLETED),created_by = request.user,date__lt = today).order_by('-date')

        if request.query_params.get("latitude") and request.query_params.get("longitude"):
            q=''
            rvt_list = []
            for u in User.objects.raw('''
                        SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                        cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                        sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id = 1 Having  distance < {3} ORDER BY id ;  
                    '''.format(request.query_params.get('latitude'),request.query_params.get('longitude'),q,env('MILES_RADIUS'))):
                user = User.objects.get(id=u.id)
                if str(user.is_verified) == str(VERIFIED):
                    rvt_list.append(u.id)
            appointment_list = appointment_list.filter(created_for_id__in=rvt_list)

        if request.query_params.get("service_type"):
            service_type = request.query_params.get("service_type").split(",")
            services = Services.objects.filter(category_id__in = service_type).values_list('id',flat=True)
            s_entities = Appointments.service.through.objects.filter(services_id__in = services).values_list("appointments_id",flat=True).distinct()
            appointment_list = appointment_list.filter(id__in=s_entities)

        if request.query_params.get("other") == 3 or request.query_params.get("other") == '3':
            appointment_list=appointment_list.all()
        
        if request.query_params.get("pet_type"):
            pet_type = request.query_params.get("pet_type").split(",")
            s_entities = Appointments.pet.through.objects.filter(pets_id__pet_type_id__in = pet_type).values_list("appointments_id",flat=True)
            appointment_list = appointment_list.filter(id__in=s_entities)

        if request.query_params.get("start_price") and request.query_params.get("end_price"):
            app_list = []
            for s in appointment_list:
                    if int(float(s.amount)) in range(int(request.query_params.get('start_price')), int(request.query_params.get('end_price'))):
                        app_list.append(s.id)
            appointment_list = appointment_list.filter(id__in=app_list)
        data=AppointmentSerializer(appointment_list,many = True,context = {"request":request}).data
        return Response({"data":data , "status":status.HTTP_200_OK ,"url" : self.request.path} , status.HTTP_200_OK)
 

class GetBookingPrices(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        if request.data.get('service_ids'):
            services = Services.objects.filter(id__in = request.data.get('service_ids').split(','))
        else:
            services = None
        if request.data.get('custom_service_ids'):
            custom_services = CustomService.objects.filter(service_id__in = request.data.get('custom_service_ids').split(','))
        else:
            custom_services = None
        try:
            services_price = sum([float(i.price if i.price else 0) for i in services])
        except:
            services_price = 0
        try:
            custom_prices = sum([float(i.price if i.price else 0) for i in custom_services]) 
        except:
            custom_prices = 0
        total_services_price = services_price + custom_prices
        try:
            tax_percentage = Tax.objects.filter().last()
            tax_amount = (float(total_services_price) * float(tax_percentage.tax_percentage)) / 100
        except:
            tax_amount = 0
        slat = 0
        slon = 0
        elat = request.user.latitude
        elon = request.user.longitude
        travelling_fee = 0
        mileage_rate = 0
        if services:
            if(len(services) > 0):
                slat = services[0].created_by.latitude
                slon = services[0].created_by.longitude
                try:
                    mileage = Mileage.objects.filter().last()
                    mileage_rate = float(mileage.mileage_percentage)
                except:
                    mileage_rate = 0
                time, distance ,distance_km = get_distance_from_coordinates(slat,slon,elat, elon)
                travelling_fee = mileage_rate * distance_km
        total_amount = total_services_price + tax_amount + travelling_fee
        return Response({
            "total_services_price":total_services_price , 
            "tax_amount":tax_amount , 
            "travelling_fee":travelling_fee , 
            "total_amount":total_amount , 
            "mileage_rate":mileage_rate , 
            "status":status.HTTP_200_OK ,
            "url" : self.request.path
        } , status.HTTP_200_OK)

