from django import template
from home.models import Cart, Guest

register = template.Library()


@register.filter
def cart_item_count(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)
    else:
        device = request.COOKIES.get("device")
        guest, created = Guest.objects.get_or_create(device=device)
        cart, created = Cart.objects.get_or_create(guest=guest, ordered=False)        
    return cart.items.count()
    
