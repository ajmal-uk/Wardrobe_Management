from django.urls import path
from .views import place_order
from . import views 


urlpatterns = [
    path('place-order/', place_order, name='place_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('place/', views.place_order, name='place_order'),
      path('my-orders/', views.user_orders, name='user_orders'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
]
