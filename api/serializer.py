x
import environ
from accounts.models import *
from rest_framework_jwt import serializers
from rest_framework import serializers as Serializers
from enduser.models import Favourite
from rvt_lvt.models import Transactions


env = environ.Env()
environ.Env.read_env()




"""
user serializer
"""
class UserSerializer(Serializers.ModelSerializer):
    is_favourite = Serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields =('id','username','full_name','first_name','last_name','email','mobile_no','profile_pic','address','city','state','role_id','state_id','status','job_status','created_on','year_of_experience','resume','registration_no','is_verified','about_me','average_rating','otp','verify_otp','is_subscribe','applied_for','user_to_rvt','features_approval','latitude','longitude','country','session_id','is_favourite','badge','expiry_date','customer_id','bank_account_id','is_push','is_email','is_text','is_direct_message','is_location_tracking')
        depth=1
    def get_is_favourite(self,obj):
        try:
            user = self.context['request'].user
        
            fav = Favourite.objects.filter(created_by=user,created_for = obj)
            if fav:
                return True
            else:
                return False
        except:
            user = None


"""
login serializer
"""
class LoginSerializer(serializers.JSONWebTokenSerializer):
    def validate_email(self,value):
        if not value or value == '':
            raise serializers.ValidationError("Please enter email.")
        return value
    
    def validate_password(self,value):
        if not value or value == '':
            raise serializers.ValidationError("Please enter password.")
        return value


"""
Transactions
"""
class TransactionsSerializer(Serializers.ModelSerializer):
    created_on = Serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Transactions
        fields = ('id','amount','currency','transaction_id','payment_status','created_on','created_by','created_for','appointment','payment_state','payment_type')

    def get_created_on(self, obj):
        transaction = Transactions.objects.get(id=obj.id)
        date_time = transaction.created_on
        return date_time.strftime("%Y-%m-%d %H:%M:%S")
