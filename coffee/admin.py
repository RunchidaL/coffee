from django.contrib import admin
from coffee.models import Category,Product,Cart,CartItem,Order,OrderItem
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)