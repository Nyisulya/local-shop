from django.contrib import admin
from .models import Product, Order, OrderItem, POSUser

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(POSUser)
class POSUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role')
    list_filter = ('role',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'grand_total', 'token', 'created_by', 'processed_by', 'dispatched_by', 'created_at')
    list_filter = ('status', 'created_at', 'created_by', 'processed_by', 'dispatched_by')
    search_fields = ('customer_name', 'token')
    readonly_fields = ('created_by', 'processed_by', 'dispatched_by')
    inlines = [OrderItemInline]
