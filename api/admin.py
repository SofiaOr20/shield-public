from django.contrib import admin
from api.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Store)
admin.site.register(Car)
admin.site.register(Cookies)
admin.site.register(CookiesToSent)
admin.site.register(Request)
admin.site.register(Delivery)
