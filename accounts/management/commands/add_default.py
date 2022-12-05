from django.core.management.base import BaseCommand
from .default_values import *
from accounts.models import *
from enduser.models import PetType


class Command(BaseCommand):
    help = "Adding default values to Database by Admin"
    def handle(self, *args, **options):
        confirm = input("Do you want to add default, (y/n):")
        try:        
            user=User.objects.get(is_superuser=1, role_id='1')
        except:
            self.stdout.write(self.style.NOTICE("Admin rights, Create Admin First"))
            return None
            
        if confirm.lower()=="y":

            self.stdout.write(self.style.HTTP_NOT_MODIFIED('pet type'))
            for type in range(len(PET_TYPE)):
                charges = PetType.objects.create(name=PET_TYPE[type],created_by=user)
                self.stdout.write(self.style.SUCCESS('Role %s' %PET_TYPE[type]))


        elif confirm.lower()=="n":
            pass
        else:
            self.stdout.write(self.style.NOTICE("Enter response from given choices"))

