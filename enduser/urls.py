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
from .views import *
from .views import *
from .views_api import *
from django.urls import path
from django.conf.urls import url

app_name = 'enduser'

urlpatterns = [
    url(r'^user-dashboard/$', UserDashboard, name='user_dashboard'),
    path('user-profile-view/', UserProfile, name='user_profile'),
    url(r'^user-profile-image/$', UserProfileImage, name='user_profile_image'),
    url(r'^user-chat-list/$', USERChat, name='users_chat_list'),
    url(r'^send-message/$', SendMessageUser, name='send_message'),
    path("ajax-load-get-group-messages-artist/<int:id>", ajax_load_get_group_messages_singer, name="ajax_load_get_group_messages_singer"),
    path("artist-ajax-load-group-message-update/<int:rid>", singer_ajax_load_group_messages_update, name="singer_ajax_load_group_message_update"),
    url(r'^user-chat-screen/$', UserChatWindow, name='users_chat_screen'),
    url(r'^send-message-rvt/$', SendMessageRvt, name='send_message_rvt'),
    url(r'^user-status-change/$', UserStatusChange, name='user_status_change'),
    url(r'^remove-pet/$',Remove_pet, name='remove_pet'),
    url(r'^edit-pet/(?P<id>[-\w]+)/$',Edit_pet, name='edit_pet'),
    url(r'^delete-appointment/(?P<id>[-\w]+)/$',Deleteappointment, name='delete_appointment'),
    url(r'^user-appointments/$',MyAppointment, name='user_appointments'),
    path('user-custom-requests/',MyCustomRequests, name='user_custom_requests'),
    url(r'^search-by-name/$',Searchuser, name='search_by_name'),
    url(r'^add-card/$',AddCard, name='add_card'),
    url(r'^search-by-service/$',SearchByService, name='search_by_service'),
    url(r'^search-by-status/$',SearchByStatus, name='search_by_status'),
    url(r'^custom-service-request/$',CustomRequest, name='custom_service'),
    url(r'^custom_service_display/$',custom_service_display, name='custom_service_display'),
    url(r'rvt-user-details/$', CategoryWiseRVTdetail, name='rvt_user_details'),
    url(r'^bookings/$',BookingsView.as_view(), name='bookings'),
    url(r'^rvt-booking/(?P<id>[-\w]+)/$',BookingRVT, name='rvt_booking'),
    path('rvt-availability', RVTAailability, name='rvt_availability'),
    path('selected-services', SelectedServices, name='selected_services'),
    path('rvt-availability-ajax', RVTavailabilityC, name='rvt_availability_ajax'),
    path('my_appointment_calendar', MyAppointmentsCalander, name='my_appointment_calendar'),
    path('searchby-service', SearchByService, name='searchby_service'),
    path('month-filter/', MonthFilter,name = 'month_filter'),
    path('availability-check/', AvailabilityCheck,name = 'availability_check'),
    path('become-an-rvt/',become_an_rvt,name='become_an_rvt'),
    path('applicants-details/',ApplicantsDetails,name='applicants_details'),
    path('accept-rvt/',AcceptRvt,name='accept_rvt'),
    path('reject-rvt/',RejectRvt,name='reject_rvt'),
    url(r'custom_appointment$', CustomAppointment, name='custom_appointment'),
    url(r'hide-custom-row$', HideCustomRow, name='hide_custom_row'),
    path('appointment-modal', AppointmentModal, name='appointment_modal'),
    url(r'view-appoints$', ViewAppoints, name='view_appoints'),
    url(r'check-availability-app$', CheckAvailabilityApp, name='check_availability_app'),
    url(r'rate-rvt$', RateRvt, name='rate_rvt'),
    url(r'view-all-rvt$', ViewAllRrvt, name='view_all_rvt'),
    path('custom-selected-services', CustomSelectedServices, name='custom_selected_services'),
    path('search-notification-user/',Search_notification_user,name='search_notification_user'),
    path('help-message/', Help_message, name='help_message'),
    path('Faq-count/', Faq_count, name='faq_count'),
    path('cancel-cus-request/', CancelCusRequest, name='cancel_cus_request'),
    path('api/add-pet/',AddPet.as_view(), name = 'addpet'),
    path('api/delete-pet/',DeletePetInfo.as_view(), name = 'delete_pet'),
    path('api/edit-pet-info/',EditPetInfo.as_view(), name = 'edit_pet_info'),
    path('api/help-request/',HelpRequestView.as_view(), name = 'help_request'),
    path('api/custom-service/',CustomServiceRequest.as_view(), name = 'custom_service_request'),
    path('api/rvt-user-list/',CategoryWiseRVTListAPI.as_view(), name = 'rvt_user_list'),
    path('api/nearby-rvt/', NearByRVTView.as_view(), name='nearby_rvt'),
    path('api/become-rvt/', BecomeAnRVT.as_view(), name='become_rvt'),
    path('api/service-category-list/', ServiceCategoryList.as_view(), name='service_category_list'),
    path('api/rvt-categorywise-list/', RVTCategoryWiseList.as_view(), name='rvt_categorywise_list'),
    path('api/hire-me/', HireMeView.as_view(), name='hire_me'),
    path('api/appointment-detail/', AppointmentDetailsView.as_view(), name='appointment_detail'),
    path('api/rvt-rating-list/', RVTRatingList.as_view(), name='rvt_rating_list'),
    path('api/search-services/', SearchService.as_view(), name='search_services'),
    path('api/rating-filter/', Ratingfilter.as_view(), name='rating_filter'),
    path('api/custom-service-list/', CustomServiceListView.as_view(), name='custom_service_list'),
    path('api/custom-service-detail/', CustomServiceDetail.as_view(), name='custom_service_detail'),
    path('api/save-card/', SaveCard.as_view(), name='save_card'),
    path('api/pet-profile/', PetProfile.as_view(), name='pet_profile'),
    path('api/pet-listing/', Petlisting.as_view(), name='pet_listing'),
    path('api/rvt-profile-detail/', RVTProfileDetailView.as_view(), name='rvt_profile_detail'),
    path('api/rvt-profile-detail-anonymous/', RVTProfileDetailViewAnonymous.as_view(), name='rvt_profile_detail_anonymous'),
    path('api/rvt-availability-list/', RVTAvailabilitylist.as_view(), name='rvt_availability_list'),
    path('api/book-rvt/', BookRVTAPI.as_view(), name='book_rvt'),
    path('api/booking-view/', BookingView.as_view(), name='booking_view'),
    path('api/get-booking-prices/', GetBookingPrices.as_view(), name='get_booking_prices'),
    path('api/user-appointment-list/', UserAppointmentListView.as_view(), name='user_appointment_list'),
    path('api/pet-listing-admin/', PetlistingAdmin.as_view(), name='pet_listing_admin'),
    path('api/all-custom-services/', UserCustomServiceList.as_view(), name='user_custom_service_list'),
    path('api/custom-service-applicants/', CustomServiceApplicants.as_view(), name='custom_service_applicants'),
    path('api/custom-service-status/', CustomServiceStatus.as_view(), name='custom_service_status'),
    path('api/user-past-appointment/', UserPastAppointment.as_view(), name='user_past_appointment'),
    path('api/commonly-asked-question/', CommonlyAskedQuestion.as_view(), name='commonly_asked_question'),
    path('api/faq-description/', FaqDescription.as_view(), name='faq_description'),
    path('api/faq-list/', FAQList.as_view(), name='faq_list'),
    path('api/user-notification/', UserNotification.as_view(), name='user_notification'),
    path('api/mark-read-notification/', MarkReadNotification.as_view(), name='mark_read_notification'),
    path('api/unread_count/', UnreadCount.as_view(), name='unread_count'),
    path('api/rvt-availabilities/', RVTAvailabilities.as_view(), name='rvt_availabilities'),
    path('api/user-custom-appointment/', UserCustomAppointment.as_view(), name='user_custom_appointment'),
    path('api/reject-applicant-request/', RejectApplicantRequest.as_view(), name='reject_applicant_request'),
    path('api/mark-cancel-appointment/', MarkCancelAppointmentView.as_view(), name='mark_cancel_appointment'),
    path('api/notification-all_read/', MarkNotificationRead.as_view(), name='notification_all_read'),
    path('api/mark-favourite/', MarkFavourite.as_view(), name='mark_favourite'),
    path('api/mark-unfavourite/', MarkUnFavourite.as_view(), name='mark_un_favourite'),
    path('api/favourite-rvt-listing/', FavouriteRVTListing.as_view(), name='favourite_rvt_listing'),
    path('api/chat-user-profile/', ChatUserProfile.as_view(), name='chat_user_profile'),
    url(r'api/anonymous-nearby-rvt-list/$',AnonymousNearByRVTView.as_view(),name="anonymous_nearby_rvt_list"),
    url(r'api/all-services/$',AnonymousServiceList.as_view(),name="anonymous_service_list"),
    path('api/banner_listing/', Bannerlisting.as_view(), name='banner_listing'),
    path('api/search-filter/', SearchFilter.as_view(), name='search_filter'),
    path('api/filter-appointment-list/', FilterAppointmentList.as_view(), name='filter_appointments_list'),

    ## Remove Later
    path('api/notification-status-push/', NotificationsStatusPush.as_view(), name='notification_status_push'),
    path('api/notification-status-email/', NotificationsStatusEmail.as_view(), name='notification_status_email'),
    path('api/notification-status-text/', NotificationsStatusText.as_view(), name='notification_status_text'),
    path('api/notification-status-direct-message/', NotificationsStatusDirectMessage.as_view(), name='notification_status_direct_message'),
    path('api/notification-status-location-tracking/', NotificationsStatusLocationTracking.as_view(), name='notification_status_location_tracking'),

    #######
    
    path('api/pet-appointment/', PetAppointment.as_view(), name='pet_appointment'),
    path('api/filter-past-appointment/', FilterPastAppointmentList.as_view(), name='filter_past_appointment'),




    path('rvt-profile/<int:id>', UserRvtProfile, name='user_rvt_profile'),
    path('choose-service', UserChooseService, name='user_choose_service'),
    path('add-pet', UserAddPet, name='add_pet'),
    path('book-add-pet', Booking_AddPet, name='book_add_pet'),
    path('pet-profile/<int:id>', UserPetProfile, name='pet_profile'),
    path('user-appointment-request', UserAppointmentRequest, name='user_appointment_request'),
    path('deletecard/',Delete_Card,name='deletecard'),
    path('api/cancel-custom-app/', CancelCustomApp.as_view(), name='cancel_custom_app'),

    path('change_to_rvt/',change_to_rvt,name='change_to_rvt'),
    path('appointment-details/',UserAppointmentDetails,name='appointment_details'),
    path('cancel-appointment/',CancelAppointment,name='cancel_appointment'),
    path("add_card/",add_card,name="Add_card_booking"),
    path('recommended-user-content/',Recommended_User_Content,name='recommended_user_content'),
    path('view-user-recommendation/',view_user_recommendation,name='view_user_recommendation'),
    path('help-user/',Help_user,name='help_user'),
    path('notification-display-user/',Notification_display_user,name='notification_display_user'),
    path('all-notifications-user/',All_notifications_user,name='all_notifications_user'),
    path('Set-default-card/',SetDefaultCard,name='set_default_card'),
    path('add-favourite-rvt/',AddFavouriteRvt,name='add_favourite_rvt'),
    path('search-notification-user/',Search_notification_user,name='search_notification_user'),
    path('user-payment/',User_payment,name="user_payment"),
    path('view-transactions-user/<int:id>',View_transactions_user,name='view_transactions_user'),
    path('Search_payment/',Search_payment,name='Search_payment'),
    path('view-rating/',ViewRating,name='view_rating'),
    path('mark-mail-vet/',MarkMailVet,name='mark_mail_vet'),
    path('api/mail-to-vets/',mailToVets.as_view(),name='mail_to_vets'),
    path('read-more-user/',Read_more_user,name='read_more_user'),
    path('calendar-appointment-list/', UserCalendarAppointmentlist, name='user_calendar_appointment_list'),
    path('user-appointments-ajax', UserMyAppointmentsAJAX, name='user_appointments_ajax'),
    url(r'^get-user-state/$', GetUserState, name='get_state_name'),
    url(r'^find-nearby-rvts/$', FindNearbyRVTs, name='find_nearby_rvts'),
    
   

]
