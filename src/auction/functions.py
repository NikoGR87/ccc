from auction.models import Auctions, Bidding
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import authenticate

def increase_bidding(user, auction):
    
    # The function creates the record for the Bidding Table
    #It is increasing the auction's number of bids and updating the time which is left     
    
    bidding = Bidding()
    bidding.user_id = user
    bidding.auction_id = auction
    bidding.bidding_time = timezone.now()
    bidding.item_id = auction.item_id
    bidding.save()
    auction.bids += 1
    auction.time_left = timezone.now() + timedelta(minutes=7)
    auction.save()

def remaining_time(auctions):
 
    #Calculation of the remaining time of the auction
        
    time_remaining = auctions.time_left - timezone.now()
    days, seconds = time_remaining.days, time_remaining.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    time_remaining = str(minutes) + "m " + str(seconds) + "s"
    expiration = days
    
    return time_remaining, expiration

def validate_login(username, password):
    
    #Checks if the user exists in the system
    
    user = authenticate(username=username, password=password)
    if user is not None:
        return True
    else:
        return False

