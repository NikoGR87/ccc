from rest_framework import serializers 
from django.contrib.auth.models import User
from .models import Items, Auctions, Bidding, Monitoring 


class UserSerializer(serializers.ModelSerializer):
   
    class Meta:
      
      model = User
      
      fields = ('id', 'username', 'password')

class ItemsSerializer(serializers.ModelSerializer):
   
   class Meta:
      
       model = Items
      
       fields = ('item_title','time_stamp','status','item_description','auction_expiration_time','item_owner')
       
class AuctionsSerializer(serializers.ModelSerializer): 
    
    class Meta:
    
        model = Auctions
        
        fields = ('auction_bidding_price','auction_status','time_start','time_left','auction_winner','item_id','item_name','bids',) 


class BiddingSerializer(serializers.ModelSerializer):
   
   class Meta:
      
       model = Bidding
      
       fields = ('auction_id','user_id','item_id','bidding_time','item_name','auction_winner','item_owner')
       
class MonitoringSerializer(serializers.ModelSerializer):
   
   class Meta:
      
       model = Monitoring
      
       fields = ('user_id','auction_id')      
