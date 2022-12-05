x
from .views import *
from accounts import views
from django.contrib import admin
from django.conf.urls import url
from django.urls import reverse_lazy, path

admin.autodiscover()

app_name = 'accounts'

urlpatterns = [
    url(r'^web-signup/$', WebSignupView.as_view(), name='web_signup'),
    url(r'^rvt-signup/$', RvtSignupView.as_view(), name='rvt_signup'),
    url(r'^email-validation/$', EmailValidation, name='email_validation'),
    url(r'^rvt-mail-validation/$', RvtEmailValidation, name='rvt_email_validation'),
    url(r'^rvt-email-validation/$', RvtUsernameValidation, name='rvt_username_validation'),
    url(r'^login/$', LoginView.as_view(), name='web_login'),
    url(r'^logout/$', LogOutView.as_view(), name='logout'),
    url(r'^OTP-verification/$', OTPVerfication, name='OTP_Verfication'),
    url(r'^reset-password/$', ResetPassword, name='reset_password'),
    url(r'^username-validation/$', UsernameValidation, name='username_validation'),
    url(r'^view-user/$', ViewUser, name='view_user'),
    url(r'^edit-user/$', EditUser.as_view(), name='edit_user'),


    url(r'^deleteuser/$', DeleteUser, name='delete_user'),
    url(r'^users/$', Allusers, name='allusers'),
    url(r'^rvt-lvt-user/$', RvtLvtUsers, name='rvt_lvt_user'),
    url(r'^edit-user/$', EditUser.as_view(), name='Edit_User'),
    url(r'^change-password/$', PasswordChange.as_view(), name='Password_Change'),
    url(r'^admin/change-status-active$', ChangeStatusActive, name='change_status_active'),
    url(r'^admin/change-status-inactive$', ChangeStatusInactive, name='change_status_inactive'),
    url(r'^admin/change-status-delete$', ChangeStatusDelete, name='change_status_delete'),
    url(r'^admin/newsletter-subscription$', NewsletterSubscriptions, name='newsletter_subscription'),
    url(r'^admin/search-newsletter-subscription$',Search_Newsletter_subscription, name='search_newsletter_subscription'),
    url(r'^admin/transaction-history$', TransactionHistory, name='transaction_history'),
    url(r'^admin/help-request$', Helprequest, name='help_request'),
    url(r'^accept-request/$', Accept_request, name='accept_request'),
    url(r'^reject_request/$', Reject_request, name='reject_request'),
    url(r'^search-name/$', SearchByName, name='search_name'),
    url(r'^view/(?P<id>[-\w]+)/$', ViewUser, name='View_User'),
    url(r'^download/(?P<id>[-\w]+)/$', download, name='download'),
    url(r'^complete-verification$', Completeverification, name='complete_verification'),
    url(r'^card-validation$', CardValidation, name='card_validation'),
    url(r'^view-transactions/(?P<id>[-\w]+)/$', View_transactions, name='view_transactions'),
    url(r'^search-transactions$', Search_Transactions, name='search_transactions'),
  
    url(r'^delete-subscription/$', DeleteSubscription, name='delete_subscription'),
    url(r'^forgot-password/$', ForgotPassword.as_view(), name='Forgot_Password'),

    url(r'^forgot-password-mail/$', Forgot_password_mail, name='forgot_password_mail'),
    path("reset-password-user/<token>/",Reset_password,name="reset_password_user"),
    url(r'^admin/search-newsletter-subscription$',Search_Newsletter_subscription, name='search_newsletter_subscription'),
    path('password_confirmation/',password_confirmation,name='password_confirmation'),
    path('activate_account/',activate_account,name='activate_account'),
    path('response/',AddBank,name='add_bank'),
    path('delete-bank/',DeleteBank,name='deletebank'),
    path('bank-message/',BankMessage,name='bank_message'),

    
    path('assign-help-request/',AssignHelpRequest,name='assign_help_request'),
    path('delete-help-request/',DleteHelpRequest,name='delete_help_request'),
    path('edit-help-request/',EditHelpRequest,name='edit_help_request'),


]