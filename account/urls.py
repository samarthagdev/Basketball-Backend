from django.urls import re_path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    re_path('login', obtain_auth_token, name="login"),
    re_path('checking', views.checkin_email, name='checking'),
    re_path('creating', views.creating_account, name='creating'),
    re_path('gettingotp', views.sending_otp, name='sendingOtp'),
    re_path('user', views.login_in, name='user'),
    re_path('credential', views.checking_credential, name='credential'),
    re_path('otp', views.sending_otp2, name='otp'),
    re_path('settingpass', views.set_pass, name='pass'),
    re_path('getnum', views.sending_otp3, name='get_num'),
    # re_path('user', views.getting_user, name='user'),
]

