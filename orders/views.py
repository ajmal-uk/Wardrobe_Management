from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from accessories.models import Accessory
from django.db.models import Q
from django.shortcuts import render, redirect
from django.shortcuts import render



@login_required
def place_order(request):
    if request.method == 'POST':
        accessory_id = request.POST.get('accessory_id')
        quantity = int(request.POST.get('quantity', 1))

        accessory = get_object_or_404(Accessory, id=accessory_id)

        if quantity > accessory.stock or quantity <= 0:
            return redirect('shop_accessories')

        total_amount = accessory.price * quantity

       
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount
        )

    
        OrderItem.objects.create(
            order=order,
            accessory=accessory,
            quantity=quantity,
            price=accessory.price
        )

      
        accessory.stock -= quantity
        accessory.save()

   
    return redirect(request.META.get('HTTP_REFERER', 'shop_accessories'))

def checkout(request):
    if request.method == 'POST':
        accessory = get_object_or_404(
            Accessory, id=request.POST['accessory_id']
        )
        quantity = int(request.POST['quantity'])

        if quantity > accessory.stock:
            return redirect('shop_accessories')

        total = accessory.price * quantity

        request.session['order_data'] = {
            'accessory_id': accessory.id,
            'quantity': quantity,
            'total': float(total)
        }

        return render(request, 'user/checkout.html', {
            'accessory': accessory,
            'quantity': quantity,
            'total': total
        })

def place_order(request):
    data = request.session.get('order_data')

    if not data:
        return redirect('shop_accessories')

    accessory = get_object_or_404(Accessory, id=data['accessory_id'])
    quantity = data['quantity']

    if quantity > accessory.stock:
        return redirect('shop_accessories')

    order = Order.objects.create(
        user=request.user,
        total_amount=accessory.price * quantity
    )

    OrderItem.objects.create(
        order=order,
        accessory=accessory,
        quantity=quantity,
        price=accessory.price
    )

    accessory.stock -= quantity
    accessory.save()

    del request.session['order_data']

    return render(request, 'user/bill.html', {
        'order': order
    })