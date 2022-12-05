x
 
from rest_framework import serializers as Serializers
from rest_framework_jwt import serializers
from enduser.models import *
from rvt_lvt.models import CustomService, Services
import environ
env = environ.Env()
environ.Env.read_env()


"""
Pet  Serializer
"""
class PettypeSerializer(Serializers.ModelSerializer):
     
    class Meta:
        model = PetType
        fields =("id","name","created_by","service_type")
        depth = 1

"""
Pet type Serializer
"""
class PetSerializer(Serializers.ModelSerializer):
     
    class Meta:
        model = Pets
        fields =("id","name","image","description","age","pet_gender","breed","pet_type","height","vet_name","vet_email","vet_number","vet_number","vet_adrress","created_on","size","vet_profile","created_by","vaccines")
        depth = 1

"""
Help Request
"""
class HelpRequestSerializer(Serializers.ModelSerializer):

    class Meta:
        model = HelpRequest
        fields = '__all__'


"""
Favourite Serializer
"""
class FavouriteSerializer(Serializers.ModelSerializer):
    services = Serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Favourite
        fields =('created_by','created_for','is_favourite','services','created_on')
        depth = 1
    def get_services(self,obj):
        service = Services.objects.filter(created_by = obj.created_for)
        custom_services = CustomService.objects.filter(created_by=obj.created_for)
        data = []
        if service:
            for service in service:
                service_list = {}
                service_list["created_by"]=service.created_by.first_name
                service_list["category"] = service.category.title
                service_list["price"] = service.price
                service_list["city"] = service.created_by.city
                service_list["state"] = service.created_by.state
                service_list["rating"] = service.created_by.average_rating
                data.append(service_list)
        if custom_services:
            for service in custom_services:
                service_list = {}
                service_list["id"]=service.id
                service_list["category"] = service.title
                service_list["service_id"] = service.service_id
                service_list["city"] = service.city
                service_list["state"] = service.state
                service_list["location"] = service.location
                service_list["country"] = service.country
                service_list["created_by"] = service.created_by.first_name
                service_list["price"] = service.price
                service_list["rating"] = service.created_by.average_rating
                data.append(service_list)
        return data
    
     
