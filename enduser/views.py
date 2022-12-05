from django.contrib.sessions.models import Session
import timeago
from os import environ
from django.views import View
from pyfcm import FCMNotification
from accounts.views import user_is_entry_author
from chat.models import *
from enduser.models import Favourite, HelpRequest, Images, PetType
from faq.models import Faq
from notification.models import Notification
from rating.models import Rating
from rvt_lvt.models import *
from datetime import datetime, timedelta
from accounts.models import *
from accounts.constants import *
from enduser.models import Card
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from geopy.geocoders import Nominatim
from django.db.models.query_utils import Q
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from datetime import date
from superuser.models import Announcements, HelpTopics, Recommendation, Tax, Mileage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
import stripe
import environ
env = environ.Env()
environ.Env.read_env()
stripe.api_key = env('STRIPE_KEY')
from django.core.mail import EmailMultiAlternatives
import pytz
from global_utils import *
from dateutil import tz
from django.utils import timezone


@login_required
def UserDashboard(request):
    today = date.today()
    nearby = []
    service_user = []
    q=''
    try:
        appointments = Appointments.objects.filter(created_by = request.user,date__gte = today,status=SCHEDULED)
        page = request.GET.get('page1', 1)
        paginator = Paginator(appointments, 5)
        try:
            appointments = paginator.page(page)
        except PageNotAnInteger:
            appointments = paginator.page(1)
    except EmptyPage:
        appointments = paginator.page(paginator.num_pages)
    custom_appointments = CustomService.objects.filter(created_by = request.user, is_appointment = PENDING).order_by('-created_on')
    my_rvt = Appointments.objects.filter(created_by = request.user).values_list("created_for",flat=True).distinct()
    rvt_service,name,rating,price,address,city,state,user_id, image  = [],[],[],[],[],[],[],[],[]
    my_rvts = User.objects.filter(id__in=my_rvt)
    for user in my_rvts:
        user_id.append(user.id) 
        name.append(user.first_name + '   ' + user.last_name)
        address.append(user.address)
        city.append(user.city)
        state.append(user.state)
        rating.append(0)
        _service = Services.objects.filter(created_by = user).values_list("category_id",flat=True)
        _service_category = ServiceCategory.objects.filter(id__in = _service)
        lst = []
        for i in _service_category:
            lst.append(i.title)
        lst=",".join(lst)
        rvt_service.append(lst)
        try:
            min_price = Services.objects.filter(created_by_id = user).order_by('price')[0]
            price.append(min_price.price)
            if min_price.created_by.profile_pic:
                image.append(min_price.created_by.profile_pic)
            else:
                image.append(None)
        except:
            price.append('')
    my_rvt_data = zip(rvt_service,name,rating,price,address,city,state,user_id,image)
    rvt_user =  User.objects.raw('''
                SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id = 1 Having  distance < {3};  
                '''.format(request.user.latitude,request.user.longitude,q,env('MILES_RADIUS')))
    for i in rvt_user:
        user = User.objects.get(id=i.id)
        if str(user.is_verified) == str(VERIFIED):
            nearby.append(i.id)
    service = Services.objects.filter(is_active = True).values_list('created_by_id',flat=True).distinct()
    for i in service:
        service_user.append(i)
    custom_service = CustomService.objects.filter(is_active = True).values_list('created_by_id',flat=True).distinct()
    for i in custom_service:
        service_user.append(i)
    r_user_list = [value for value in nearby if value in service_user]
    r_user = User.objects.filter(id__in = r_user_list, state_id=ACTIVE).order_by('-created_on').exclude(id=request.user.id)
    service_category = ServiceCategory.objects.all()
    user = Appointments.objects.filter(created_by = request.user).values_list('created_for',flat=True)
    service = Services.objects.filter(created_by__in = user)
    service_categories = ServiceCategory.objects.all()
    past_appointments = Appointments.objects.filter(created_by = request.user,date__lt = today).order_by('-id')
    page = request.GET.get('page2', 1)
    paginator = Paginator(past_appointments, 5)
    try:
        past_appointments = paginator.page(page)
    except PageNotAnInteger:
        past_appointments = paginator.page(1)
    except EmptyPage:
        past_appointments = paginator.page(paginator.num_pages)
    pet_type =PetType.objects.all().order_by('-created_on')
    fav =Favourite.objects.filter(created_by=request.user,is_favourite = True).values_list("created_for",flat=True)
    banners= Announcements.objects.filter(Q(target=TARGET_USER)|Q(target=TARGET_ALL), status=1).order_by('-id')
    return render(request, 'user/index.html', {"title":"Dashboard","nbar" :"","r_user":r_user,"service_category":service_category,"appointments":appointments,"service":service,"service_categories":service_categories,"my_rvt_data":my_rvt_data,"my_rvts":my_rvts,"past_appointments":past_appointments,"pets":pet_type,"fav":fav,"banners":banners,"custom_appointments":custom_appointments})


"""
View all RVT
"""
@login_required
def ViewAllRrvt(request):
    nearby =[]
    service_user=[]
    min_price=[]
    q=''
    rvt_user = User.objects.raw('''
                SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id = 1 Having  distance < {3};  
                '''.format(request.user.latitude,request.user.longitude,q,env('MILES_RADIUS')))
    for i in rvt_user:
        user = User.objects.get(id=i.id)
        if str(user.is_verified) == str(VERIFIED):
            nearby.append(i.id)
    service = Services.objects.filter(is_active = True).values_list('created_by_id',flat=True).distinct()
    for i in service:
        service_user.append(i)
    custom = CustomService.objects.filter(is_active = True).values_list('created_by_id',flat=True).distinct()
    for i in custom:
        service_user.append(i)
    r_user_list = [value for value in nearby if value in service_user]
    r_user = User.objects.filter(state_id=ACTIVE, id__in = r_user_list).order_by('-id').exclude(id=request.user.id)
    rvt_services = Services.objects.filter(created_by_id__in = r_user_list)
    rvt_custom_services = CustomService.objects.filter(created_by_id__in = r_user_list)
    for user in r_user_list:
        try:        
            min_price_service = Services.objects.filter(created_by_id = user).order_by('price')[0]
        except:
            min_price_service = None
        try:        
            min_price_custom = CustomService.objects.filter(created_by_id = user).order_by('price')[0]
        except:
            min_price_custom = None
        
        if min_price_service and min_price_custom:
            if float(min_price_service.price if min_price_service.price else 0) < float(min_price_custom.price if min_price_custom.price else 0):
                min_price.append(min_price_service)
            else:
                min_price.append(min_price_custom)
        elif min_price_custom:
            min_price.append(min_price_custom)
        elif min_price_service:
            min_price.append(min_price_service)
        else:
            min_price.append()
    fav = Favourite.objects.filter(created_by=request.user,is_favourite = True).values_list("created_for",flat=True)
    servicess = []
    for user in User.objects.filter(is_verified=VERIFIED):
        try:        
            min_price_service = Services.objects.filter(created_by = user).order_by('price')[0]
        except:
            min_price_service = None
        try:        
            min_price_custom = CustomService.objects.filter(created_by = user).order_by('price')[0]
        except:
            min_price_custom = None
        
        if min_price_service and min_price_custom:
            if float(min_price_service.price if min_price_service.price else 0) < float(min_price_custom.price if min_price_custom.price else 0):
                servicess.append(min_price_service)
            else:
                servicess.append(min_price_custom)
        elif min_price_custom:
            servicess.append(min_price_custom)
        elif min_price_service:
            servicess.append(min_price_service)
    return render(request , "user/all-rvt.html",{"title":"RVT's","map_rvt":servicess,"rvt_user":r_user,"rvt_services":rvt_services,"rvt_custom_services":rvt_custom_services,"min_price":min_price,"fav":fav})



@login_required
def CategoryWiseRVTdetail(request):
    try:
        rvt = Services.objects.filter(category_id = request.GET.get('id')).exclude(created_by=request.user).values_list('created_by_id',flat=True).distinct()
        rvt_users=[]
        for r in rvt:
            rvt_users.append(Services.objects.filter(created_by_id=r).first())

        fav_ids = Favourite.objects.filter(created_by=request.user,is_favourite = True).values_list('created_for_id', flat=True)
        if rvt_users:
            my_rvt = Services.objects.filter(category_id = request.GET.get('id')).exclude(created_by=request.user).values_list("created_by",flat=True)
            my_rvts = User.objects.filter(id__in = my_rvt)
            services, min_price,id,is_fav = [],[],[],[]
            for user in my_rvts:
                fav = Favourite.objects.filter(created_by = request.user,created_for = user,is_favourite=True)
            if fav:
                is_fav.append("1")
            else:
                is_fav.append("")
            id.append(user)
            for user in rvt_users:
               
                services.append(Services.objects.filter(created_by = user.created_by))
                min_price.append(Services.objects.filter(created_by_id = user.created_by).order_by('price')[0])
            rvt_user = zip(rvt_users,services,min_price)
            return render(request, "user/user-detail.html",{"title":"RVT's","rvt_user":rvt_user,"rvt_users":rvt_users,"favt":fav_ids})
        else:
            rvt_user =None
            rvt_users = None
            return render(request, "user/user-detail.html",{"rvt_user":rvt_user,"rvt_users":rvt_users,"favt":fav_ids})
    except:
        rvt_user =None
        rvt_users = None    
        return render(request, "user/user-detail.html",{"title":"RVT's","rvt_user":rvt_user,"rvt_users":rvt_users})



"""
user profile
"""
@login_required
def UserProfile(request):
    BANK_ADD_URL = env('BANK_ADD_URL')
    if request.method == 'GET':
        user = User.objects.get(id = request.user.id)
        try:
            stripe_bank_accounts = stripe.Account.list_external_accounts(user.bank_account_id,
                                object="bank_account",
                                limit=1)
        except:
            stripe_bank_accounts = None
        pets = Pets.objects.filter(created_by = request.user).order_by("-created_on")
        try:
            cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
            customer = stripe.Customer.retrieve(request.user.customer_id)
            default = customer.default_source
        except:
            cards = None
            default = None
        API_KEY = env('GOOGLE_API_KEY')
        completed_jobs=Appointments.objects.filter(created_by=request.user,status=COMPLETED).count()
        return render(request, 'user/user-profile.html',{"default":default,"stripe_bank_accounts":stripe_bank_accounts,"title":"Settings","user":request.user,"nbar":"settings","pets":pets,"cards":cards,"API_KEY":API_KEY,"completed_jobs":completed_jobs,"BANK_ADD_URL":BANK_ADD_URL})

    if request.method == 'POST':
        user = User.objects.get(id = request.user.id)
        if request.POST.get("first_name"):
            user.first_name = request.POST.get("first_name")

        if request.POST.get("last_name"):
            user.last_name = request.POST.get("last_name")

        if request.POST.get("mobile_no"):
            user.mobile_no = request.POST.get("mobile_no")

        if request.POST.get("address"):
            user.address = request.POST.get("address")

        if request.POST.get("city"):
            user.city = request.POST.get("city")

        if request.POST.get("state"):
            user.state = request.POST.get("state")

        if request.POST.get("about_me"):
            user.about_me = request.POST.get("about_me")
        if request.POST.get("country"):
            user.country = request.POST.get("country")
            if user.country.lower() == "canada":
                user.default_currency="cad"
            else:
                user.default_currency="usd"

        if request.POST.get("latitude"):
            user.latitude = request.POST.get("latitude")
        else:
            messages.add_message(request, messages.INFO, 'Please fill the address')
            return redirect('enduser:user_profile')
        if request.POST.get("longitude"):
            user.longitude = request.POST.get("longitude")
        else:
            messages.add_message(request, messages.INFO, 'Please fill the address')
            return redirect('enduser:user_profile')

        user.save()
        messages.add_message(request, messages.INFO, 'Profile Updated Successfully')
        return redirect('enduser:user_profile')


"""
edit profile_pic
"""
@login_required
def UserProfileImage(request):
    if request.method == 'POST':
        user = User.objects.get(id = request.user.id)
        file_pic = request.FILES.get("profile_pic")
        if file_pic:
                ext = os.path.splitext(file_pic.name)[1]
                valid_extensions = ['.jpg', '.JPG','.jpeg', '.JPEG','.gif','.png','.PNG']
                if not ext.lower() in valid_extensions:
                    messages.error(request, 'Unsupported File Format. please select proper Image Format')
                    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
                else:
                    user.profile_pic = request.FILES.get("profile_pic")
                    user.save()
                    messages.add_message(request, messages.INFO, 'Profile Image Updated Successfully')
                    return redirect('enduser:user_profile')
        else:
            messages.add_message(request, messages.INFO, 'Profile image Not Selected')
            return redirect('enduser:user_profile')


