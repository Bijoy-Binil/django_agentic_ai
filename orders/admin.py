from django.contrib import admin
from  .models import Order,Product,RefundRequest
# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display=["name","price","category","in_stock"]

class OrderAdmin(admin.ModelAdmin):
    list_display=["product_name","status","amount","carrier","tracking_number"]


class RefundRequestAdmin(admin.ModelAdmin):
    list_display=["order","user","status","reason"]


admin.site.register(Order,OrderAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(RefundRequest,RefundRequestAdmin)