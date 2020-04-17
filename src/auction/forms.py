from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
    
    username = forms.CharField(max_length=60)

    password1 = forms.CharField(max_length=60)

class LoginForm(forms.Form):
    
    username = forms.CharField(max_length=60)
    
    password = forms.CharField(max_length=60)
    
class ItemsForm(forms.Form):
  
    STATUS_CHOICES = ( 
    	('NEW', 'New'), 
    	('USED', 'Used'),  
    )
       
    item_title = forms.CharField()
    
    status = forms.ChoiceField(choices = STATUS_CHOICES)
        
    item_description = forms.CharField()
    
    auction_bidding_price = forms.IntegerField()

class ItemsFilterForm(forms.Form):

    select_user = forms.CharField()