"""
RVT Profile
"""
@login_required
def UserRvtProfile(request,id):
    rvt_user = User.objects.get(id = id)
    services = Services.objects.filter(created_by = rvt_user, is_active = True).order_by('-id')
    custom_service = CustomService.objects.filter(created_by = rvt_user, is_active = True).order_by('-id')
    availability = ServiceAvailability.objects.filter(user = rvt_user)
    return render(request , "user/user-rvt-profile.html" , {"title":"RVT Profile", "nbar" : "user_rvt_profile","rvt_user":rvt_user,"services":services,"availability":availability,"custom_service":custom_service},)


"""
Add Pet
"""
@login_required
def UserAddPet(request):
    BANK_ADD_URL = env('BANK_ADD_URL')
    try:
        stripe_bank_accounts = stripe.Account.list_external_accounts(
            request.user.bank_account_id,
            object="bank_account",
            limit=1
        )
    except:
        stripe_bank_accounts = None
    if request.method == 'GET':
        pet_type = PetType.objects.all().order_by('-created_on')
        return render(request , "user/add-pet.html" , {"title":"Add Pet", "nbar" : "settings","pet_type":pet_type,"stripe_bank_accounts":stripe_bank_accounts})

    if request.method == 'POST':
        image = request.FILES.getlist("pet_image")
        pet = Pets.objects.create(
            name = request.POST.get('pet_name'),
            age = request.POST.get('pet_age'),
            breed = request.POST.get('pet_breed'),
            pet_gender = request.POST.get('pet_gender'),
            size = request.POST.get('size'),
            created_by = request.user,
            description = request.POST.get('about'),
            vet_name = request.POST.get('vet_info'),
            vet_email = request.POST.get('vet_email'),
            vet_number = request.POST.get('vet_phone'),
            vet_adrress = request.POST.get('vet_adrress'),
            vet_profile=request.FILES.get('vet_image'),
            vaccines = request.POST.get('vet_adrress'),
            )
        images=[]
        for img in image:
            images.append(Images.objects.create(
                file = img,
                created_by = request.user
            ))
        if image:
            pet.image.set(images)
            pet.save()
        pets = PetType.objects.get(id = request.POST.get('pet_type'))
        pet.pet_type_id = pets
        pet.save()
        user = User.objects.get(id = request.user.id)
        pets = Pets.objects.filter(created_by = request.user).order_by("-id").order_by('-created_on')
        try:
            cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
            customer = stripe.Customer.retrieve(request.user.customer_id)
            default = customer.default_source
        except:
            cards = None
            default = None
        messages.add_message(request, messages.INFO, 'Pet added successfully')
        if request.POST.get("book_add_pet"):
            dates  = datetime.strptime(request.POST.get("book_add_pet_date"), "%d/%m/%Y")
            selected_date = dates.strftime("%Y-%m-%d")
            data_obtain = request.POST.get("book_add_pet_user")
            user_id = data_obtain.split(",")[0]
            user = User.objects.get(id=user_id)
            pets = Pets.objects.filter(created_by = request.user)
            if request.POST.get("custom_id"):
                return redirect(reverse('enduser:bookings') + '?user_id='+str(user_id) +','+selected_date+','+ request.POST.get("local_time_zone")+',&custom_id='+request.POST.get("custom_id"))
            else:
                return redirect(reverse('enduser:bookings') + '?user_id='+str(user_id) +','+selected_date+','+request.POST.get("local_time_zone"))
        else:
            completed_jobs=Appointments.objects.filter(created_by=request.user,status=COMPLETED).count()
            return render(request, 'user/user-profile.html',{"default":default,"user":user,"nbar":"settings","user":user,"pets":pets,"cards":cards,"petTab":True,"completed_jobs":completed_jobs,"stripe_bank_accounts":stripe_bank_accounts,"BANK_ADD_URL":BANK_ADD_URL})


"""
Edit Pet
"""
@login_required
def Edit_pet(request,id):
    BANK_ADD_URL = env('BANK_ADD_URL')
    try:
        stripe_bank_accounts = stripe.Account.list_external_accounts(
            request.user.bank_account_id,
            object="bank_account",
            limit=1
        )
    except:
        stripe_bank_accounts = None
    if request.method == 'GET':
        pet = Pets.objects.get(id = id)
        pets = PetType.objects.all()
        return render(request , "user/edit-pet.html" , {"title":"Edit Pet", "nbar" : "settings","pet":pet,"pets":pets,"stripe_bank_accounts":stripe_bank_accounts})
    if request.method == 'POST':
        pet = Pets.objects.get(id = id)
        if pet:
            pet.name = request.POST.get('pet_name')
            pet.age = request.POST.get('pet_age')
            pet.size = request.POST.get('size')
            pet.breed = request.POST.get('pet_breed')
            pet.pet_gender = request.POST.get('pet_gender')
            pet.description = request.POST.get('about')
            pet.vet_name = request.POST.get('vet_name')
            pet.vet_email = request.POST.get('vet_email')
            pet.vet_number = request.POST.get('vet_number')
            pet.vet_adrress = request.POST.get('vet_address')
            pet.vaccines = request.POST.get('vaccines')
            pet.save()
            user = User.objects.get(id = request.user.id)
            pets = Pets.objects.filter(created_by = request.user).order_by("-id")
        if request.FILES.getlist("pet_image",None):
            image = request.FILES.getlist("pet_image",None)
            pet_image = Pets.image.through.objects.filter(pets_id = pet.id)
            if pet_image:
                pet_image.delete()
            images=[]
            for img in image:
                images.append(Images.objects.create(
                    file = img,
                    created_by = request.user
                ))
            if image:
                pet.image.set(images)
                pet.save()
            for img in image:
                pet.image.set = img
        pet.pet_type =  PetType.objects.get(id=request.POST.get('pet_type'))
        pet.save()
        try:
            cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
            customer = stripe.Customer.retrieve(request.user.customer_id)
            default = customer.default_source
        except:
            cards = None
            default = None
        messages.add_message(request, messages.INFO, 'Pet updated successfully')
        completed_jobs=Appointments.objects.filter(created_by=request.user,status=COMPLETED).count()
        return render(request, 'user/user-profile.html',{"default":default,"user":user,"nbar":"settings","pets":pets,"cards":cards,"petTab":True,"completed_jobs":completed_jobs,"stripe_bank_accounts":stripe_bank_accounts,"BANK_ADD_URL":BANK_ADD_URL})


"""
User Pet Profile
"""
@login_required
def UserPetProfile(request,id):
    pet_details=request.GET.get('details')
    pet = Pets.objects.get(id = id)
    appointments = Appointments.objects.filter(created_by = request.user).order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(appointments, 10)
    try:
        appointments = paginator.page(page)
    except PageNotAnInteger:
        appointments = paginator.page(1)
    except EmptyPage:
        appointments = paginator.page(paginator.num_pages)
    return render(request , "user/pet-profile.html" , {"title":"Pet Profile", "nbar" : "pet_profile","pet":pet,"appointments":appointments,"pet_details":pet_details})


"""
Remove Pet
"""
@login_required
def Remove_pet(request):
    BANK_ADD_URL = env('BANK_ADD_URL')
    try:
        stripe_bank_accounts = stripe.Account.list_external_accounts(
            request.user.bank_account_id,
            object="bank_account",
            limit=1
        )
    except:
        stripe_bank_accounts = None
    completed_jobs=Appointments.objects.filter(created_by=request.user,status=COMPLETED).count()
    try:
        pet = Pets.objects.get(id = request.GET.get("id")).delete()
    except:
        pet = None
    user = User.objects.get(id = request.user.id)
    pets = Pets.objects.filter(created_by = request.user).order_by("-created_on")
    try:
        cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
        customer = stripe.Customer.retrieve(request.user.customer_id)
        default = customer.default_source
    except:
        cards = None
        default = None
    return render(request, 'user/user-profile.html',{"default":default,"user":user,"nbar":"settings","user":user,"pets":pets,"cards":cards,"petTab":True,"completed_jobs":completed_jobs,"stripe_bank_accounts":stripe_bank_accounts,"BANK_ADD_URL":BANK_ADD_URL})


"""
User Appointment request
"""
@login_required
def UserAppointmentRequest(request):
    return render(request , "user/user-appointment-request.html" , {"title":"Booking Details", "nbar" : "user_appointment_request"})


"""
User Choose Service
"""
def UserChooseService(request):
    return render(request , "user/choose-service.html" , {"title":"Choose Time and Service", "nbar" : "user_choose_service"})


"""
users list
"""
@login_required
def USERChat(request):
    connectId = []        
    frndidArray = {} 
    last_chatings = Chating.objects.filter(
        Q(sender = request.user)|
        Q(receiver_id = request.user)
    )

    for i in last_chatings:        
        if request.user.id != i.sender_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.sender_id
            frndidArray[i.id] = i.receiver_id

        if request.user.id != i.receiver_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.receiver_id
    x = []
    my_list = sorted(set(frndidArray))
    for frndid in my_list:

        last_message = Message.objects.filter(chat_id = frndid).order_by('-id')[:1]
        for i in last_message:
            x.append(i.id)

    last_message = Message.objects.filter(id__in = x).order_by("-id")
    return render(request , "user/user-chat.html" , {"title":"Inbox", "nbar" : "user_chat" ,"last_message":last_message})


"""
ajax-update new message
"""
@login_required
def ajax_load_get_group_messages_singer(request, id):
    user = User.objects.get(id = request.user.id)
    chating = Chating.objects.filter(Q(sender_id = user.id,receiver_id = id)|Q(sender_id = id,receiver = user.id)).values_list("id",flat=True)
    messages = Message.objects.filter(Q(receiver_id=id, sender_id=request.user,seen=0,sender_seen=True) |Q(receiver_id=request.user, sender_id=id,seen=0,sender_seen=True))

    for msg in messages:
        message_image = Message.images.through.objects.filter(message_id = msg.id).values_list("chatimage_id",flat=True)
        image = ChatImage.objects.filter(id__in = message_image).last()
    try:
        if image:
            image = image.images.url
        else:
            image = ''
    except:
        pass

    message_list = [{
        "sender": message.sender.username,
        "image" : image,
        "sender_image":message.sender.profile_pic.url if message.sender.profile_pic else "",
        "sender_id": message.sender.id,
        "message": message.message,
        "sent": message.sender == request.user,
        "sender_seen":message.sender_seen,
        "seen":message.seen,
        "current_user":user.id,
        "receiver": id,

    } for message in messages]
    return JsonResponse(message_list, safe=False)


"""
enduser chat sscreen with Rvt's
"""
@login_required
def UserChatWindow(request):
    connectId = []        
    frndidArray = {} 
    to = User.objects.get(id = request.GET.get("id"))
    chatings = Chating.objects.filter(
        Q(sender = request.user,receiver_id = to.id)|
        Q(receiver_id = request.user,sender_id = to.id)
    )

    all_message = Message.objects.filter(chat_id__in =  chatings)
    final_all_message = Message.objects.filter(chat_id__in =  chatings).values_list("id",flat=True)

    message_image = Message.images.through.objects.filter(message_id__in = final_all_message).values_list("chatimage_id",flat=True)
    image = ChatImage.objects.filter(id__in = message_image)[:10]
  
    
    last_chatings = Chating.objects.filter(
        Q(sender = request.user)|
        Q(receiver_id = request.user)
    )

    for i in last_chatings:        
        if request.user.id != i.sender_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.sender_id
            frndidArray[i.id] = i.receiver_id

        if request.user.id != i.receiver_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.receiver_id
    x = []
    my_list = sorted(set(frndidArray))
    for frndid in my_list:

        last_message = Message.objects.filter(chat_id = frndid).order_by('-id')[:1]
        for i in last_message:
            x.append(i.id)
    last_message = Message.objects.filter(id__in = x).order_by("-id")

    recipient_id = to.id
    sender_id = request.user.id
    
    shared_appointments = Appointments.objects.filter(
        Q(created_by__id = sender_id,created_for__id = recipient_id)|
        Q(created_for__id = sender_id,created_by__id = recipient_id)
    )

    return render(request , 'user/user-chat-window.html',{"mesaage_to":to.username,"to":to,"all_message":all_message,"image":image,"last_message":last_message,"image":image,"nbar" : "user_chat", "shared_appointments":shared_appointments})



@login_required
def SendMessageUser(request):
    user = User.objects.get(id = request.user.id)
    to = User.objects.get(id = request.POST.get('id'))

    try:
        chating = Chating.objects.get(Q(sender_id = user.id,receiver_id = to.id)|Q(sender_id = to.id,receiver = user.id))
    except Chating.DoesNotExist:
        chating = Chating.objects.create(sender = user,receiver_id = to.id)
    if request.POST.get("message") == '':
        pass
    if request.FILES.get("image"):
        message1 = Message.objects.create(
            sender = user,
            receiver = to,
            chat = chating,
            image = request.FILES.get("image"),
            seen=0,
            sender_seen=True
        )
    if request.POST.get("message"):
        message1 = Message.objects.create(
            sender = user,
            receiver = to,
            chat = chating,
            message = request.POST.get("message"),
            seen=0,
            sender_seen=True
        )
    if request.user.role_id == RVT_LVT:
        return redirect('chat:user_chat', to.id )
    else:
        return redirect('enduser:users_chat_screen', to.id )


