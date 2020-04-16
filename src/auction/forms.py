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
    
    item_owner = forms.CharField()

    #
    auction_bidding_price = forms.IntegerField()
    
    
    
    #auction_expiration_time = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], help_text="(Day/Month/Year Hour:Min)")
    
    
    
