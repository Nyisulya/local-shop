from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.pos_login, name='login'),
    path('logout/', views.pos_logout, name='logout'),
    path('attendant/', views.attendant_dashboard, name='attendant'),
    path('cashier/', views.cashier_dashboard, name='cashier'),
    path('dispatcher/', views.dispatcher_dashboard, name='dispatcher'),
    path('boss/', views.boss_dashboard, name='boss'),
    path('store/', views.store_dashboard, name='store'),
    
    # API
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/add/', views.api_add_product, name='api_add_product'),
    path('api/order/create/', views.api_create_order, name='api_create_order'),
    path('api/orders/pending/', views.api_pending_orders, name='api_pending_orders'),
    path('api/order/<int:order_id>/pay/', views.api_pay_order, name='api_pay_order'),
    path('api/orders/cashier_paid/', views.api_cashier_paid_orders, name='api_cashier_paid_orders'),
    path('api/orders/paid/', views.api_paid_orders, name='api_paid_orders'),
    path('api/order/<int:order_id>/dispatch/', views.api_dispatch_order, name='api_dispatch_order'),
]
