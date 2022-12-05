x
 

import re
from django import forms
from accounts.models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

users = get_user_model()

alnum_re = re.compile(r"\w+$") 

regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Email Or Username"), max_length=254)
    
class EmailValidationOnForgotPasswordForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with the specified email address!")

        return email       





class ChangePassword(forms.Form):
    old_paasword=forms.CharField(widget=forms.PasswordInput())
    password=forms.CharField(widget=forms.PasswordInput())
    confirm_password=forms.CharField(widget=forms.PasswordInput())
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        qs = User.objects.filter(email__iexact=value)
        if not qs:
            raise forms.ValidationError(_("No user found with this email address"))
        return value
    
    def clean(self):
        if len(self.cleaned_data["password"]) < 8:
            raise forms.ValidationError("Password is too short.")
        
        if self.cleaned_data["password"] != self.cleaned_data["confirm_password"]:
            raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data


class SubscriptionForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"), widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'input100 form-control'}),
        required=True)

    def clean_email(self):
        value = self.cleaned_data["email"]
        qs = User.objects.filter(email__iexact=value)
        if qs.exists():
            return value
        raise forms.ValidationError(
            _("User is not registered with this email address."))