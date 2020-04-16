from . import views 

from django.urls import path

app_name = 'auction'

urlpatterns = [ 
        
        path('', views.index, name='index'),
        
        path('auction/registration/', views.registration_page, name='registration_page'),
	
        path('auction/registration/new_user/', views.registration, name='registration'),
                   
        path('auction/login/', views.login_page, name='login_view'),
	
        path('auction/logout/', views.logout_page, name='logout_view'),
 
        path('auction/category/<str:category>/', views.filter_auctions, name='filter_auctions'),
    
        path('auction/monitoring/<int:auction_id>/', views.monitoring, name='monitoring'),
        
        path('auction/monitoring/', views.monitoring_page, name='monitoring'),
        
        path('auction/bidding/<int:auction_id>/', views.bid_page, name='bid_page'),
    
        path('auction/bidding/<int:auction_id>/raise_bid/', views.raise_bid, name='raise_bid'),
        
        path('auction/items/', views.items_page, name='items_view'),
        
        path('auction/availableitems/', views.availableitems, name='availableitems_view'),
        
        path('auction/itemssold/', views.itemssold_page, name='itemssold_view'),
        
        path('auction/historicalbids/', views.historicalbids_page, name='historicalbids_view'),   
       
]
