from auction.models import Auctions, Bidding, Items

from django.utils import timezone

from datetime import datetime, timedelta


from django.contrib.auth.models import User

from django.contrib.auth import authenticate



def increase_bid(user, auction):
    """
    Removes €1.0 from user.
    Creates a Bid record
    Increases the auction's number of bids
    Parameters
    ----------
    auction : class 'website.models.Auction
    """
    #userDetails = UserDetails.objects.filter(user_id=user.id)
    #userDetails.balance = float(user.balance) - 1.0
    #user.save()
    bid = Bidding()
    bid.user_id = user
    bid.auction_id = auction
    bid.bidding_time = timezone.now()
    bid.item_id = auction.item_id
    bid.save()
    auction.bids += 1
    auction.time_left = timezone.now() + timedelta(minutes=360)
    auction.save()

def remaining_time(auctions):
    """
    Calculates the auction's remaining time
    in minutes and seconds and converts them 
    into a string.
    
    Parameters
    ----------
    auction : class 'website.models.Auction
    
    Returns
    -------
    
    time_left : str
        string representation of remaining time in
        minutes and seconds.
    expired : int
        if the value is less than zero then the auction ended.
    
    """
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

def validate_registration(username, password1):
    user = User.objects.filter(username=username)

    if user:
        print('User already exists')
        return False
    return True

def populate_item(itemtitle,itemdescription,itemowner):
    a = Items()
    a.item_title = itemtitle
    a.item_description = itemdescription
    a.item_owner = itemowner
    
    a.save()
