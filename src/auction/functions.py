from auction.models import Auctions, Bidding, Items
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def increase_bid(user, auction):
      
    bid = Bidding()
    bid.user_id = user
    bid.auction_id = auction
    bid.bidding_time = timezone.now()
    bid.item_id = auction.item_id
    bid.save()
    auction.bids += 1
    auction.time_left = timezone.now() + timedelta(minutes=7)
    auction.save()

def remaining_time(auctions):
 
    time_left = auctions.time_left - timezone.now()
    days, seconds = time_left.days, time_left.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    time_left = str(minutes) + "m " + str(seconds) + "s"
    expired = days
    
    return time_left, expired

def validate_login(username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
        return True
    else:
        return False

