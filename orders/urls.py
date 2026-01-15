from django.urls import path
from .views import place_order
from . import views 


urlpatterns = [
    path('place-order/', place_order, name='place_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('place/', views.place_order, name='place_order'),
]
