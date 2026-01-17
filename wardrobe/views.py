from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import WardrobeItem, Category, Occasion, Season


@role_required('user')
def wardrobe_home(request):
    items = WardrobeItem.objects.filter(user=request.user)
    return render(request, 'user/manage_wardrobe.html', {'items': items})


@role_required('user')
def add_wardrobe(request):
    categories = Category.objects.all()
    occasions = Occasion.objects.all()
    seasons = Season.objects.all()

    if request.method == 'POST':
        WardrobeItem.objects.create(
            user=request.user,
            item_type=request.POST.get('item_type'),
            category_id=request.POST.get('category'),
            color=request.POST.get('color'),
            occasion_id=request.POST.get('occasion'),
            season_id=request.POST.get('season'),
            image=request.FILES.get('image')
        )
        return redirect('wardrobe_home')

    return render(request, 'user/add_wardrobe.html', {
        'categories': categories,
        'occasions': occasions,
        'seasons': seasons
    })


@role_required('user')
def delete_wardrobe(request, item_id):
    item = get_object_or_404(WardrobeItem, id=item_id, user=request.user)
    item.delete()
    return redirect('wardrobe_home')


@login_required
def view_clothes(request):
    categories = Category.objects.all()
    items = WardrobeItem.objects.filter(user=request.user)

    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)

    return render(request, 'user/view_clothes.html', {
        'items': items,
        'categories': categories
    })


@role_required('user')
def mark_as_worn(request, item_id):
    item = get_object_or_404(WardrobeItem, id=item_id, user=request.user)
    item.mark_worn()
    return redirect('view_clothes')


@role_required('user')
def send_to_laundry(request, item_id):
    item = get_object_or_404(
        WardrobeItem,
        id=item_id,
        user=request.user
    )
    item.clean_status = False
    item.save()
    return redirect('view_clothes')


@role_required('user')
def laundry_list(request):
    laundry_items = WardrobeItem.objects.filter(
        user=request.user,
        clean_status=False
    )
    return render(request, 'user/laundry_list.html', {
        'laundry_items': laundry_items
    })

@role_required('user')
def mark_as_clean(request, item_id):
    item = get_object_or_404(
        WardrobeItem,
        id=item_id,
        user=request.user
    )
    item.clean_status = True
    item.wear_count = 0
    item.save()
    return redirect('laundry_list')
