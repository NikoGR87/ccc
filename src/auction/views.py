from django.shortcuts import render

from django.http import HttpResponseRedirect
########################
from django.utils import timezone

from datetime import datetime, timedelta


from itertools import chain

from auction.functions import increase_bid, remaining_time,validate_registration,validate_login ####

#####
from django.contrib.auth.models import User
#####

from auction.forms import *

from auction.models import Items, Auctions, Bidding, Monitoring 


from django.template import RequestContext




############################




# Create your views here.

from rest_framework import viewsets 

#from .models import User

#from .serializers import UserSerializer

from .models import Items

from .serializers import ItemsSerializer

from .models import Auctions
 
from .serializers import AuctionsSerializer

from .models import Bidding
 
from .serializers import BiddingSerializer 

from .models import Monitoring
 
from .serializers import MonitoringSerializer

#class UserViewSet(viewsets.ModelViewSet): 
    
 #   queryset = User.objects.all() 
    
#    serializer_class = UserSerializer

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


# Create your views here. 

def index(request): #server takes a request 
       
    auctions = Auctions.objects.filter(time_left__gte=datetime.now())
       
    try:
        if request.session['username']:
            user = User.objects.get(username=request.session['username'])
   
            m = Monitoring.objects.filter(user_id=user)
            monitoring = Auctions.objects.none()
            
            for item in m:
                
                a = Auctions.objects.filter(id=item.auction_id.id)
                
                monitoring = list(chain(monitoring, a))

            #userDetails = UserDetails.objects.get(user_id=user.id)
        
            return render(request, 'index.html',
                {'auctions': auctions,'monitoring': monitoring})
    
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
                stats.append(winner[0].username)
            else:
                stats.append(None)

            # Fourth element in stats list
            #chat = Chat.objects.all().order_by('time_sent')
            #stats.append(chat)

            # Getting user's monitoring.
            w = Monitoring.objects.filter(user_id=user[0])
            monitoring = Auctions.objects.none()
            for item in w:
                a = Auctions.objects.filter(id=item.auction_id.id)
                monitoring = list(chain(monitoring, a))

            return render(request, 'bidding.html',
            {
                'auctions': auctions[0],
                'user': user[0],
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
            #userDetails = UserDetails.objects.filter(user_id=user.id)
            #if userDetails.balance > 0.0:
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
    if category == "NEW":
        f_auctions = Auctions.objects.filter(
            time_left__gte=datetime.now(), item_id__status="NEW"
            ).order_by('time_start')
    #f_auctions = Auctions.objects.all()

    elif category == "USED":
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
            print(1)
            return render(request, 'index.html', {'auctions': f_auctions, 'user': user[0], 'monitoring': monitoring})
    #return render(request, 'index.html', {'auctions': f_auctions, 'monitoring': monitoring})
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
    
def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            is_valid = validate_registration(
                form.cleaned_data['username'],
                form.cleaned_data['password1'],    
            )
            if is_valid:
                # Create an User object with the form parameters.
                user = User.objects.create_user(username=form.cleaned_data['username'],                                                
                                                password=form.cleaned_data['password1'])                
                user.save()  # Save the object to the database.
                #userDetails = UserDetails()
                #userDetails.user_id = user
                #userDetails.save()
    return index(request) 

def items_page(request):
    item_instance = Items()
    if request.method == 'POST':
        form = ItemsForm(request.POST)
        if form.is_valid():
            
            item_instance.item_title  =   form.cleaned_data['item_title'] 
            item_instance.item_description  =  form.cleaned_data['item_description']
            item_instance.item_owner  =  form.cleaned_data['item_owner']           
            item_instance.status  =  form.cleaned_data['status']
            item_instance.save() 
            
            c = Auctions()
            d = Items.objects.filter(id=item_instance.id)
            c.item_id = d[0]
            c.bids = 0
            c.auction_bidding_price = form.cleaned_data['auction_bidding_price']
            c.time_start  = timezone.now() + timedelta(minutes=1)
            c.time_left = timezone.now() + timedelta(minutes=360)
            c.auction_status = 'OPEN'
            c.save()
            
            
            
            return HttpResponseRedirect('http://193.61.36.93:8000/')
    
    else:
        test1 = ''
        test2 = ''
        test3 = ''
        test4 = ''
        test5 = ''
        form = ItemsForm(initial={'item_title': test1,'item_description': test2,'item_owner ': test3,'status':test4,'auction_bidding_price':test5})  
    
    
    
    context = {
        'form': form,
        'item_instance': item_instance,
    }        

    return render(request, 'items.html',context)
     
def availableitems(request): 
    
    items_list = Items.objects.all() # SELECT ALL!     
    
    return render(request,'availableitems.html',{'items':items_list})

def itemssold_page(request):
    
    f_auctions = []
    #if category == "OPEN":
    f_auctions = Auctions.objects.filter(
        time_left__gte=datetime.now(), auction_status="COMPLETED"
        ).order_by('time_start')
    #f_auctions = Auctions.objects.all()

    #elif category == "COMPLETED":
    #    f_auctions = Auctions.objects.filter(
    #        time_left__gte=datetime.now(), auction_status="COMPLETED"
    #       ).order_by('time_start')

    try:
        if request.session['username']:
            auctions = Auctions.objects.filter(time_left__gte=datetime.now()).order_by('time_start')
            user = User.objects.filter(username=request.session['username'])

            m = Monitoring.objects.all() #filter(user_id=user[0])
            monitoring = Auctions.objects.none()
            for item in m:
                a = Auctions.objects.filter(id=item.auction_id.id)
                monitoring = list(chain(monitoring, a))
            print(1)
            return render(request, 'index.html', {'auctions': f_auctions, 'user': user[0], 'monitoring': monitoring})
   
    except:
        return render(request, 'index.html', {'auctions': f_auctions})

    return index(request) 
    
def historicalbids_page(request):

    return index(request) 


    
