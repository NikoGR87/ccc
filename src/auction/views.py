from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import datetime, timedelta
from itertools import chain
from auction.functions import increase_bid, remaining_time, validate_login 
from auction.forms import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from users.serializers import CreateUserSerializer
from rest_framework import viewsets 
from .models import Items, Auctions, Bidding, Monitoring
from .serializers import ItemsSerializer, AuctionsSerializer, BiddingSerializer, MonitoringSerializer 
from django.contrib import messages
from django.core import serializers
from django.core import validators
from django.core.exceptions import ValidationError

import requests

class ItemsViewSet(viewsets.ModelViewSet):
    
    queryset = Items.objects.all().order_by('item_title')
    
    serializer_class = ItemsSerializer

class AuctionsViewSet(viewsets.ModelViewSet): 
    
    queryset = Auctions.objects.all() 
    
    serializer_class = AuctionsSerializer   

class BiddingViewSet(viewsets.ModelViewSet): 
    
    queryset = Bidding.objects.all() 
    
    serializer_class = BiddingSerializer
    
class MonitoringViewSet(viewsets.ModelViewSet): 
    
    queryset = Monitoring.objects.all() 
    
    serializer_class = MonitoringSerializer

def index(request): 
       
    auctions = Auctions.objects.filter(time_left__gte=datetime.now())
       
    try:
        if request.session['username']:
            user = User.objects.get(username=request.session['username'])
   
            m = Monitoring.objects.filter(user_id=user)
            monitoring = Auctions.objects.none()
            
            for item in m:
                
                a = Auctions.objects.filter(id=item.auction_id.id)
                
                monitoring = list(chain(monitoring, a))

            return render(request, 'index.html',{'auctions': auctions, 'user': user,'monitoring': monitoring})
    
    except KeyError:
        
        return render(request, 'index.html', {'auctions': auctions})
    
    return render(request, 'index.html', {'auctions': auctions})
 
def bid_page(request, auction_id):   
    
    print(type(auction_id))
    
    try:
        # if not logged in return to the index page.
        if request.session['username']:
            # If the auction hasn't started return to the index page.
            auctions = Auctions.objects.filter(id=auction_id)
            if auctions[0].time_start > timezone.now():
                return index(request)
            user = User.objects.filter(username=request.session['username'])

            stats = []
            time_left, expired = remaining_time(auctions[0])
            stats.append(time_left) # First element in stats list

            current_cost = 0.20 + (auctions[0].bids * 0.20)
            current_cost = "%0.2f" % current_cost
            stats.append(current_cost)

            # Second element in stats list
            if expired < 0: # if auction ended append false.
                stats.append(False)
            else:
                stats.append(True)

            # Third element in stats list
            latest_bid = Bidding.objects.all().order_by('-bidding_time')
            if latest_bid:
                winner = User.objects.filter(id=latest_bid[0].user_id.id)
                
                ##################
               
                t = Auctions.objects.filter(id=auction_id)   
                for a in t:        
                    i = Items.objects.filter(id=a.item_id.id).values('item_title')       
                    a.item_name = i
                    a.auction_winner = winner[0].username
                    a.auction_status = "COMPLETED" 
                    a.save() # this will update only

                if request.session['username']:
                    user = User.objects.get(username=request.session['username'])
                biddings = Bidding.objects.filter(user_id = user.id)
                for a in biddings:
                    i = Items.objects.filter(id=a.item_id.id).values('item_title') 
                    a.item_name = i 
                    a.auction_winner = winner[0].username
                    a.save() # this will update only
                
                if request.session['username']:
                    user = User.objects.get(username=request.session['username'])
                biddings = Bidding.objects.filter(user_id = user.id)
                for a in biddings:
                    i = Items.objects.filter(id=a.item_id.id).values('item_owner') 
                    a.item_name = i  
                    a.save() # this will update only
                        
                ####################################
                
                stats.append(winner[0].username)
            else:
                stats.append(None)
       
            # Getting user's monitoring.
            w = Monitoring.objects.filter(user_id=user.id)
            monitoring = Auctions.objects.none()
            for item in w:
                a = Auctions.objects.filter(id=item.auction_id.id)
                monitoring = list(chain(monitoring, a))

            return render(request, 'bidding.html',
            {
                'auctions': auctions[0],
                'user': user,
                'stats': stats,
                'monitoring':monitoring
            })
    except KeyError:
        return index(request)

    return index(request)