def SendMessageRvt(request):
    if request.is_ajax():
        data = {}
        user = User.objects.get(id = request.user.id)
        to = User.objects.get(id = request.POST.get('id'))
        try:
            chating = Chating.objects.get(
                Q(sender_id = user.id, receiver_id = to.id)|Q(receiver_id = user.id, sender_id = to.id)
            )
        except Chating.DoesNotExist:
            chating = Chating.objects.create(sender_id = user.id,receiver_id = to.id)

        if request.FILES.get("image"):
            images = []
            message = Message.objects.create(
                sender = user,
                receiver = to,
                chat = chating,
                sender_seen = True
            )
            images.append(ChatImage.objects.create(images = request.FILES.get("image")))
            if images:
                for image in images:
                    message.images.add(image.id)

        elif request.POST.get('message'):
            message = Message.objects.create(
                sender = user,
                receiver = to,
                chat = chating,
                message = request.POST.get("message"),
                sender_seen = True
            )
            chating.save()
        return JsonResponse(data,safe=False)

"""
new message
"""
@login_required
def singer_ajax_load_group_messages_update(request,rid):
    user = User.objects.get(id = request.user.id)
    chating = Chating.objects.filter(Q(sender_id = user.id,receiver_id = rid)|Q(sender_id = rid,receiver = user.id)).values_list("id",flat=True)
    msgs = Message.objects.filter(receiver_id = user.id,sender_id = rid,chat_id__in = chating,seen = 0)
    msgs.update(seen = 1)
    return JsonResponse([],safe=False)


"""
activate -inactive rvt status
"""
@login_required
def UserStatusChange(request):
    if request.method == 'GET':
        user = User.objects.get(id = request.GET.get("user_id"))
    else:
        user = User.objects.get(id = request.POST.get("user_id"))
    if not user.status:
        user.status = True
        user.state_id = ACTIVE
        user.save()
        messages.add_message(request, messages.INFO, 'Account Activated Successfully!')
    elif user.status:
        user.status = False
        user.state_id = INACTIVE
        user.save()
        Session.objects.filter(session_key = user.session_id).delete()
        messages.add_message(request, messages.INFO, 'Account Deactivated Successfully!')
    if request.GET.get("user_id"):
        return redirect(reverse('superuser:edit_user_info',) + '?user='+str(user.id))
    else:
        return redirect('enduser:user_profile')


"""
Add Card for User
"""
@login_required
def AddCard(request):
    BANK_ADD_URL = env('BANK_ADD_URL')
    try:
        stripe_bank_accounts = stripe.Account.list_external_accounts(
            request.user.bank_account_id,
            object="bank_account",
            limit=1
        )
    except:
        stripe_bank_accounts = None
    if request.method=="POST":
        if Card.objects.filter(ac_no = request.POST.get('ac_no')):
            messages.error(request, 'Card number already exist')
            return redirect("enduser:user_profile")
        combine = request.POST.get("expire_date")
        month , year = combine.split("/")
        completed_jobs=Appointments.objects.filter(created_by=request.user,status=COMPLETED).count()
        try:
            stripe_customer=stripe.Token.create(
                card={
                    "number": request.POST.get('ac_no'),
                    "exp_month": int(month),
                    "exp_year": int(year),
                    "cvc": request.POST.get('cvv'),
                    "name":request.POST.get('card_holder_name')
                },
            )
            stripe.Customer.create_source(request.user.customer_id,source=stripe_customer.id)
            messages.error(request, 'Card added successfully!')
        except Exception as e:
            messages.add_message(request, messages.INFO, str(e).split(':')[1])
        user = User.objects.get(id = request.user.id)
        pets = Pets.objects.filter(created_by = request.user).order_by("-created_on")
        try:
            cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
            customer = stripe.Customer.retrieve(request.user.customer_id)
            default = customer.default_source
        except:
            cards = None
            default = None
        return render(request, 'user/user-profile.html',{"default":default,"user":user,"nbar":"settings","user":user,"pets":pets,"cards":cards,"secondTab":True,"completed_jobs":completed_jobs,"stripe_bank_accounts":stripe_bank_accounts,"BANK_ADD_URL":BANK_ADD_URL})

"""
Delete User card
"""
@login_required
def Delete_Card(request):
    BANK_ADD_URL = env('BANK_ADD_URL')
    try:
        stripe_bank_accounts = stripe.Account.list_external_accounts(
            request.user.bank_account_id,
            object="bank_account",
            limit=1
        )
    except:
        stripe_bank_accounts = None
    user = User.objects.get(id = request.user.id)
    stripe.Customer.delete_source(user.customer_id,request.GET.get('card_id'))
    messages.add_message(request, messages.INFO, 'Card deleted successfully')
    user = User.objects.get(id = request.user.id)
    pets = Pets.objects.filter(created_by = request.user).order_by("-created_on")
    completed_jobs=Appointments.objects.filter(created_by=request.user,status=COMPLETED).count()
    try:
        cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
        customer = stripe.Customer.retrieve(request.user.customer_id)
        default = customer.default_source
    except:
        cards = None
        default = None
    return render(request, 'user/user-profile.html',{"default":default,"user":user,"nbar":"settings","user":user,"pets":pets,"cards":cards,"secondTab":True,"completed_jobs":completed_jobs,"stripe_bank_accounts":stripe_bank_accounts,"BANK_ADD_URL":BANK_ADD_URL})


"""
My appointment Calendar
"""
@login_required
def MyAppointmentsCalander(request):
    appointments = Appointments.objects.filter(created_by = request.user)
    data={"date":[]}
    for i in appointments:
        app_date=datetime.strptime(str(i.date), '%Y-%m-%d').strftime('%d-%m-%Y')
        data['date'].append(app_date)
    return JsonResponse(data,safe=False)


"""
Delete Appointment
"""
@login_required
def Deleteappointment(request,id):
    appointment =Appointments.objects.get(id = id)
    if appointment:
        appointment.delete()
        return redirect('enduser:user_dashboard')


"""
My appointment
"""
def MyAppointment(request):
    if request.user.is_authenticated:
        service_list,date,app_id = [],[],[]
        appointment = Appointments.objects.filter(created_by = request.user).order_by('-id')
        if request.GET.get('reset') == "reset":
                return redirect("enduser:user_appointments")
        if request.GET.get("name"):
            appointment = appointment.filter(created_by = request.user,created_for__first_name__icontains = request.GET.get("name"))
        if request.GET.get("service"):
            if not 'CUS-' in request.GET.get('service'):
                service_cat = ServiceCategory.objects.filter(id = request.GET.get('service')).values_list("id",flat=True)
                service = Services.objects.filter(category_id__in = service_cat).values_list("id",flat=True)
                service_appointments = Appointments.service.through.objects.filter(services_id__in =service).values_list('appointments_id',flat = True)
                appointment = appointment.filter(id__in=service_appointments)
            else:
                custom = CustomService.objects.filter(service_id = request.GET.get("service")).values_list("id",flat=True) 
                custom_appointments = Appointments.custom.through.objects.filter(customservice_id__in =custom).values_list('appointments_id',flat = True)
                appointment = appointment.filter(id__in=custom_appointments) 
        
        if request.GET.get("month"):
            appointment = appointment.filter(created_by_id = request.user,date__month = request.GET.get('month')) 
        
        if request.GET.get("status"):
            appointment = appointment.filter(created_by = request.user,status = request.GET.get('status')).order_by('-id')
        
        for appoint in appointment.exclude(status=CANCELLED):
            date.append(appoint.date)
            app_id.append(appoint.id)
            services = []
            customservices = Appointments.custom.through.objects.filter(appointments_id = appoint.id).values_list("customservice_id",flat=True)
            [services.append(i.title + '('+ i.pet_type.name +')') for i in CustomService.objects.filter(id__in=customservices)]
            allservices = Appointments.service.through.objects.filter(appointments_id = appoint.id).values_list("services_id",flat=True)
            [services.append(i.category.title + '('+ i.pet.name +')') for i in Services.objects.filter(id__in=allservices)]
            service_list.append(", ". join(services))
        calender_data = zip(service_list,date,app_id)
        service_category = Appointments.objects.filter(created_by = request.user ).values_list('service__category_id', flat=True).distinct()
        cus_service_title = Appointments.objects.filter(created_by = request.user ).values_list('custom__id', flat=True).distinct()
        cus_service_title = Appointments.custom.through.objects.filter(customservice_id__in =cus_service_title).values_list("customservice_id",flat=True)
        c_serivice = CustomService.objects.filter(id__in =cus_service_title )
        catgory = ServiceCategory.objects.filter(id__in = service_category)
        user_cust_service = CustomService.objects.filter(created_by = request.user, is_appointment = PENDING).order_by('-created_on')
        appointments = Appointments.objects.filter(created_by = request.user ).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(appointments, 10)
        try:
            appointments = paginator.page(page)
        except PageNotAnInteger:
            appointments = paginator.page(1)
        except EmptyPage:
            appointments = paginator.page(paginator.num_pages)
        try:
            service_id = int(request.GET.get("service")) if request.GET.get("service") else ""
        except:
            service_id = request.GET.get("service")
        return render(request , 'user/my-appointments.html',{"title":"My Appointments","custom_appointment":"custom_appointment","nbar" : "user_my_appointments","appointments":appointments,"service_category":catgory,"custom_service":user_cust_service,"calender_data":calender_data,"cus_service_title":c_serivice,"name":request.GET.get("name"),"month":request.GET.get("month"),"status":request.GET.get("status"),"service":service_id})
    else:
        return redirect('accounts:web_login')

@login_required
def MyCustomRequests(request):
    custom_requests = CustomService.objects.filter(created_by=request.user)
    return render(request , 'user/user-custom-requests.html', {"nbar" : "user_custom_requests", "custom_requests": custom_requests})


"""
Appointment model
"""
@login_required
def AppointmentModal(request):
    app_id= request.GET.get("app_id")
    appoint = Appointments.objects.get(id=app_id)
    data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services":[], "phone":[], "app_id":[]}
    services = []
    customservices = Appointments.custom.through.objects.filter(appointments_id = appoint.id).values_list("customservice_id",flat=True)
    [services.append(i.title + '('+ i.pet_type.name +')') for i in CustomService.objects.filter(id__in=customservices)]
    allservices = Appointments.service.through.objects.filter(appointments_id = appoint.id).values_list("services_id",flat=True)
    [services.append(i.category.title + '('+ i.pet.name +')') for i in Services.objects.filter(id__in=allservices)]
    data["services"] = ", ". join(services)
    data["name"].append(appoint.created_for.first_name)
    data["date"].append(appoint.date)
    data["start_time"].append(appoint.start_time)
    data["end_time"].append(appoint.end_time)
    data["location"].append(appoint.created_for.address)
    data["amount"].append(appoint.amount)
    data["phone"].append(appoint.created_for.mobile_no)
    data["app_id"].append(appoint.id)
    return JsonResponse(data)
    

"""
View appoint from modal
"""
@login_required
def ViewAppoints(request):
    appointment = Appointments.objects.get(id = request.GET.get('id'))   
    appointment_services = Appointments.service.through.objects.filter(appointments_id = appointment).values_list("services_id",flat=True)
    appointment_pet = Appointments.pet.through.objects.filter(appointments_id = appointment).values_list("pets_id",flat=True)
    service = Services.objects.filter(id__in = appointment_services)
    pet = Pets.objects.filter(id__in = appointment_pet)
    notes = Notes.objects.filter(appointment_id = request.GET.get('id'),type = PUBLIC)
    return render(request , "rvt/appointment-details.html" , {"title":"Appointment Details", "nbar" : "rvt_my_appointments","appointment":appointment,"service":service,"pets":pet,"notes":notes})
    

@login_required
def CheckAvailabilityApp(request):
    data ={"is_exist":"false"}
   
    services = ServiceAvailability.objects.filter(user =request.GET.get('user_id'), id = request.GET.get('slot_id'))
    for s in services:
        availability = Appointments.objects.filter(date = request.GET.get('slot_date'),created_for = request.GET.get('user_id'),start_time =s.start_time, end_time = s.end_time )
        if availability :
            data["is_exist"] = "true"
        else:
            data["is_exist"] = "false"
            messages.add_message(request, messages.INFO, 'Appointment created')
        return JsonResponse(data)
    

