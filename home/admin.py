from django.contrib import admin

from .models import *


admin.site.register(Item)
admin.site.register(LineItem)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(UserProfile)
admin.site.register(PlacedOrder)
admin.site.register(Payment)
admin.site.register(Guest)