def raise_bid(request, auction_id):
   
    auction = Auctions.objects.get(id=auction_id)
    
    if auction.time_left < timezone.now():
        return bid_page(request, auction_id)
    elif auction.time_start > timezone.now():
        return index(request)

    try:
        if request.session['username']:
            user = User.objects.get(username=request.session['username'])
            
            usercondition = request.session['username']
            
            items = Items.objects.filter(item_owner = usercondition)            
            for condition in items: 
                
                print (str(condition))
                if str(condition) == str(usercondition):    
                    raise ValidationError('User cannot bid on own item!')
            
            object_list = serializers.serialize("python", Items.objects.filter(id=auction.item_id.id,item_owner = usercondition))
            for object in object_list:
                for field_name, field_value in object['fields'].items():
                    print (field_name, field_value)
                    if str(field_value) == str(usercondition):    
                        raise ValidationError('User cannot bid on own item!')
            
            latest_bid = Bidding.objects.filter(auction_id=auction.id).order_by('-bidding_time')
            if not latest_bid:
                increase_bid(user, auction)
            else:
                current_winner = User.objects.filter(id=latest_bid[0].user_id.id)
                if current_winner[0].id != user.id:
                    increase_bid(user, auction)

            return bid_page(request, auction_id)
    except KeyError:
        return index(request)

    return bid_page(request, auction_id)
    
def monitoring(request, auction_id):
    
    try:
        if request.session['username']:
            user = User.objects.filter(username=request.session['username'])
            auction = Auctions.objects.filter(id=auction_id)

            m = Monitoring.objects.filter(auction_id=auction_id)
            if not m:
                monitoring_item = Monitoring()
                monitoring_item.auction_id = auction[0]
                monitoring_item.user_id = user[0]
                monitoring_item.save()
            else:
                m.delete()

            return index(request)
    except KeyError:
        return index(request)

    return index(request)    

def monitoring_page(request):
    
    try:
        if request.session['username']:
            user = User.objects.filter(username=request.session['username'])
            m = Monitoring.objects.filter(user_id=user[0])

            auctions = Auctions.objects.none()
            for item in m:
                a = Auctions.objects.filter(id=item.auction_id.id, time_left__gte=timezone.now())
                auctions = list(chain(auctions, a))
            return render(request, 'index.html', {
                'auctions': auctions,
                'user': user[0],
                'monitoring':auctions
            })
    except KeyError:
        return index(request)
        
def filter_auctions(request, category):
    
    f_auctions = []
    if category == "new":
        f_auctions = Auctions.objects.filter(
            time_left__gte=datetime.now(), item_id__status="NEW"
            ).order_by('time_start')

    elif category == "used":
        f_auctions = Auctions.objects.filter(
            time_left__gte=datetime.now(), item_id__status="USED"
           ).order_by('time_start')

    try:
        if request.session['username']:
            auctions = Auctions.objects.filter(time_left__gte=datetime.now()).order_by('time_start')
            user = User.objects.filter(username=request.session['username'])

            m = Monitoring.objects.all() #filter(user_id=user[0])
            monitoring = Auctions.objects.none()
            for item in m:
                a = Auctions.objects.filter(id=item.auction_id.id)
                monitoring = list(chain(monitoring, a))
            
            return render(request, 'index.html', {'auctions': f_auctions, 'user': user[0], 'monitoring': monitoring})   
    except:
        return render(request, 'index.html', {'auctions': f_auctions})

    return index(request)            

def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            is_valid = validate_login(
                form.cleaned_data['username'], 
                form.cleaned_data['password']
            )
            if is_valid :
                # Creates a session with 'form.username' as key.
                request.session['username'] = form.cleaned_data['username']
    return index(request)

def logout_page(request):
    try:
        del request.session['username']
    except:
        pass # if there is no session pass
    return index(request)


def registration_page(request):
    
    return render(request, 'registration.html')
    