"""
appointment details
"""
@login_required
def UserAppointmentDetails(request):
    try:
        appointment = Appointments.objects.get(id = request.GET.get('id'),created_by = request.user)
        appointment_services = Appointments.service.through.objects.filter(appointments_id = appointment).values_list("services_id",flat=True)
        appointment_pet = Appointments.pet.through.objects.filter(appointments_id = appointment).values_list("pets_id",flat=True)
        service = Services.objects.filter(id__in = appointment_services)
        appointment_custom_services = Appointments.custom.through.objects.filter(appointments_id = appointment).values_list("customservice_id",flat=True)
        rvt_cus_service = CustomService.objects.filter(id__in = appointment_custom_services,created_by = appointment.created_for)
        pet = Pets.objects.filter(id__in = appointment_pet)
        notes = Notes.objects.filter(appointment_id = appointment,type = PUBLIC )
        app_custom_services = Appointments.custom.through.objects.filter(appointments_id = appointment).values_list("customservice_id",flat=True)
        cus_service = CustomService.objects.filter(id__in= app_custom_services, created_by = appointment.created_by)
        rating = Rating.objects.filter(appointment=appointment, created_for=appointment.created_for)
        time, distance, distance_km=get_distance_from_coordinates(appointment.created_for.latitude,appointment.created_for.longitude,appointment.created_by.latitude,appointment.created_by.longitude)
        return render(request , "user/appointment-details.html" , {"nbar" : "user_my_appointments","title":"Appointment Details","appointment":appointment,"service":service,"pets":pet,"notes":notes,"cus_service":cus_service,"rvt_cus_service":rvt_cus_service,"distance":distance,"time":time,"rating":rating})
    except:
        return render(request, 'frontend/500.html')


"""
Applicants details
"""
@login_required
def ApplicantsDetails(request):
    user = Applied_by.objects.filter(custom_id__service_id =request.GET.get('id')).values_list('applied_by',flat=True)
    service_id = request.GET.get('id')
    applied_by= Applied_by.objects.filter(applied_by__in =user,custom_id__service_id =request.GET.get('id'))
    service = Services.objects.filter(created_by__in = user)
    applied_rvt = CustomService.objects.filter(service_id =request.GET.get('id')).values_list('assigend_to_id',flat=True)
    applied_rvt = CustomService.objects.filter(assigend_to_id__in = applied_rvt)[:10]
    description = CustomService.objects.filter(service_id =request.GET.get('id'))
    return render(request,'user/user-appointment-request.html',{"title":"Applications For Custom Request","applied_by":applied_by,"rvt_service":service,"applied_rvt":applied_rvt,"description":description, "service_id": service_id })


"""
#Accept RVT request
"""
@login_required
def AcceptRvt(request):
    data = {"id":[],"start_time":[], "end_time":[], "date":[], 'user_id':[]}
    availability= ServiceAvailability.objects.filter(user=request.GET.get('user_id'),date=request.GET.get('custom_date'))
    for avail in availability:
        data['id'].append(avail.id)
        data['start_time'].append(avail.start_time)
        data['end_time'].append(avail.end_time)
        data['date'].append(avail.date)
        data['user_id'].append(avail.user.id)
    return JsonResponse(data,safe=False)   


"""
#Reject Rvt request
"""
@login_required
def RejectRvt(request):
    ids=request.GET.get("user_id")
    ids=ids.split(',')
    id=ids[0]
    cus_id=ids[1]
    customs_id = CustomService.objects.get(service_id=cus_id)
    applied_by = Applied_by.objects.get(applied_by = id,custom_id=customs_id.id)
    users=User.objects.get(id=request.user.id)
    custom_service = CustomService.objects.get(id=applied_by.custom_id.id)
    if custom_service:
        custom_service.is_rejected_id = id
        custom_service.save()
        messages.add_message(request, messages.INFO, 'You have Rejected the application.')
    apply = Applied_by.objects.get(applied_by_id =id, custom_id__service_id =cus_id)
    apply.status = REJECTED
    apply.save()
    if apply.applied_by.is_email:
        current_site = get_current_site(request)
        context = {
            'domain':current_site.domain,
            'site_name': current_site.name,
            'protocol': 'https' if USE_HTTPS else 'http',
            'name':apply.applied_by.first_name,
            'user':users.first_name
        }
        message = render_to_string('user/reject_rvt_mail.html', context)
        mail_subject = 'Application  Rejected'
        to_email =  apply.applied_by.email
        email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
        html_email = render_to_string('user/reject_rvt_mail.html',context)
        email_message.attach_alternative(html_email, 'text/html')
        email_message.send()
    user = Applied_by.objects.filter(custom_id__service_id =cus_id).values_list('applied_by',flat=True)
    applied_by= Applied_by.objects.filter(applied_by__in =user,custom_id__service_id =cus_id)
    service = Services.objects.filter(created_by__in = user)
    applied_rvt = CustomService.objects.filter(service_id =cus_id).values_list('assigend_to_id',flat=True)
    applied_rvt = CustomService.objects.filter(assigend_to_id__in = applied_rvt)[:10]
    description = CustomService.objects.filter(service_id =cus_id)
    return render(request,'user/user-appointment-request.html',{"title":"Applications For Custom Request","applied_by":applied_by,"rvt_service":service,"applied_rvt":applied_rvt,"description":description})


@login_required
def CustomAppointment(request):
    try:
        availability= ServiceAvailability.objects.get(id =request.POST.get('time_slot'))
    except:
        messages.error(request, 'Please choose time slot.')
        return redirect('enduser:applicants_details')
    c_s = CustomService.objects.get(service_id = request.POST.get("cust_id"))
    assigned_to = Applied_by.objects.get(applied_by_id = request.POST.get("user_id"),custom_id=c_s.id)
    custom_service = CustomService.objects.get(id=assigned_to.custom_id.id)
    if custom_service:
        custom_service.assigend_to_id = request.POST.get("user_id")
        custom_service.is_appointment = ACCEPT
        custom_service.save()
    user = User.objects.get(id =request.POST.get("user_id"))
    app = Appointments.objects.create(
        created_by = request.user,
        created_for = user,
        description = custom_service.description,
        date = custom_service.date,
        start_time = availability.start_time,
        end_time = availability.end_time,
        address = custom_service.location,
        custom_title = custom_service.title,
        timezone = convert_timezone_to_short_form(availability.rvt_timezone)
    )
    app.custom.add(custom_service.id)
    
    if assigned_to.applied_by.is_email:
        current_site = get_current_site(request)
        context = {
            'domain':current_site.domain,
            'site_name': current_site.name,
            'protocol': 'https' if USE_HTTPS else 'http',
            'name':app.created_for.first_name,
            'user':app.created_by.first_name,
            'start_time':app.start_time,
            'end_time':app.end_time,
            'date':app.date
        }
        message = render_to_string('user/accept_rvt_mail.html', context)
        mail_subject = 'Application  Accepted'
        to_email =  app.created_for.email
        email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
        html_email = render_to_string('user/accept_rvt_mail.html',context)
        email_message.attach_alternative(html_email, 'text/html')
        email_message.send()
    if assigned_to.applied_by.is_push:
        Notification.objects.create(
            title = "Appointment Confirmed",
            description = "Your appointment is confirmed with {}".format(request.user.first_name),
            created_for=assigned_to.applied_by,
            created_by = request.user,
            appointment = app
        )
    return redirect('enduser:user_appointments')


"""
#Hide Custom row
"""
def HideCustomRow(request):
    data ={"appointmnet":"true"}
    appointment = Appointments.custom.through.objects.filter(customservice_id__service_id= request.GET.get('cus_id'))
    if appointment:
        data['appointmnet']='true'
    return JsonResponse(data)
    

"""
Search User filter
"""
@login_required
def Searchuser(request):
    if request.is_ajax():
        if request.GET.get("search_user") == '':
            data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services" :[],"custom" :[],"image":[],"id":[],"status":[]}
            custom={"un-assigned": "Un-assigned","title":[],"user-service-date":[],"user-service-location":[],"cus_id":[]}
            users = Appointments.objects.filter(created_by = request.user).order_by('-id')
            user_custom_service = CustomService.objects.filter(created_by = request.user,is_appointment = PENDING).order_by('-created_on')

            service_list = ""
            custom_service_list = ""
            for user in users:
                service_list = ""
                custom_service_list = ""
                app_service = Appointments.service.through.objects.filter(appointments_id = user.id)
                for service in app_service:
                    service_list += service.services.category.title+"<br>"
                custom_service = Appointments.custom.through.objects.filter(appointments_id = user.id )
                for service in custom_service:
                    custom_service_list += service.customservice.title+"<br>"
                data["name"].append(user.created_for.first_name)
                data["date"].append(user.date)
                data["start_time"].append(user.start_time)
                data["end_time"].append(user.end_time)
                data["location"].append(user.created_for.address)
                data["amount"].append(user.amount)
                data["services"].append(service_list[:-1])
                data["custom"].append(custom_service_list)
                data["id"].append(user.id)
                data["status"].append(user.status)
                if user.created_for.profile_pic:
                    data["image"].append(user.created_for.profile_pic.url)
                else:
                    data["image"].append('/static/admin-assets/images/default.png')
            for user_custom in user_custom_service:
                custom["title"].append(user_custom.title)
                custom["user-service-date"].append(user_custom.date)
                custom["user-service-location"].append(user_custom.location)
                custom["cus_id"].append(user_custom.service_id)
            return JsonResponse({"data":data,"custom":custom},safe=False)

        elif request.GET.get("search_user"):
            data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services" :[],"custom" :[],"image":[],"id":[],"status":[],}
            custom={"un-assigned": "Un-assigned","title":[],"user-service-date":[],"user-service-location":[],"cus_id":[]}
            users = Appointments.objects.filter(created_by = request.user,created_for__first_name__icontains = request.GET.get("search_user")).order_by('-id')
            user_custom_service = CustomService.objects.filter(created_by = request.user,is_appointment = PENDING).order_by('-created_on')
   
            service_list = ""
            custom_service_list = ""
            for user in users:
                service_list = ""
                custom_service_list = ""
                app_service = Appointments.service.through.objects.filter(appointments_id = user.id)
                for service in app_service:
                    service_list += service.services.category.title+"<br>"
                custom_service = Appointments.custom.through.objects.filter(appointments_id = user.id )
                for service in custom_service:
                    custom_service_list += service.customservice.title+"<br>"
                data["name"].append(user.created_for.first_name)
                data["date"].append(user.date)
                data["start_time"].append(user.start_time)
                data["end_time"].append(user.end_time)
                data["location"].append(user.created_for.address)
                data["amount"].append(user.amount)
                data["services"].append(service_list[:-1])
                data["custom"].append(custom_service_list)
                data["id"].append(user.id)
                data["status"].append(user.status)
                if user.created_for.profile_pic:
                    data["image"].append(user.created_for.profile_pic.url)
                else:
                    data["image"].append('/static/admin-assets/images/default.png')
            for user_custom in user_custom_service:
                custom["title"].append(user_custom.title)
                custom["user-service-date"].append(user_custom.date)
                custom["user-service-location"].append(user_custom.location)
                custom["cus_id"].append(user_custom.service_id)
            return JsonResponse({"data":data,"custom":custom},safe=False)

"""
Status Filter
"""
def SearchByStatus(request):
    try:
        if request.GET.get('status') == "":
            users =Appointments.objects.filter(created_by = request.user).order_by('-id')
            user_custom_service = CustomService.objects.filter(created_by = request.user,is_appointment = PENDING).order_by('-created_on')

            data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services" :[],"custom" :[],"image":[],"id":[],"status":[]}
            custom={"un-assigned": "Un-assigned","title":[],"user-service-date":[],"user-service-location":[],"cus_id":[]}
            service_list = ""
            custom_service_list = ""
            for user in users:
                service_list = ""
                custom_service_list = ""
                app_service = Appointments.service.through.objects.filter(appointments_id = user.id)
                for service in app_service:
                    service_list += service.services.category.title+"<br>"
                custom_service = Appointments.custom.through.objects.filter(appointments_id = user.id )
                for service in custom_service:
                        custom_service_list += service.customservice.title+"<br>"
                data["name"].append(user.created_by.first_name)
                data["date"].append(user.date)
                data["start_time"].append(user.start_time)
                data["end_time"].append(user.end_time)
                data["location"].append(user.created_by.address)
                data["amount"].append(user.amount)
                data["services"].append(service_list[:-1])
                data["custom"].append(custom_service_list)
                data["id"].append(user.id)
                data["status"].append(user.status)
                if user.created_by.profile_pic:
                        data["image"].append(user.created_by.profile_pic.url)
                else:
                    data["image"].append('/static/admin-assets/images/default.png')

            for user_custom in user_custom_service:
                custom["title"].append(user_custom.title)
                custom["user-service-date"].append(user_custom.date)
                custom["user-service-location"].append(user_custom.location)
                custom["cus_id"].append(user_custom.service_id)
        return JsonResponse({"data":data,"custom":custom},safe=False)
        
    except:
        
        data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services" :[],"custom" :[],"image":[],"id":[],"status":[]}
        custom={"un-assigned": "Un-assigned","title":[],"user-service-date":[],"user-service-location":[],"cus_id":[]}
        users =Appointments.objects.filter(created_by = request.user,status = request.GET.get('status')).order_by('-id')
        user_custom_service = CustomService.objects.filter(created_by = request.user,is_appointment = PENDING).order_by('-created_on')
        service_list = ""
        custom_service_list = ""
        for user in users:
            service_list = ""
            custom_service_list = ""
            app_service = Appointments.service.through.objects.filter(appointments_id = user.id)
            for service in app_service:
                service_list += service.services.category.title+"<br>"
            custom_service = Appointments.custom.through.objects.filter(appointments_id = user.id )
            for service in custom_service:
                    custom_service_list += service.customservice.title+"<br>"
            data["name"].append(user.created_by.first_name)
            data["date"].append(user.date)
            data["start_time"].append(user.start_time)
            data["end_time"].append(user.end_time)
            data["location"].append(user.created_by.address)
            data["amount"].append(user.amount)
            data["services"].append(service_list[:-1])
            data["custom"].append(custom_service_list)
            data["id"].append(user.id)
            data["status"].append(user.status)
            if user.created_by.profile_pic:
                data["image"].append(user.created_by.profile_pic.url)
            else:
                data["image"].append('/static/admin-assets/images/default.png')
        for user_custom in user_custom_service:
                custom["title"].append(user_custom.title)
                custom["user-service-date"].append(user_custom.date)
                custom["user-service-location"].append(user_custom.location)
                custom["cus_id"].append(user_custom.service_id)
        return JsonResponse({"data":data,"custom":custom},safe=False)


