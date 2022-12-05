'''
/**
 *@copyright : ToXSL Technologies Pvt. Ltd. < www.toxsl.com >
 *@author     : Shiv Charan Panjeta < shiv@toxsl.com >
 *
 * All Rights Reserved.
 * Proprietary and confidential :  All information contained herein is, and remains
 * the property of ToXSL Technologies Pvt. Ltd. and its partners.
 * Unauthorized copying of this file, via any medium is strictly prohibited.
 **/
'''

from django.contrib import admin
x
from .views import *
from django.conf.urls import url


admin.autodiscover()
app_name = 'api'


urlpatterns = [

    ## Authentication
    url(r'register-user/$',NormalSignUpViews.as_view(),name="register_user"),
    url(r'login/$',LoginView.as_view(),name="login"),
    url(r'social-signin/$',SocialSignInView.as_view(),name="social_sign_in"),
    url(r'check-user/$',UserCheckView.as_view(),name="check_user"),
    url(r'logout/$',LogoutView.as_view(),name="logout"),
    url(r'edit-profile/$',EditProfileView.as_view(),name="edit_profile"),
    url(r'reset_password/$',ResetPassword.as_view(),name="reset_password"),
    url(r'user-profile/$',UserProfileView.as_view(),name="user_profile"),
    url(r'forget-password/$',ForgetPassword.as_view(),name="forget_password"),

    ## Stripe Card
    url(r'add-card/$',AddCardView.as_view(),name="add_card_view"),
    url(r'delete-card/$',DeleteCardView.as_view(),name="delete_card_view"),
    url(r'user-cards-list/$',UserCardsList.as_view(),name="user_cards_list"),
    url(r'set-default-card/$',SetDefaultCard.as_view(),name="set_default_card"),

    ## Transactions 
    url(r'transactions-list/$',TransactionsList.as_view(),name="transactions_list"),
    url(r'transaction-details/$',TransactionDetails.as_view(),name="transaction_details"),

    ## Bank Accounts
    url(r'add-bank-account/$',AddBankAccount.as_view(),name="add_bank_account"),
    url(r'get-bank-account/$',GetBankAccount.as_view(),name="get_bank_account"),
    url(r'delete-bank-account/$',DeleteBankAccount.as_view(),name="delete_bank_account"),

    ## Change Settings
    url(r'change-user-settings/$',ChangeUserSettings.as_view(),name="change_user_settings"),
    url(r'active-inactive-account/$',ActiveInactiveUserAccount.as_view(),name="active_inactive_account"),
    url(r'take-break/$',TakeBreak.as_view(),name="take_break"),
    url(r'flat_page/$',FlatPages.as_view(),name="flat_page"),
    url(r'delete-account/$',DeleteAccount.as_view(),name="delete_account"),
    url(r'user-details/$',UserDetails.as_view(),name="user_details"),

    ## Calender API
    url(r'google-calender-link/$', GenerateCalenderLink.as_view(), name='google_calender_link'),

]