@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    CLIENT_ID = '9dGBsdHYqLICRZC4gKoNa57dkiHPIvh4PtxXZ0l5'
    CLIENT_SECRET = 'OU3LF7o9xGd1TuRvi5UBnrrUUQdd96uPBWqISAltkWArg4M8vANV0gSYplQ0uPtltcR71mjguqyS3axJKqPwMrFibr7SWVAQ4rC8QZzDMvcRNWnFuQJAvfd4fL3iyCyR'


    IP_token = 'http://193.61.36.93:8000/o/token/'
    IP_revoke_token ='http://193.61.36.93:8000/o/revoke_token/'
    
    '''
    Registers user to the server. Input should be in the format:
    {"username": "username", "password": "1234abcd"}
    '''
    # Put the data from the request into the serializer 
    serializer = CreateUserSerializer(data=request.data) 
    # Validate the data
    if serializer.is_valid():
        # If it is valid, save the data (creates a user).
        serializer.save() 
        # Then we get a token for the created user.
        # This could be done differentley 
        r = requests.post(IP_token, 
            data={
                'grant_type': 'password',
                'username': request.data['username'],
                'password': request.data['password'],
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
            },
        )
        #return Response(r.json())
        return index(request)
    return Response(serializer.errors)
    #return render('User already exists')

def items_page(request):
    item = Items()
    if request.method == 'POST':
        form = ItemsForm(request.POST)
        if form.is_valid():
            
            item.item_title  =   form.cleaned_data['item_title'] 
            item.item_description  =  form.cleaned_data['item_description']           
            item.status  =  form.cleaned_data['status']
            item.auction_expiration_time = timezone.now() + timedelta(minutes=360)
            user = User.objects.get(username=request.session['username'])
            item.item_owner = user.username
            item.save() 
            
            auction = Auctions()
            i = Items.objects.filter(id=item.id)
            auction.item_id = i[0]
            auction.bids = 0
            auction.auction_bidding_price = form.cleaned_data['auction_bidding_price']
            auction.time_start  = timezone.now() + timedelta(minutes=1)
            auction.time_left = item.auction_expiration_time
            auction.auction_status = 'OFFERS'
            auction.save()
                      
            messages.success(request, 'Item and auction created!')
            return HttpResponseRedirect('http://193.61.36.93:8000/')
    
    else:
        placeholder1 = ''
        placeholder2 = ''
        placeholder3 = ''
        placeholder4 = ''
        placeholder5 = ''
        form = ItemsForm(initial={'item_title': placeholder1,'item_description': placeholder2,'item_owner ': placeholder3,'status':placeholder4,'auction_bidding_price':placeholder5})  
       
    if request.session['username']:
            user = User.objects.get(username=request.session['username'])
    
    context = {
        'form': form,
        'item': item,
        'user': user
    }        

    return render(request, 'items.html',context)
     
def availableitems(request): 
     
    if request.session['username']:
            user = User.objects.get(username=request.session['username'])
    
    form = ItemsFilterForm()
    if form.is_valid():
        test = form.cleaned_data['select_user']
        items_list = Items.objects.filter(item_owner = test)     
    
        return render(request,'availableitems.html',{'form' : form,'items': items_list}) 
    else:       
        placeholder = User.objects.all()
        form = ItemsFilterForm(initial={'select_user': placeholder})
        form = ItemsFilterForm(request.GET)
        if form.is_valid():
            test = form.cleaned_data['select_user']          
            items_list = Items.objects.filter(item_owner = test) 
    
    if form.is_valid():       
        context = {
            'form': form,
            'items': items_list,
            'user': user
        }
    else:
        context = {
            'form': form,
            'user': user
        }
        
    return render(request, 'availableitems.html',context)


def itemssold_page(request):
       
    if request.session['username']:
            user = User.objects.get(username=request.session['username'])
    
    
    
    #t = Auctions.objects.filter(time_left__lte = datetime.now(), auction_status="OFFERS")    
    #for a in t:        
     #   i = Items.objects.filter(id=a.item_id.id).values('item_title')       
     #   a.item_name = i
     #   a.auction_status = "COMPLETED" # change field
     #   a.save() # this will update only
    
 
    b = Auctions.objects.filter(auction_status="COMPLETED")        
    
    return render(request, 'itemssold.html',{'auctions': b,'user': user})
   
def historicalbids_page(request):

    if request.session['username']:
        user = User.objects.get(username=request.session['username'])
    
    
    bidel = Bidding.objects.filter(item_owner = user.username)
    
  
    return render(request,'historicalbids.html',{'bidding':bidel,'user': user})

def please_delete(request):

    Items.objects.all().delete()
    Auctions.objects.all().delete()

    print('success')
    return render(request, 'index.html')
        


    