"""
Month Filter
"""
def MonthFilter(request):
    try:
        users =Appointments.objects.filter(created_by_id = request.user,date__month = request.GET.get('month')).order_by('-id')  
        data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services" :[],"custom" :[],"image":[],"id":[],"status":[]}
        custom={"un-assigned": "Un-assigned","title":[],"user-service-date":[],"user-service-location":[],"cus_id":[]}
        user_custom_service = CustomService.objects.filter(created_by = request.user,is_appointment = PENDING).order_by('-created_on')

        service_list = ""
        custom_service_list = ""
        for user in users:
            service_list = ""
            custom_service_list = ""
            app_service = Appointments.service.through.objects.filter(appointments_id = user.id)
            for service in app_service:
                service_list += service.services.category.title+"<br>"
            custom_service = Appointments.custom.through.objects.filter(appointments_id = user.id )
            for service in custom_service:
                    custom_service_list += service.customservice.title+"<br>"
            data["name"].append(user.created_for.first_name)
            data["date"].append(user.date)
            data["start_time"].append(user.start_time)
            data["end_time"].append(user.end_time)
            data["location"].append(user.created_for.address)
            data["amount"].append(user.amount)
            data["services"].append(service_list[:-1])
            data["custom"].append(custom_service_list)
            data["id"].append(user.id)
            data["status"].append(user.status)
            if user.created_for.profile_pic:
                data["image"].append(user.created_for.profile_pic.url)
            else:
                data["image"].append('/static/admin-assets/images/default.png')

        for user_custom in user_custom_service:
                custom["title"].append(user_custom.title)
                custom["user-service-date"].append(user_custom.date)
                custom["user-service-location"].append(user_custom.location)
                custom["cus_id"].append(user_custom.service_id)
        return JsonResponse({"data":data,"custom":custom},safe=False)
    except:
        if request.GET.get('month') == "":
            users =Appointments.objects.filter(created_by_id = request.user).order_by('-id')
            data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services" :[],"custom" :[],"image":[],"id":[],"status":[]}
            custom={"un-assigned": "Un-assigned","title":[],"user-service-date":[],"user-service-location":[],"cus_id":[]}
            user_custom_service = CustomService.objects.filter(created_by = request.user,is_appointment = PENDING).order_by('-created_on')

            service_list = ""
            custom_service_list = ""
            for user in users:
                service_list = ""
                custom_service_list = ""

                app_service = Appointments.service.through.objects.filter(appointments_id = user.id)
                for service in app_service:
                    service_list += service.services.category.title+"<br>"
                custom_service = Appointments.custom.through.objects.filter(appointments_id = user.id )
                for service in custom_service:
                    custom_service_list += service.customservice.title+"<br>"
                data["name"].append(user.created_for.first_name)
                data["date"].append(user.date)
                data["start_time"].append(user.start_time)
                data["end_time"].append(user.end_time)
                data["location"].append(user.created_for.address)
                data["amount"].append(user.amount)
                data["services"].append(service_list[:-1])
                data["custom"].append(custom_service_list)
                data["id"].append(user.id)
                data["status"].append(user.status)
                if user.created_for.profile_pic:
                    data["image"].append(user.created_for.profile_pic.url)
                else:
                    data["image"].append('/static/admin-assets/images/default.png')
            for user_custom in user_custom_service:
                custom["title"].append(user_custom.title)
                custom["user-service-date"].append(user_custom.date)
                custom["user-service-location"].append(user_custom.location)
                custom["cus_id"].append(user_custom.service_id)
            return JsonResponse({"data":data,"custom":custom},safe=False)



"""
Search By Service Filter
"""
@login_required
def SearchByService(request):
      if request.GET.get("search_service") == "":
        users = Appointments.objects.filter(created_by = request.user).order_by('-id')
        data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services" :[],"custom" :[],"image":[],"id":[],"status":[]}
        custom={"un-assigned": "Un-assigned","title":[],"user-service-date":[],"user-service-location":[],"cus_id":[]}
        user_custom_service = CustomService.objects.filter(created_by = request.user,is_appointment = PENDING).order_by('-created_on')

        service_list = ""
        custom_service_list = ""
        for user in users:
            service_list = ""
            custom_service_list=""
            app_service = Appointments.service.through.objects.filter(appointments_id = user.id)
            for service in app_service:
                service_list += service.services.category.title+"<br>"
            custom_service = Appointments.custom.through.objects.filter(appointments_id = user.id )
            for service in custom_service:
                custom_service_list += service.customservice.title+"<br>"
            data["name"].append(user.created_for.first_name)
            data["date"].append(user.date)
            data["start_time"].append(user.start_time)
            data["end_time"].append(user.end_time)
            data["location"].append(user.created_for.address)
            data["amount"].append(user.amount)
            data["services"].append(service_list[:-1])
            data["custom"].append(custom_service_list)
            data["id"].append(user.id)
            data["status"].append(user.status)
            if user.created_for.profile_pic:
                data["image"].append(user.created_for.profile_pic.url)
            else:
                data["image"].append('/static/admin-assets/images/default.png')
        for user_custom in user_custom_service:
                custom["title"].append(user_custom.title)
                custom["user-service-date"].append(user_custom.date)
                custom["user-service-location"].append(user_custom.location)
                custom["cus_id"].append(user_custom.service_id)
        return JsonResponse({"data":data,"custom":custom},safe=False)

      elif request.GET.get("search_service"):
       
        users = Appointments.objects.filter(created_by = request.user).order_by('-id')
        try:
            app = Appointments.service.through.objects.filter(appointments_id__in = users).values_list('services_id',flat=True)
            ser = Services.objects.filter(id__in =app, category = request.GET.get("search_service") )
            appp = Appointments.service.through.objects.filter(services_id__in = ser).values_list('appointments_id',flat=True)
        except:
            app = Appointments.custom.through.objects.filter(appointments_id__in = users).values_list('customservice_id',flat=True)
            ser = CustomService.objects.filter(id__in =app, service_id = request.GET.get("search_service") )
            appp = Appointments.custom.through.objects.filter(customservice_id__in = ser).values_list('appointments_id',flat=True)
        users=Appointments.objects.filter(created_by = request.user,id__in =appp).order_by('-id')
        data = {"name" :[],"date" :[],"start_time" :[],"end_time": [],"location" :[],"amount" :[],"services" :[],"custom" :[],"image":[],"id":[],"status":[]}
        custom={"un-assigned": "Un-assigned","title":[],"user-service-date":[],"user-service-location":[],"cus_id":[]}
        user_custom_service = CustomService.objects.filter(created_by = request.user,is_appointment = PENDING).order_by('-created_on')

        service_list = ""
        custom_service_list = ""
        for user in users:
            service_list = ""
            custom_service_list = ""

            app_service = Appointments.service.through.objects.filter(appointments_id = user.id)
            for service in app_service:
                service_list += service.services.category.title+"<br>"
            custom_service = Appointments.custom.through.objects.filter(appointments_id = user.id )
            for service in custom_service:
                custom_service_list += service.customservice.title+"<br>" 
            data["name"].append(user.created_for.first_name)
            data["date"].append(user.date)
            data["start_time"].append(user.start_time)
            data["end_time"].append(user.end_time)
            data["location"].append(user.created_for.address)
            data["amount"].append(user.amount)
            data["services"].append(service_list[:-1])
            data["custom"].append(custom_service_list)
            data["id"].append(user.id)
            data["status"].append(user.status)
            if user.created_for.profile_pic:
                data["image"].append(user.created_for.profile_pic.url)
            else:
                data["image"].append('/static/admin-assets/images/default.png')
        for user_custom in user_custom_service:
                    custom["title"].append(user_custom.title)
                    custom["user-service-date"].append(user_custom.date)
                    custom["user-service-location"].append(user_custom.location)
                    custom["cus_id"].append(user_custom.service_id)
        return JsonResponse({"data":data,"custom":custom},safe=False)

"""
Custom Service Request
"""
@login_required
def CustomRequest(request):
    if request.method == 'POST':
        custom_service = CustomService.objects.create(
            title = request.POST.get('title'),
            description = request.POST.get('description'),
            location = request.POST.get('location'),
            city = request.POST.get('city'),
            state =  request.POST.get('state'),
            country = request.POST.get('country'),
            date= request.POST.get('input_date'),
            created_by = request.user,
            local_time_zone = request.POST.get('local_time_zone'),
        )
        if request.POST.get('latitude'):
            custom_service.latitude =request.POST.get('latitude')
        else:
            custom_service.latitude =request.user.latitude

        if request.POST.get('longitude'):
            custom_service.longitude = request.POST.get('longitude')
        else:
            custom_service.longitude = request.user.longitude
        
        # Locate Nearby RVTS and send email or text
        ##########################################
        user_list = []
        q=''
        for i in User.objects.raw('''
                    SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                    cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                    sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id=1 Having  distance < {3};  
                    '''.format(request.user.latitude,request.user.longitude,q,env('MILES_RADIUS'))):
            user = User.objects.get(id=i.id)
            if str(user.is_verified) == str(VERIFIED):
                user_list.append(i.id)
        rvt_users = User.objects.filter(id__in=user_list)

        
        cs_title = request.POST.get('title')
        cs_description = request.POST.get('description')
        cs_location = request.POST.get('location')
        cs_date = request.POST.get('input_date')
        cs_created_by = request.user
        cs_local_time_zone = request.POST.get('local_time_zone')
        user_timezone = request.POST.get('local_time_zone')

        for user in rvt_users:
            if user.is_text == 1:
                if user.mobile_no:
                    try:
                        send_twilio_message(env('TWILIO_NUMBER'), user.mobile_no, "New x Custom Request by {0} {1} for date {2} ({3}). Title: {4}, Description: {5}. Log in to the website and apply.".format(request.user.first_name,request.user.last_name, cs_date, user_timezone, cs_title,cs_description ))  
                        text_sent = True
                    except Exception as e:
                        error = e
                else:
                    error = "User is missing mobile number"
            if user.is_email:
                context = {
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'date': cs_date,
                    'timezone': user_timezone,
                    'title': cs_title,
                    'description': cs_description
                }
                message = render_to_string('registration/custom_request_email.html', context)
                mail_subject = 'x Nearby Custom Request'
                to_email =  user.email
                email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
                html_email = render_to_string('registration/custom_request_email.html',context)
                email_message.attach_alternative(html_email, 'text/html')
                email_message.send()
        # Nearby RVTs
        ##########################################

        pets = PetType.objects.get(id = request.POST.get('pet_type'))
        custom_service.pet_type_id = pets.id
        custom_service.save()         
               
    messages.error(request, 'Custom request submitted successfully')
        
    return redirect('enduser:user_dashboard')    



"""
Custom services display
"""
def custom_service_display(request):
    POST=CustomService.objects.all()
    return render(request,'rvt/index',{'opportunities':POST})

"""
My appointment
"""
@login_required
def RVTAailability(request):
    data = {"date" :[]}
    availability = ServiceAvailability.objects.filter(user = request.GET.get('user_id'))
    for i in availability:
        data["date"].append(i.date)
    return JsonResponse(data,safe=False)

