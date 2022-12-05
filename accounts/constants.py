x

USE_HTTPS=True

"""
Notifications
"""
NOTIFICATION = ((1, "On"),(2,"Off"))
ON = 1
OFF = 2

"""
user role type name
"""
USER_ROLE = ((1, "Admin"),(2,"Users"),(3,"RVT_LVT"),(4,"Sub-Admin"))
ADMIN = 1
USERS = 2
RVT_LVT = 3
SUB_ADMIN = 4

"""
Verified
"""
IS_VERIFIED = ((0, "unverified"),(1,"verified"),(2,"declined"),(3,"reject"))
UNVERIFIED = 0
VERIFIED = 1
DECLINED = 2
REJECT_RVT = 3


"""
User Status
"""
USER_STATUS = ((1, "Active"),(2,"Inactive"),(3,"Deleted"))
ACTIVE = 1
INACTIVE = 2
DELETED = 3


"""
User Gender
"""
GENDER  = ((1,"Male"),(2,"Female"),(3, "Transgender"))
MALE = 1
FEMALE = 2
TRANSGENDER = 3


"""
Device
"""
DEVICE_TYPE  = ((1,"Android"),(2,"IOS"),)
ANDROID = 1
IOS = 2


"""
JOB_APPLY_STATUS
"""
JOB_APPLY_STATUS = ((0,"Pending"),(1,"Accepted"),(2,"Rejected"),(3,"Apply") )
PENDING = 0
ACCEPTED = 1
REJECTED = 2
APPLIED = 3


"""
APP_STATUS
"""
APP_STATUS = ((0,"Pending"),(1,"Scheduled"),(2,"Completed"),(3,"Cancelled"),(4,"Accept"),(5,"Reject"))
PENDING = 0
SCHEDULED = 1
COMPLETED = 2
CANCELLED = 3
ACCEPT = 4
REJECT = 5


"""
NOTES_TYPE
"""
NOTES_TYPE = ((1,"Public"),(2,"Private"))
PUBLIC = 1
PRIVATE = 2


"""
Page Type
"""
PAGE_TYPE =  ((1,"Terms_And_Condition"),(2,"Privacy_Policy"),(3,"Cookie_Policy"))
TERMS_AND_CONDITION = 1
PRIVACY_POLICY  = 2
COOKIE_POLICY = 3



"""
Help Status
"""
HELP_STATUS = ((0,"NotAssigned"),(1,"Assigned"))
NOTASSIGNED = 0
ASSINGED = 1


"""
blog staus
"""
BLOG_STATUS = ((0,"BS_Pending"),(1,"BS_Published"))
BS_PENDING = 0
BS_PUBLISHED = 1


"""
BLOG_VISIBILITY
"""
BLOG_VISIBILITY = ((0,"BV_Public"),(1,"BV_Private"))
BV_PUBLIC = 0
BV_PRIVATE = 1


"""
news staus
"""
NEWS_STATUS = ((0,"NS_Pending"),(1,"NS_Published"))
NS_PENDING = 0
NS_PUBLISHED = 1


"""
NEWS_VISIBILITY
"""
NEWS_VISIBILITY = ((0,"NV_Public"),(1,"NV_Private"))
NV_PUBLIC = 0
NV_PRIVATE = 1


"""
Faq User type
"""
USER_TYPE = ((1,"USER"),(2,"RVT"))
USER = 1
RVT = 2

"""
service status
"""
SERVICE_STATUS = ((1,"ACTIVE"),(2,"INACTIVE"))
ACTIVE = 1
INACTIVE = 2
RVT = 2


"""
ANNOUNCEMENT_STATUS
"""
ANNOUNCEMENT_STATUS = ((1,"TARGET_USER"),(2,"TARGET_RVT"),(3,"TARGET_ALL"))
TARGET_USER = 1
TARGET_RVT = 2
TARGET_ALL = 3 

"""
Blog category
"""
BLOG_CATEGORY = ((1,"WhatsNew"),(2,"PetResource"),(3,"ContinueEduction"))
WHATS_NEW = 1
PET_RESOURCE = 2
CONTINUE_EDUCATION = 3


"""
CARD_TYPE
"""
CARD_TYPE = ((1,"Visa"),(2,"Mastercard"))
VISA = 1
MASTERCARD = 2


"""
Payment Status
"""
PAYMENT_STATE = ((1,'Not_Realeased'),(2,'Released'))
NOT_RELEASED = 1
RELEASED = 2

PAYMENT_TYPE = ((1,'Payment'),(2,'Credit'),(3,'Refund'))
PAYMENT = 1
CREDIT = 2
REFUND = 3


"""
Social Type
"""
SOCIAL_TYPE = ((1,'Google'),(2,'APPLE'))
GOOGLE = 1
APPLE = 2

"""
Notification Type
"""
NOTIFICATION_TYPE=((1,'Booking'),(2,'Cancel'),(3,'Mark_complete'),(4,'Become_Rvt'))
BOOKING=1
CANCEL=2
MARK_COMPLETE=3
BECOME_RVT=4

"""
Notification
"""
NOTIFICATION=((1,'On'),(2,'Of'))
ON = 1
OFF = 2 