from django.db import models
from django.contrib.auth.models import User
from datetime import datetime 
from django.core import validators
from django.core.exceptions import ValidationError

class Items(models.Model): 

    STATUS_CHOICES = ( 
    	('NEW', 'New'), 
    	('USED', 'Used'),  
    )
       
    item_title = models.CharField(max_length=60)

    time_stamp = models.DateTimeField(auto_now_add=True, blank=True)
 
    status = models.CharField( 
        max_length = 20, 
        choices = STATUS_CHOICES,
        )

    item_description = models.CharField(max_length=60)
    
    auction_expiration_time = models.DateTimeField(default=datetime.now)

    item_owner = models.CharField(max_length=60)
    
class Auctions(models.Model): 
        
    STATUS_AUCTIONS_CHOICES = ( 
            ('OFFERS', 'Offers'), 
            ('COMPLETED', 'Completed'),  
        )    
       
    auction_bidding_price = models.IntegerField()
    
    auction_status = models.CharField( 
        max_length = 20, 
        choices = STATUS_AUCTIONS_CHOICES, 
        )
        
    time_start = models.DateTimeField(default=datetime.now)
    
    time_left = models.DateTimeField()
    
    auction_winner = models.CharField(max_length=60)
    
    item_id = models.ForeignKey(Items, on_delete=models.CASCADE)
    
    item_name = models.CharField(max_length=60,default='')
    
    bids = models.IntegerField()
    
class Bidding(models.Model):

    auction_id = models.ForeignKey(Auctions,on_delete=models.CASCADE,) 
    
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,)
    
    item_id = models.ForeignKey(Items,on_delete=models.CASCADE)
    
    bidding_time = models.DateTimeField(default=datetime.now)
    
    item_name = models.CharField(max_length=60,default='')
    
    auction_winner = models.CharField(max_length=60,default='')
    
    item_owner = models.CharField(max_length=60,default='')
    
class Monitoring(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    auction_id = models.ForeignKey(Auctions, on_delete=models.CASCADE)


    
    
    
    

    
