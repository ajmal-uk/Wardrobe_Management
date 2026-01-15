from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import *
from wardrobe.models import *
from django.shortcuts import *
from django.db.models import Q
from . import views 
from orders.models import OrderItem, Order






@role_required('supplier')
def supplier_home(request):
    return render(request, 'supplier/supplier_home.html')


def manage_accessories(request):
    accessories = Accessory.objects.filter(supplier=request.user)
    return render(request, 'supplier/manage.html', {
        'accessories': accessories
    })


@role_required('supplier')
def update_stock(request, accessory_id):
    if request.method == 'POST':
        accessory = get_object_or_404(
            Accessory,
            id=accessory_id,
            supplier=request.user
        )
        accessory.stock = int(request.POST.get('stock', accessory.stock))
        accessory.save()
    return redirect('manage_accessories')


@role_required('supplier')
def delete_accessory(request, accessory_id):
    if request.method == 'POST':
        accessory = get_object_or_404(
            Accessory,
            id=accessory_id,
            supplier=request.user
        )
        accessory.delete()
    return redirect('manage_accessories')


@role_required('supplier')
def edit_accessory(request, accessory_id):
    accessory = get_object_or_404(
        Accessory,
        id=accessory_id,
        supplier=request.user
    )

    if request.method == 'POST':
        accessory.name = request.POST['name']
        accessory.price = request.POST['price']
        accessory.category = request.POST['category']
        accessory.save()
        return redirect('manage_accessories')

    return render(request, 'supplier/edit_accessory.html', {
        'accessory': accessory
    })

@role_required('supplier')
def supplier_orders(request):
    items = OrderItem.objects.filter(
        accessory__supplier=request.user
    ).select_related('order', 'accessory')

    return render(request, 'supplier/supplier_orders.html', {
        'items': items
    })


@role_required('supplier')
def mark_shipped(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'ordered':
        order.status = 'shipped'
        order.save()

    return redirect('supplier_orders')

@role_required('supplier')
def add_accessories(request):
    return render(request, 'supplier/add_accessories.html')





@login_required
def shop_accessories(request):
    accessories = Accessory.objects.filter(is_active=True, stock__gt=0)
    categories = Category.objects.all()

    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        accessories = accessories.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query)
        )

    if category:
        accessories = accessories.filter(category=category)

    return render(request, 'user/shop.html', {
        'accessories': accessories,
        'categories': categories
    })