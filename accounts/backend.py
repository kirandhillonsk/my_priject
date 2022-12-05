x
 
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from accounts.constants import ACTIVE, INACTIVE

User = get_user_model()



class EmailLoginBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        try:
            user = User.objects.get(Q(username=username)|Q(email=username), Q(state_id=str(ACTIVE))|Q(state_id=str(INACTIVE)))
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user


