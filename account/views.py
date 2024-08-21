from contextlib import nullcontext

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Account, Otpveification1
from main_app.models import Players
from .serializers import AccountSerilizer
import http.client
import random
from firebase.views import firebase_account
from firebase.models import devicetoken

from collections import namedtuple
import json

# Create your views here.

lis = []
for x in range(1, 10):
    for y in range(1, 10):
        for a in range(1, 10):
            for b in range(1, 10):
                lis1 = str(x) + str(y) + str(a) + str(b)
                if len(lis1) == 4:
                    lis.append(int(lis1))

@api_view(['POST'])
def checkin_email(request):
    if request.method == 'POST':
        if Account.objects.filter(email=request.data.get('email')).exists():
            account = Account.objects.get(email=request.data.get('email'))
            serializer = AccountSerilizer(account, context= {'request': request})
            data = serializer.data
            token = Token.objects.get(user=account).key
            data['token'] = token
            return firebase_account(uni_id=account.userName, data=data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def creating_account(request):
    if request.method == 'POST':
        if Account.objects.filter(userName=request.data.get('uniId')).exists():
            return Response(status=status.HTTP_205_RESET_CONTENT)
        else:
            if request.data.get('number') is None:
                account = Account.objects.create_user(userName=request.data.get('uniId').strip(), name=request.data.get('displayName'),
                                                      email=request.data.get('email'), password=request.data.get('password'),
                                                      number=None)
            else:
                if Otpveification1.objects.filter(number=request.data.get('number').strip(), otp=request.data.get('otp')).exists():
                    account = Account.objects.create_user(userName=request.data.get('uniId'),
                                                          name=request.data.get('displayName'), email=None,
                                                          password=request.data.get('password'),
                                                          number=request.data.get('number'))
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = AccountSerilizer(account, context={'request': request})
            data = serializer.data
            token = Token.objects.get(user=account).key
            data['token'] = token
            return firebase_account(uni_id=request.data.get('uniId'), firebase_token=request.data.get('firebase'),
                                    data=data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# def getting_user(request):
#     s = request.user
#     print(s.email)
#     print(request.auth)
#     print('hi')
#     return Response(status=status.HTTP_200_OK, data=request.user)


@api_view(['POST'])
def login_in(request):
    if request.method == 'POST':
        s = Account.objects.filter(userName=request.data.get('uniId'),).exists()
        if s:
            a = authenticate(request, username = request.data.get('uniId'), password=request.data.get('password'))
            if a is None:
                return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        loginaccount = Account.objects.get(userName=request.data.get('uniId'))
        token = Token.objects.get(user=loginaccount).key
        serializer = AccountSerilizer(loginaccount, context={'request':request})
        data = serializer.data
        data['token'] = token
        return firebase_account(uni_id=request.data.get('uniId'), firebase_token=request.data.get('firebase'),
                                data=data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def sending_otp(request):
    if request.method == 'POST':
        if Account.objects.filter(userName=request.data.get('uniId')).exists():
            return Response(status=status.HTTP_205_RESET_CONTENT)
        if Account.objects.filter(number=request.data.get('number')).exists():
            return Response(status= status.HTTP_226_IM_USED)
        else:
            try:
                number = "+91"+request.data.get('number')
                otp = random.choice(lis)
                conn = http.client.HTTPConnection("2factor.in")
                payload = ""
                headers = {'content-type': "application/x-www-form-urlencoded"}
                factor = "/API/V1/da764a2a-a1a6-11eb-80ea-0200cd936042/SMS/{number}/{otp}".format(number=number,
                                                                                                  otp=otp)
                conn.request("GET", factor, payload, headers)
                res = conn.getresponse()
                if Otpveification1.objects.filter(number=request.data.get('number')).exists():
                    otpinstance = Otpveification1.objects.get(number=request.data.get('number'))
                    otpinstance.otp = otp
                else:
                    otpinstance = Otpveification1(number=request.data.get('number'), otp=otp)
                otpinstance.save()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def checking_credential(request):
    if request.method == 'POST':
        try:
            cheking_id = Account.objects.get(userName=request.data.get('uniId'))
            token = Token.objects.get(user=cheking_id).key
            if token == request.data.get('token'):
                device = devicetoken.objects.get(userName=cheking_id.userName)
                device.fcm_token = request.data.get('firebase')
                device.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status = status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def sending_otp2(request):
    if request.method == 'POST':
        try:
            number = "+91" + request.data.get('number')
            otp = random.choice(lis)
            conn = http.client.HTTPConnection("2factor.in")
            payload = ""
            headers = {'content-type': "application/x-www-form-urlencoded"}
            factor = "/API/V1/da764a2a-a1a6-11eb-80ea-0200cd936042/SMS/{number}/{otp}".format(number=number,
                                                                                              otp=otp)
            conn.request("GET", factor, payload, headers)
            res = conn.getresponse()
            try:
                Otpveification1.objects.get(number=request.data.get('number')).delete()
            finally:
                otpinstance = Otpveification1(number=request.data.get('number'), otp=otp)
                otpinstance.save()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def sending_otp3(request):
    if request.method == 'POST' and Account.objects.filter(number=request.data.get('number')).exists():
        try:
            number = "+91" + request.data.get('number')
            otp = random.choice(lis)
            conn = http.client.HTTPConnection("2factor.in")
            payload = ""
            headers = {'content-type': "application/x-www-form-urlencoded"}
            factor = "/API/V1/da764a2a-a1a6-11eb-80ea-0200cd936042/SMS/{number}/{otp}".format(number=number,
                                                                                              otp=otp)
            conn.request("GET", factor, payload, headers)
            res = conn.getresponse()
            try:
                Otpveification1.objects.get(number=request.data.get('number')).delete()
            finally:
                otpinstance = Otpveification1(number=request.data.get('number'), otp=otp)
                otpinstance.save()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def set_pass(request):
    if request.method == 'POST':
        if Otpveification1.objects.filter(number=request.data.get('number').strip(), otp=request.data.get('otp')).exists():
            loginaccount = Account.objects.get(number=request.data.get('number'))
            loginaccount.set_password(request.data.get('pass'))
            loginaccount.save()
            token = Token.objects.get(user=loginaccount).key
            serializer = AccountSerilizer(loginaccount, context={'request': request})
            data = serializer.data
            data['token'] = token
            return firebase_account(uni_id=loginaccount.userName, firebase_token=request.data.get('firebase'),
                                    data=data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)