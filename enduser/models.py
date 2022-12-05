x
 
from django.db import models
from accounts.models import User
from accounts.constants import *
from enduser.constants import PET_GENDER, PET_TYPE
from .constants import *
"""
Images
"""
class Images(models.Model):
    file = models.ImageField(upload_to='images',blank=True,null=True)
    created_on = models.ImageField(upload_to='images',blank=True,null=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'tbl_image'



"""
Pet type
"""
class PetType(models.Model):
    name = models.CharField(max_length=100,blank=True,null = True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    service_type = models.PositiveIntegerField(default=1,choices=SERVICE_TYPE,null=True,blank=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super(PetType, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = 'tbl_pet_type'

"""
Pet 
"""
class Pets(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    image = models.ManyToManyField(Images)
    description = models.TextField(null=True,blank=True)
    age = models.CharField(max_length=50,null=True,blank=True)
    pet_gender = models.PositiveIntegerField(default=1,choices=PET_GENDER,null=True, blank=True)
    breed = models.CharField(max_length=100,blank=True,null=True)
    pet_type =models.ForeignKey(PetType,on_delete=models.CASCADE,null=True, blank=True)
    height = models.CharField(max_length=50,null=True,blank=True)
    vet_name = models.CharField(max_length=150,null=True,blank=True)
    vet_email = models.CharField(max_length=100,null=True,blank=True)
    add_note = models.TextField(max_length=255,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    size = models.CharField(max_length=50,null=True,blank=True)
    vet_profile = models.ImageField(upload_to='profile_pic/',blank=True,null=True)
    vet_number = models.CharField(max_length=12,blank=True,null=True)
    vet_adrress = models.CharField(max_length=500,blank=True,null=True)
    vaccines = models.CharField(max_length=500,blank=True,null=True)

    class Meta:
        managed = True
        db_table = 'tbl_pet'

    def __str__(self):
        return str(self.name)



"""
Help Request
"""
class HelpRequest(models.Model):
    title = models.CharField(max_length=50,blank=True,null=True)
    complain = models.CharField(max_length=255,blank=True,null=True)
    status = models.CharField(max_length=30,choices=HELP_STATUS,default=0)
    assign_to = models.ForeignKey(User,on_delete=models.CASCADE,related_name='assign_to', null = True, blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='complaint_creator')
    created_on = models.DateTimeField(auto_now_add=True)
    class Meta:
        managed = True
        db_table = 'tbl_helprequest'


"""
card
"""
class Card(models.Model):
    expire_date = models.CharField(max_length=255,blank=True,null=True)
    card_holder_name = models.CharField(max_length=100,blank=True,null=True)
    ac_no =  models.CharField(max_length=150,blank=True,null=True)
    cvv = models.CharField(max_length=10,blank=True,null=True)
    created_on= models.DateTimeField(auto_now_add=True,null=-True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    image = models.ImageField(upload_to='card_image/', blank=True, null=True)
    default = models.CharField(max_length=10,blank=True,null=True)
    type = models.CharField(max_length=50, choices=CARD_TYPE,blank=True,null=True)

    class Meta:
        db_table = 'tbl_card'
        managed = True


"""
Favourite RVT
"""
class Favourite(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='favourite_by')
    created_for = models.ForeignKey(User,on_delete=models.CASCADE,related_name='favourite_for')
    is_favourite = models.BooleanField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    class Meta:
        managed = True
        db_table = 'tbl_favourite_rvt'