class BookingsView(View):
    def get(self, request, *args, **kwargs):
        data_obtain = request.GET.get('user_id')
        selected_date = data_obtain.split(",")[1]
        user_id = data_obtain.split(",")[0]
        local_time = data_obtain.split(",")[2]
        local_tz = pytz.timezone("UTC")
        user = User.objects.get(id=user_id)
        rvt_timezone = ServiceAvailability.objects.filter(user=user).last().rvt_timezone
        if rvt_timezone:
            UTC_tz = pytz.timezone(rvt_timezone)
        else:
            UTC_tz = pytz.timezone('Asia/Calcutta')
        current_time = str(UTC_tz.normalize(local_tz.localize(datetime.now()).astimezone(UTC_tz))).split(".")[0]
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        cus_id = request.GET.get('custom_id')
        if '-' in selected_date:
            selected_date = datetime.strptime(str(selected_date), '%Y-%m-%d').date() 
        else:
            selected_date = datetime.strptime(str(selected_date), '%d/%m/%Y').date()  
        availability = ServiceAvailability.objects.filter(user=user,date=selected_date,end_date_time__gte=current_time)
        appointment_availabilty = Appointments.objects.filter(availability__isnull=False).values_list('availability_id',flat=True)
        if appointment_availabilty:
            availability = availability.exclude(id__in=appointment_availabilty)
        services = Services.objects.filter(created_by=user, is_active=True)
        custom_service = CustomService.objects.filter(created_by=user, is_active=True)
        pets = Pets.objects.filter(created_by = request.user).order_by('-created_on')
        try:
            cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
            customer = stripe.Customer.retrieve(request.user.customer_id)
            default = customer.default_source
        except:
            cards = None
            default = None
        if cus_id:
            return render(request , 'user/booking.html',{"default":default,"title":"Booking",'availability':availability,"services":services,"custom_service":custom_service,"pets":pets,"user":user, "selected_date":selected_date,"cus_id":cus_id,"rvt_timezone":rvt_timezone,"cards":cards})
        else:
            return render(request , 'user/booking.html',{"default":default, "title":"Booking",'availability':availability,"services":services,"custom_service":custom_service,"pets":pets,"user":user, "selected_date":selected_date,"rvt_timezone":rvt_timezone,"cards":cards})

"""
Add Pet
"""
@login_required
def Booking_AddPet(request):
    if request.method == 'GET':
        pet_type = PetType.objects.all().order_by('-created_on')
        user = User.objects.get(id = request.GET.get("user_id"))
        date = request.GET.get("date")
        dates  = datetime.strptime(request.GET.get("date"), "%Y-%m-%d")
        date = dates.strftime("%d/%m/%Y")
        custom_id=request.GET.get("cus_id")
        local_time_zone=request.GET.get("local_time_zone")
    
        return render(request , "user/book-add-pet.html" , {"title":"Add Pet", "nbar" : "settings","pet_type":pet_type,"user":user,"date":date,"custom_id":custom_id,"local_time_zone":local_time_zone})


"""
RVT availability Month wise
"""

def RVTavailabilityC(request):
    user_id = request.GET.get("user_id")
    selected = request.GET.get("selected")
    next = request.GET.get("next")

    data = {"date" :[]}
    availability = ServiceAvailability.objects.filter(user = user_id , date__gte= selected , date__lt = next )
    for i in availability:
        data["date"].append(i.date)

    return JsonResponse(data)

