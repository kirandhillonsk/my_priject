from django.core.management.base import BaseCommand
from accounts.models import User
from enduser.models import PetType 
from .pettypes import *

class Command(BaseCommand):
    help = "Adding default pet type to Database by Admin"
    def handle(self, *args, **options):
        confirm = input("Do you want to add categories, (y/n):")
        try:        
            user=User.objects.get(is_superuser=1,role_id=1)
        except:
            self.stdout.write(self.style.NOTICE("Admin rights, Create Admin First"))
            return None
            
        if confirm.lower()=="y":

            self.stdout.write(self.style.HTTP_NOT_MODIFIED('Pet-Type'))
            for pet in pettypes:
                pet = PetType.objects.create(name=pet, created_by=user)
                self.stdout.write(self.style.SUCCESS('Pet-Type %s' %pet.name))

        elif confirm.lower()=="n":
            pass
        else:
            self.stdout.write(self.style.NOTICE("Enter response from given choices"))
        