"""
Book RVT
"""
@login_required
def BookingRVT(request,id):
    user = User.objects.get(id=id)  
    if not request.POST.get('time_slot'):
        messages.error(request, 'Please choose the time slot')
    if not request.POST.get('pets'):
        messages.error(request, 'You have not choosen any pet')    
    service_availbility = ServiceAvailability.objects.get(user = user,id = request.POST.get('time_slot'))
    booking_timezone = request.POST.get('rvt_timezone')
    charge_id=None
    try:
        try:
            stripe_card = stripe.Customer.retrieve_source(request.user.customer_id,request.POST.get('card_value'))
            stripe_payment = stripe.Charge.create(
                amount = int(float(request.POST.get('total_amount')) * 100),
                currency = request.user.default_currency,
                card = stripe_card,
                customer = request.user.customer_id,
                description = "Appointment payment for RVT {0} {1} ({2})".format(service_availbility.user.first_name, service_availbility.user.last_name, service_availbility.user.email ),
            )
            charge_id = stripe_payment["id"]
        except:
            stripe_customer=stripe.Token.create(
                card = {
                    "number": request.POST.get('number'),
                    "exp_month": request.POST.get('month'),
                    "exp_year": request.POST.get('year'),
                    "cvc": request.POST.get('cvv'),
                    "name":user.email
                },
            )
            if request.POST.get('save_card'):
                stripe_card = stripe.Customer.create_source(request.user.customer_id,source=stripe_customer.id)
                stripe_payment = stripe.Charge.create(
                    amount = int(float(request.POST.get('total_amount')) * 100),
                    currency = request.user.default_currency,
                    card = stripe_card,
                    customer = request.user.customer_id,
                    description = "Appointment payment for RVT {0} {1} ({2})".format(service_availbility.user.first_name, service_availbility.user.last_name, service_availbility.user.email ),
                )
            else:
                stripe_payment = stripe.Charge.create(
                    amount = int(float(request.POST.get('total_amount')) * 100),
                    currency = request.user.default_currency,
                    source = stripe_customer.id ,
                    description = "Appointment payment for RVT {0} {1} ({2})".format(service_availbility.user.first_name, service_availbility.user.last_name, service_availbility.user.email ),
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
        messages.add_message(request, messages.INFO, str(e).split(':')[1])
        selected_date = service_availbility.date
        user_id = id
        selected_date = datetime.strptime(str(selected_date), '%Y-%m-%d').date() 
        user = User.objects.get(id=user_id)
        availability = ServiceAvailability.objects.filter(user=user,date=selected_date)
        services = Services.objects.filter(created_by=user, is_active=True)
        custom_service = CustomService.objects.filter(created_by=user, is_active=True)
        pets = Pets.objects.filter(created_by = request.user).order_by('-created_on')
        try:
            cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
            customer = stripe.Customer.retrieve(request.user.customer_id)
            default = customer.default_source
        except:
            cards = None
            default = None
        return render(request , 'user/booking.html',{"cards":cards,"default":default,'availability':availability,"services":services,"custom_service":custom_service,"pets":pets,"user":user, "selected_date":selected_date})

    tax_amount = round(float(request.POST.get('total_amount'))*float(request.POST.get('tax_percentage'))/100,2)
    data_obtain = request.GET.get('user_id')

    appointment = Appointments.objects.create(
            created_by = request.user,
            created_for = service_availbility.user,
            description = request.POST.get('booking_description'),
            date = service_availbility.date,
            start_time = service_availbility.start_time,
            end_time = service_availbility.end_time,
            amount = request.POST.get('total_amount'),
            actual_amount=request.POST.get('actual_amount'),
            tax_amount = request.POST.get('tax_percentage'),
            tax_percentage = request.POST.get('tax_percent'),
            mileage_fee = request.POST.get('mileage_fee'),
            mileage_rate = request.POST.get('mileage_rate'),
            availability = service_availbility,
            charge_id = charge_id,
            timezone = convert_timezone_to_short_form(booking_timezone)
    )
    ######################
    text_sent = False
    error = ""
    availability_timezone = convert_timezone_to_short_form(service_availbility.rvt_timezone)
    if service_availbility.user.is_text == 1:
        if service_availbility.user.mobile_no:
            try:
                send_twilio_message(env('TWILIO_NUMBER'), service_availbility.user.mobile_no, "New x Appointment Booking by {0} {1} for {2} from {3} to {4} ({5})".format(request.user.first_name,request.user.last_name, service_availbility.date, convert_time(service_availbility.start_time),convert_time(service_availbility.end_time), convert_timezone_to_short_form(booking_timezone)))  
                text_sent = True
            except Exception as e:
                error = e
        else:
            error = "User is missing mobile number"
    else:
        error = "User doesnt have text enabled"
        
    #####################        
    
    try:
        appointment.timezone = data_obtain.split(",")[2]
        appointment.save()
    except:
        pass
    try:
        custom = CustomService.objects.get(id=request.POST.get('custom_id'))
        if custom:
            custom.is_appointment=SCHEDULED
            custom.save()
    except:
        custom=None
    
    payout.appointment = appointment
    payout.save()
    transaction.appointment = appointment
    transaction.save()

    if request.POST.get('service',None):
        ser = request.POST.getlist('service')
        services = Services.objects.filter(id__in = ser, created_by_id =user)
        if services:
            appointment.service.set(services)


    if request.POST.get('custom_service',None):
                ser = request.POST.getlist('custom_service')
                services = CustomService.objects.filter(service_id__in = ser, created_by_id =user)
                if services:
                    appointment.custom.set(services)

    if request.POST.get('pets',None):
        pets = request.POST.getlist('pets')
        pets = Pets.objects.filter(id__in = pets, created_by_id =request.user.id)
        if pets:
            appointment.pet.set(pets)
    
    rvt_user=User.objects.get(id=appointment.created_for.id)
    if rvt_user.is_email: 
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
    if service_availbility.user.is_push:
        Notification.objects.create(
            title = "Appointment Confirmed",
            description = "Your appointment is confirmed with {}".format(request.user.first_name),
            created_for=service_availbility.user,
            created_by = request.user,
            appointment = appointment,
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
                data_message={"message_title" :msg['title'],"message_body" : msg['description'],"type" : msg['type']
            }) 
        except:
            pass 
    messages.add_message(request, messages.INFO, 'Appointment booked successfully')
    return redirect('enduser:user_appointments')

"""
Time slot 
"""
def AvailabilityCheck(request):
    data ={"is_exist":"false"}
    date = datetime.strptime(request.GET.get('date'), '%B %d, %Y')
    try:
        services = ServiceAvailability.objects.get(user =request.GET.get('user_id'), id = request.GET.get('id'))
    except:
        services=None
    try:
        availability = Appointments.objects.get(date = date,created_for = request.GET.get('user_id'),start_time =services.start_time, end_time = services.end_time,status = 1)
        if availability :
            data["is_exist"] = "true"
        else:
            data["is_exist"] = "false"
        return JsonResponse(data)
    except:
        services=None
        return JsonResponse(data)
    
"""
Selected Services
"""
def SelectedServices(request):
    ser = request.GET.getlist('service[]')
    custom = request.GET.getlist('custom[]')
    services = Services.objects.filter(id__in = ser)
    try:
        cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
    except:
        cards = None
    data = {"name" :[],"price" :[],"total" :[],"tax" :[],"tax_percent":[],"actual_amount" :[] , "mileage_fee":[], "distance": [], "mileage_rate":[] }
    card_data={"card_holder_name":[],"account_no":[],"card_token":[]}
    for ser_detail in services:
        data["name"].append(ser_detail.category.title + ' ('+ser_detail.pet.name+')')
        data["price"].append(ser_detail.price)
    custom_services = CustomService.objects.filter(service_id__in = custom)
    for ser_detail in custom_services:
        data["name"].append(ser_detail.title + ' ('+ser_detail.pet_type.name+')')
        data["price"].append(ser_detail.price)
    totals_amount = sum(float(t) for t in data["price"])
    data["actual_amount"].append(totals_amount)
    totals=format(totals_amount, '.2f')
    try:
        tax_percentage = Tax.objects.filter().last()
        tax_amount = (float(totals) * float(tax_percentage.tax_percentage)) / 100
        percent = tax_percentage.tax_percentage
    except:
        percent = 0
        tax_amount = 0
    data["tax"].append(tax_amount)
    data["tax_percent"].append(percent)
    charged_value = float(tax_amount)+ float(totals)
    if cards:
        for card in cards:
            card_data["card_holder_name"].append(card.name)
            card_data["account_no"].append(card.last4)
            card_data["card_token"].append(card.id)
    slat = 0
    slon = 0
    elat = request.user.latitude
    elon = request.user.longitude
    if(len(services) or len(custom_services) > 0):
        try:
            slat = services[0].created_by.latitude
            slon = services[0].created_by.longitude
        except:
            slat = custom_services[0].created_by.latitude
            slon = custom_services[0].created_by.longitude
        try:
            mileage = Mileage.objects.filter().last()
            mileage_rate = float(mileage.mileage_percentage)
        except:
            mileage_rate = 0
        time, distance ,distance_km = get_distance_from_coordinates(slat,slon,elat, elon)
        data["distance"].append(distance_km)

        #################################################################
        # check if any appointments are within one hour and scheduled or completed
        # ###############################################################
        availability_id=request.GET.get('availability_id')
        booking_user = request.user
        rvt_user = services[0].created_by
        try:
            availability=ServiceAvailability.objects.get(id=availability_id)
            start_date_time = availability.start_date_time
            end_date_time = availability.end_date_time
            appointment_date = start_date_time.date()

            same_day_appt = Appointments.objects.filter(created_by = booking_user, created_for = rvt_user, date=appointment_date).filter(~Q(status = CANCELLED))
            computed_start_date = datetime.combine(appointment_date, availability.start_time)
            computed_end_date = datetime.combine(appointment_date, availability.end_time)
            one_hour_before_start = computed_start_date-(timedelta(hours=1))
            one_hour_after_end = computed_end_date+(timedelta(hours=1))
            appt_last_hour = same_day_appt.filter(start_time__gte=one_hour_before_start, start_time__lt=computed_start_date ).order_by('-created_on')
            appt_next_hour = same_day_appt.filter(start_time__gte=computed_start_date, start_time__lt=one_hour_after_end ).order_by('-created_on')
            if appt_last_hour or appt_next_hour:
                data["mileage_rate"].append(0)
                data["mileage_fee"].append(0)
                charged_value += 0
            else:
                data["mileage_rate"].append(mileage_rate)
                data["mileage_fee"].append(mileage_rate * distance_km)
                charged_value += (mileage_rate * distance_km)
        except:
            data["mileage_rate"].append(0)
            data["mileage_fee"].append(0)
            charged_value += 0
    data["total"].append(round(float(charged_value),2))  
    return JsonResponse({"data":data,"card_data":card_data})


"""
Custom selected Services
"""
@login_required
def CustomSelectedServices(request):
    ser = request.GET.get('id')
    ser = ser.split(",")
    services = CustomService.objects.filter(id__in = ser)
    data = {"name" :[],"price" :[],"total" :[]}
    for ser_detail in services:
        data["name"].append(ser_detail.title)
        data["price"].append(ser_detail.price)
    total = sum(float(t) for t in data["price"])
    total=format(total, '.2f')
    try:
        tax_percentage = Tax.objects.filter().last()
        tax_amount = (float(total) * float(tax_percentage.tax_percentage)) / 100
    except:
        tax_amount = 0
    if tax_percentage:
        data["tax"].append(tax_percentage.tax_percentage)
        tax_amount = (float(total) * float(tax_percentage.tax_percentage)) / 100
        tax_value=(float(total)/float(total)*100) + float(tax_amount)
        data["total"].append(tax_value)

    return JsonResponse(data, safe =False)


"""
Mark Appointment Cancel
"""
@login_required
def CancelAppointment(request):
    appointment = Appointments.objects.get(id = request.GET.get('id'))
    appointment.status = CANCELLED
    appointment.cancel_remarks = request.POST.get('cancel_remarks')
    if appointment.created_for.is_push:
        Notification.objects.create(
            title = "Appointment Cancellation",
            description = "Your appointment is cancelled with {}".format(appointment.created_by.first_name),
            created_by =request.user,
            created_for_id=appointment.created_for.id,
            appointment=appointment
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
    mileage_fee = appointment.mileage_fee
    payout_object = Payouts.objects.filter(appointment=appointment).last()     
    if time_since_booking <= 1:
        refund_percentage = 100
    elif time_until_appointment_in_hours <= 12:
        refund_percentage = 0
    elif time_until_appointment_in_hours <24 and time_until_appointment_in_hours > 12:
        refund_percentage = 50
    elif time_until_appointment_in_hours >= 24:
        refund_percentage = 100
    refundamount = (float(payout_object.appointment.amount)-float(mileage_fee))*(refund_percentage/100)+float(mileage_fee)
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
            messages.add_message(request, messages.INFO, str(e).split(':')[1])
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
                "refundamount": refundamount
            }
            message = render_to_string('registration/booking_cancelled.html', context)
            mail_subject = 'Appointment Cancellation'
            to_email =  appointment.created_for.email
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            html_email = render_to_string('registration/booking_cancelled.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
        availability_timezone = convert_timezone_to_short_form(appointment.timezone)
        if appointment.created_for.is_text == 1:
            if appointment.created_for.mobile_no:
                try:
                    send_twilio_message(env('TWILIO_NUMBER'), appointment.created_for.mobile_no, "x Appointment Cancelation by {0} {1} for {2} from {3} to {4} ({5}) [{6}]".format(request.user.first_name,request.user.last_name, appointment.date, convert_time(appointment.start_time),convert_time(appointment.end_time), appointment.timezone, appointment.cancel_remarks))  
                    text_sent = True
                except Exception as e:
                    error = e
                    print (">>>> failed to send text with error {0}".format(e))

            else:
                error = ">>> User is missing mobile number"
        else:
            error = "User doesnt have text enabled"
        messages.add_message(request, messages.INFO, 'Appointment cancelled successfully. {0} refund will be processed to your account.'.format(refundamount))
    else:
        messages.add_message(request, messages.ERROR, 'Appointment cancelleds. Refunded({0})'.format(refundamount))
    return redirect(reverse('enduser:appointment_details',) + '?id='+str(appointment.id))

"""
ajax appointment view
"""
def ajax_app_view(request):
    app=Appointments.objects.filter(status=CANCEL)
    return render(request,"admin-includes/header.html",{'app':app})

"""
Become an Rvt
"""
@login_required
def become_an_rvt(request):
    try:
        user=User.objects.get(id=request.user.id)
    except:
        messages.add_message(request, messages.INFO, 'User not found')

    if User.objects.filter(id=request.user.id,applied_for=RVT_LVT, is_verified = VERIFIED):
        messages.add_message(request, messages.INFO, 'You already have verified RVT profile')
        return redirect('enduser:user_profile') 
    elif User.objects.filter(id=request.user.id,applied_for=RVT_LVT, is_verified=0):
        messages.add_message(request, messages.INFO, 'Your request has been already submitted ..please wait for admin approval')
        return redirect('enduser:user_profile')  
    else:
        if request.POST.get('year_of_experience'):
            user.year_of_experience = request.POST.get("year_of_experience")
        if request.POST.get('registration_no'):
            user.registration_no=request.POST.get('registration_no')
        if request.FILES.get('resume'):
            user.resume=request.FILES.get('resume')
        if request.FILES.get('expiry_date'):
            user.expiry_date=request.FILES.get('expiry_date')
        user.is_verified = 0 
        user.applied_for=RVT_LVT
        if user.is_email: 
            current_site = get_current_site(request)
            context = {
                'domain':current_site.domain,
                'site_name': current_site.name,
                'protocol': 'https' if USE_HTTPS else 'http',
                'name':user.first_name
            }
            message = render_to_string('user/become-rvt-mail.html', context)
            mail_subject = 'RVT Application'
            to_email = user.email
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            html_email = render_to_string('user/become-rvt-mail.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
        messages.add_message(request, messages.INFO, 'Request submitted successfully.')
        user.save()
        return redirect('enduser:user_profile')
    
"""
User profile
"""
@user_is_entry_author
def change_to_rvt(request):
    try:
        user=User.objects.get(id=request.user.id)
        if user.user_to_rvt==1:
            user.role_id=3
            user.save()
            return redirect("rvt_lvt:rvt_dashboard")
        else:
            return redirect("enduser:user_dashboard")
    except:
        return redirect('accounts:web_login')

"""
Add Cards 
"""
@login_required
def add_card(request):
    cards = Card.objects.filter(created_by = request.user)
    return render(request,"user/booking.html",{"cards":cards})

"""
Rate RVT
"""
@login_required
def RateRvt(request):
    try:
        rvt_user = User.objects.get(id=request.POST.get('rvt_id'))
    except:
        messages.add_message(request, messages.INFO, 'User not found')
    try:  
        Rating.objects.get(
            created_by = request.user,
            created_for = rvt_user,
            appointment_id = request.POST.get('app_id')
        )
        messages.add_message(request, messages.INFO, 'You have already rated this RVT')
    except:
        Rating.objects.create(
            comment = request.POST.get('description'),
            rating = request.POST.get('rating'),
            created_for = rvt_user,
            created_by = request.user,
            appointment_id = request.POST.get('app_id')
        )
        messages.add_message(request, messages.INFO, 'Rating submitted successfully')
        ratings = Rating.objects.filter(created_for = rvt_user).values_list('rating',flat=True)
        rate = 0
        for a in ratings:
            rate += float(a)
        avg_rating = round(rate/len(ratings))
        if avg_rating:
            rvt_user.average_rating = avg_rating
            rvt_user.save()
    appointment = Appointments.objects.get(id = request.POST.get('app_id'))
    return redirect(reverse('enduser:appointment_details',) + '?id='+str(appointment.id))
            

"""
Help
"""
@login_required
def Recommended_User_Content(request):
    data = {"id":[],"title" :[],"help_topic" :[]}
    recommendations=Recommendation.objects.filter(help_type = request.GET.get('topic_id'),user_type=USER).order_by("-created_on")
    help_topic=HelpTopics.objects.filter(id = request.GET.get('topic_id')).order_by('-created_on')
    for topic in help_topic:
        data["title"].append(topic.title) 
    for rec in recommendations:
        data["help_topic"].append(rec.title)
        data["id"].append(rec.id) 
    return JsonResponse(data)

"""
View Recommendation
"""
@login_required
def view_user_recommendation(request):
    recommendation=Recommendation.objects.get(id=request.GET.get('id'))
    return render(request,'user/view-recommendation.html',{'recommendation':recommendation,"title":"Recommendation"})

"""
Help user
"""
@login_required
def Help_user(request):
    recommendations=Recommendation.objects.all().order_by("-created_on")
    help_type = HelpTopics.objects.all().order_by('-created_on')
    faq=Faq.objects.filter(user_type=2).order_by('-count')[:5]
    faqq=Faq.objects.filter(user_type=2).order_by('-created_on')
    return render(request , "user/user-help.html" , {"title":"Help", "nbar" : "rvt_help","recommendations":recommendations,"help_type":help_type,"faq":faq,"faqq":faqq})

"""
count For Faq
"""
def Faq_count(request):
    data={"count":'0'}
    faqq=Faq.objects.get(id=request.GET.get('faq_id'))
    if faqq:
        faqq.count = int(faqq.count)+1  
        faqq.save()
        data['count']=1
    return JsonResponse(data)


"""
Notifications display
"""
@login_required
def Notification_display_user(request):
    data={"title":[],"created_for":[],"description":[],"created_on":[],"image":[],"n_type":[],"notifications":[],"appointment_id":[],"custom":[],'show_circle':True}
    try:
        notification = Notification.objects.filter(created_for_id=request.user.id).order_by("-created_on")[:5]
        notifications = Notification.objects.filter(created_for=request.user,is_read=0).count()
        if notifications <= 1:
            data['show_circle'] = False
        for noc in notification:
            data["title"].append(noc.title)
            if noc.appointment:
                data['appointment_id'].append(noc.appointment.id)
            else:
                data['appointment_id'].append("")
            data['created_for'].append(noc.created_for.first_name)
            if noc.created_by.profile_pic:
                data['image'].append(noc.created_by.profile_pic.url)
            else:
                data['image'].append(None)
            data['description'].append(noc.description)
            if noc.custom:
                data['custom'].append(noc.custom.service_id)
            data['n_type'].append(noc.n_type)
            data['created_on'].append(timeago.format(noc.created_on.time(), datetime.now()))
        data['notifications'].append(notifications) 
    except:
        pass
    return JsonResponse(data)

"""
All Notifications
"""
@login_required
def All_notifications_user(request):
    notifications =Notification.objects.filter(created_for=request.user).order_by("-created_on")
    page = request.GET.get('page', 1)
    paginator = Paginator(notifications, 10)
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)
    return render(request,"user/all_notification_user.html",{"notifications":notifications,"title":"Notifications","nbar":"notifications"})

"""
Search Notifications
"""
@login_required
def Search_notification_user(request):
    if request.method == 'POST':
        search = request.POST.get("search")
        if not search:
            return redirect('enduser:all_notifications_user')
        if search:
            notification = Notification.objects.filter(title__icontains = search,created_for=request.user)
        return render(request,'user/all_notification_user.html',{"search":request.POST.get("search"),'notifications':notification})

"""
Add or remove favourites
"""
@login_required
def AddFavouriteRvt(request):
    data={"status":""}
    rvt_id=request.GET.get('rvt_id')
    try:
         fav = Favourite.objects.get(created_by = request.user,created_for_id = rvt_id,is_favourite = True)
         if fav:
            fav.delete()
            data["status"] = "removed"
            return JsonResponse(data)

    except:
        fav=Favourite.objects.create(
            created_by = request.user,
            created_for_id = rvt_id,
            is_favourite = True
        )
        data["status"] = "added"
        return JsonResponse(data)

"""
Set Card Default
"""
def SetDefaultCard(request):
    BANK_ADD_URL = env('BANK_ADD_URL')
    try:
        stripe_bank_accounts = stripe.Account.list_external_accounts(
            request.user.bank_account_id,
            object="bank_account",
            limit=1
        )
    except:
        stripe_bank_accounts = None
    stripe_user = stripe.Customer.modify(request.user.customer_id,default_source=request.GET.get('id'))
    completed_jobs=Appointments.objects.filter(created_by=request.user,status=COMPLETED).count()
    if stripe_user.default_source == request.GET.get('id'):
        messages.add_message(request, messages.INFO, 'Default card set successfully!')
    else:
        messages.add_message(request, messages.INFO, 'There is Some issue in your card details!')
    user = User.objects.get(id = request.user.id)
    pets = Pets.objects.filter(created_by = request.user).order_by("-created_on")
    try:
        cards = stripe.Customer.list_sources(request.user.customer_id,object="card",limit=15)
        customer = stripe.Customer.retrieve(request.user.customer_id)
        default = customer.default_source
    except:
        cards = None
        default = None
    return render(request, 'user/user-profile.html',{"default":default,"user":user,"nbar":"settings","user":user,"pets":pets,"cards":cards,"secondTab":True,"completed_jobs":completed_jobs,"stripe_bank_accounts":stripe_bank_accounts,"BANK_ADD_URL":BANK_ADD_URL})

"""
Search Notifications
"""
@login_required
def Search_notification_user(request):
    if request.method == 'POST':
        search = request.POST.get("search")
        if not search:
            return redirect('enduser:all_notifications_user')
        if search:
            notification = Notification.objects.filter(title__icontains = search,created_for=request.user)
        return render(request,'user/all_notification_user.html',{"search":request.POST.get("search"),'notifications':notification})


"""
View Transactions
"""
def View_transactions_user(request,id):
    transactions = Transactions.objects.filter(created_by_id=request.user.id,id=id)
    return render(request,"user/user-view-transaction.html",{"title":"Transaction Information","transactions":transactions})

"""
Payments By user
"""
def User_payment(request):
    transactions = Transactions.objects.filter(created_by=request.user).order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 10)
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    return render(request,"user/user-payments.html",{"title":"Payments","transactions":transactions,"nbar":"payments"})


def Search_payment(request):
     if request.method == "GET":
        if request.GET.get('reset') == "reset":
            return redirect("enduser:user_payment")
        try:
            search=request.GET.get('search')
            d = {'transaction_id':request.GET.get("search"),"created_on" :request.GET.get("date_filter"),"payment_status":request.GET.get('status')}
            syn = "SELECT * FROM tbl_transaction WHERE "
            k =[]
            query = ""
            for i in d.keys():
                if d[i]:
                    k.append('%'+d[i]+"%")
                    query += i + " LIKE %s and "
                elif i == 'status':    
                    if d[i]:
                        k.append(d[i])
                        query += i + " = %s and " 
                else:
                    if i == 'payment_status':    
                        if d[i]:
                            k.append(d[i])
                            query += i + " = %s and " 
            query = query.rstrip(" and")
            syn += query
            searclist=[]
            for user in Transactions.objects.raw(syn,k):
                searclist.append(user.id)
            transactions = Transactions.objects.filter(id__in = searclist,created_by=request.user)
            if transactions:
                return render(request,"user/user-payments.html",{"title":"Transaction History", "nbar" : "payments","search":search,"transactions":transactions,"transaction_id":request.GET.get("search"),"created_on" :request.GET.get("date_filter"),"payment_status":request.GET.get('status')})
            elif request.GET.get('reset') == "reset":
                return redirect("enduser:user_payment")
            else:
                messages.add_message(request, messages.INFO, 'No Payment Found')
                return render(request,"user/user-payments.html",{"title":"Transaction History", "nbar" : "payments","search":search,"transactions":transactions,"transaction_id":request.GET.get("search"),"created_on" :request.GET.get("date_filter"),"payment_status":request.GET.get('status')})
        except:
            messages.add_message(request, messages.INFO, 'Please Enter Something To Search')
            return redirect('enduser:user_payment')

"""
Add rating page
"""
def ViewRating(request):
    user = request.user.id
    rating = Rating.objects.filter(created_for = request.GET.get('id'))
    rating_user = rating.count()
    average_rating = User.objects.get(id= request.GET.get('id'))

    five = Rating.objects.filter(created_for = request.GET.get('id'), rating = 5).count()
    try:
        progress_bar_five = round(rating_user/five) * 100
    except:
        progress_bar_five = 0

    four = Rating.objects.filter(created_for = request.GET.get('id'), rating = 4).count()
    try:
        progress_bar_four = round(rating_user/four) * 100
    except:
        progress_bar_four = 0

    three = Rating.objects.filter(created_for = request.GET.get('id'), rating = 3).count()
    try:
        progress_bar_three = round(rating_user/three) * 100
    except:
        progress_bar_three = 0

    two = Rating.objects.filter(created_for = request.GET.get('id'), rating = 2).count()
    try:
        progress_bar_two = round(rating_user/two) * 100
    except:
        progress_bar_two = 0

    one = Rating.objects.filter(created_for = request.GET.get('id'), rating = 1).count()
    try:
        progress_bar_one = round(rating_user/len(one)) * 100
    except:
        progress_bar_one = 0

    return render(request,'user/rvt-reviews.html',{'title':'Rating',"rating":rating,"average_rating":average_rating,
    "rating_user":rating_user,"five":five,"progress_bar_five":progress_bar_five,"four":four,"progress_bar_four":progress_bar_four,"three":three,
    "progress_bar_three":progress_bar_three,"two":two,"progress_bar_two":progress_bar_two,"one":one,"progress_bar_one":progress_bar_one})


"""
Push notification ON/OFF
"""
def NotificationsStatus(request):
        values = request.GET.get("value")
        user = request.user
        if values =='push_notification':
            if user.is_push:
                user.is_push = False
            else:
                user.is_push = True
        elif values =='email_notification':
            if user.is_email:
                user.is_email = False
            else:
                user.is_email = True
        elif values =='text_notification':
            if user.is_text:
                user.is_text = False
                
            else:
                user.is_text = True
        elif values =='d_notification':
            if user.is_direct_message:
                user.is_direct_message = False
            else:
                user.is_direct_message = True
        user.save()
        return JsonResponse({})


def SearchStatus(request):
    search=request.POST.get('status')
    transactions = Transactions.objects.filter(payment_status__icontains=search,created_by=request.user)
    return render(request,'user/user-payments.html',{'search':search,"transactions":transactions})


"""
Mark mail to vets by User
"""
def MarkMailVet(request):
    appointments = Appointments.objects.get(id=request.GET.get('app_id'))
    pets = Appointments.pet.through.objects.filter(appointments_id=request.GET.get('app_id')).values_list('pets_id',flat=True)
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
        messages.add_message(request, messages.INFO, 'Email Sent Successfully')
        return redirect(reverse('enduser:appointment_details') + '?id='+str(request.GET.get('app_id')))
    else:
        if not vet_emails:
            messages.add_message(request, messages.INFO, 'No Vet Email Found')
        else:
            messages.add_message(request, messages.INFO, 'No Notes Found')
        return redirect(reverse('enduser:appointment_details') + '?id='+str(request.GET.get('app_id')))


"""
Help Request Message
"""
def Help_message(request):
    if request.method=="POST":
        complain=request.POST.get('complain')
        help_request = HelpRequest.objects.create(complain = complain,created_by_id=request.user.id)
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
        messages.add_message(request,messages.INFO,"Your message sent Successfully")
        return redirect('enduser:help_user')


"""
Multiple Search custom  
"""
def Multiple_search_custom(request):
    if request.method=="GET":
        try:
            search=request.GET.get('title')
            d = {
                "title":request.GET.get('title'),
                "date":request.GET.get('date'),
                "is_appointment":request.GET.get('is_appointment')
            }
            syn = "SELECT * FROM tbl_custom_service WHERE "
            k =[]
            query = ""
            for i in d.keys():
                if i == 'state':    
                    if d[i]:
                        k.append(d[i])
                        query += i + " = %s and " 
                elif i == 'date':    
                    if d[i]:
                        k.append(d[i]+"%")
                        query += "DATE("+i+")" + " = %s and " 
                else:
                    if d[i]:
                        k.append('%'+d[i]+"%")
                        query += i + " LIKE %s and "
            query = query.rstrip(" and")
            syn += query
            searclist=[]
            for make in CustomService.objects.raw(syn,k):
                    searclist.append(make.id)
            custom_request = CustomService.objects.filter(id__in = searclist)
            if not custom_request:
                messages.add_message(request,messages.INFO, 'No Data Found')
            elif request.GET.get('reset')=='reset':
                messages.add_message(request,messages.INFO, 'No Data Found')
                return redirect("superuser:custom_requests")
            return render(request,'admin/custom-request.html',{'nbar':'custom-request',"title":"Custom Request","search":search,"custom_request":custom_request,"title":request.GET.get('title'),"date":request.GET.get('date'),'is_appointment':request.GET.get('is_appointment')})
        except:
            return redirect("superuser:custom_requests")


"""
Read More User Dashboard
"""
def Read_more_user(request):
    try:
        banner = Announcements.objects.get(id=request.GET.get('id'))
    except:
        banner = None
    return render(request,"user/readmore.html",{"banner":banner,"title":"Announcment","nbar" :""} )

"""
Calendar appointment list
"""
@login_required
def UserCalendarAppointmentlist(request):
    appointments= Appointments.objects.filter(date = request.GET.get('date'), created_by = request.user)
    return render(request,'user/calendar-appointmentlist.html',{"appointments":appointments})

"""
My appointment
"""
@login_required
def UserMyAppointmentsAJAX(request):
    app_date=datetime.strptime(request.GET.get('datee'), '%d/%B/%Y').strftime('%Y-%m-%d')

    appointments = Appointments.objects.filter(created_by = request.user,date=app_date)
    data = {"date" :[]}
    for app in appointments:
        data["date"].append(app.date)
    return JsonResponse(data,safe=False)


@login_required
def GetUserState(request):
    data = {"state":""}
    try:
        lat = request.GET.get("lat")
        long = request.GET.get("long")
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(lat+","+long)
        state = location.raw['address']['state']
        country=location.raw ['address']['country']
        city=location.raw ['address']['city']
        data['state'] = state
        data['country'] = country
        data['city'] = city
    except:
        data['state'] = ''
        data['country'] = ''
        data['city'] = ''
    return JsonResponse(data)


@login_required
def CancelCusRequest(request):
    try:
        custom=CustomService.objects.get(service_id = request.POST.get('cus_id'))
        if custom:
            custom.delete()
        messages.add_message(request, messages.INFO, 'Custom request cancelled successfully!')
        return redirect('enduser:user_appointments')
    except Exception as e:
        messages.add_message(request, messages.INFO, 'Custom request id not found. {0}'.format(e))
        return redirect('enduser:user_appointments')


@login_required
def FindNearbyRVTs(request):
    API_KEY=env('GOOGLE_API_KEY')
    if request.GET.get("latitude") and request.GET.get("longitude"):
        lattitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
    else:
        lattitude = request.user.latitude
        longitude = request.user.longitude
    services_list =ServiceCategory.objects.all().order_by('-id')
    if lattitude and longitude and lattitude!= 'None' and  longitude!= 'None':
        q=''
        user_list = []
        for i in User.objects.raw('''
                    SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                    cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                    sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id=1 Having  distance < {3};  
                    '''.format(lattitude,longitude,q,env('MILES_RADIUS'))):
            user = User.objects.get(id=i.id)
            if str(user.is_verified) == str(VERIFIED):
                user_list.append(i.id)
        rvt_users = User.objects.filter(id__in=user_list)
    else:
        rvt_users = User.objects.filter(is_verified=VERIFIED)

    if request.GET.get('search_service'):
        service_cat = ServiceCategory.objects.filter(title__icontains = request.GET.get('search_service')).values_list("id",flat=True)
        custom = CustomService.objects.filter(title__icontains = request.GET.get("search_service")).values_list("created_by_id",flat=True) 
        service = Services.objects.filter(category_id__in = service_cat).values_list("created_by_id",flat=True)
        rvt_users = rvt_users.filter(Q(id__in = service)|Q(id__in = custom))  

    if request.GET.get('search_service_select'):
        service_cat = ServiceCategory.objects.filter(title = request.GET.get('search_service_select')).values_list("id",flat=True)
        service = Services.objects.filter(category_id__in = service_cat).values_list("created_by_id",flat=True)
        rvt_users = rvt_users.filter(id__in = service)    
    user_list = Services.objects.all().values_list('created_by_id',flat=True)
    user_list_custom = CustomService.objects.all().values_list('created_by_id',flat=True)
    rvt_users = rvt_users.filter(Q(id__in=user_list)|Q(id__in=user_list_custom))
    servicess = []
    for user in User.objects.filter(is_verified=VERIFIED):
        try:        
            min_price_service = Services.objects.filter(created_by = user).order_by('price')[0]
        except:
            min_price_service = None
        try:        
            min_price_custom = CustomService.objects.filter(created_by = user).order_by('price')[0]
        except:
            min_price_custom = None
        
        if min_price_service and min_price_custom:
            if float(min_price_service.price if min_price_service.price else 0) < float(min_price_custom.price if min_price_custom.price else 0):
                servicess.append(min_price_service)
            else:
                servicess.append(min_price_custom)
        elif min_price_custom:
            servicess.append(min_price_custom)
        elif min_price_service:
            servicess.append(min_price_service)
    return render(request,'user/find-nearby-rvts.html',{"map_rvt":servicess,"rvt_user":rvt_users,"services_list":services_list,"search_service":request.GET.get('search_service'),"search_service_select":request.GET.get('search_service_select'),"API_KEY":API_KEY,"latitude":lattitude,"longitude":longitude,"address":request.GET.get('address'),'nbar':"find_rvt","title":"Find RVT's"})