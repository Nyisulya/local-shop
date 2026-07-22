import json
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Product, Order, OrderItem, POSUser, ActivityLog
from django.db import transaction
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import Coalesce
from .decorators import pos_login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def pos_login(request):
    next_url = request.GET.get('next', 'home')
    # If already logged in, redirect to next_url
    if request.session.get('pos_user_id'):
        return redirect(next_url)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        pin = request.POST.get('pin')
        if not user_id or not pin:
            messages.error(request, 'Tafadhali chagua mtumiaji na uingize PIN.')
            return redirect(f'/login/?next={next_url}')
        try:
            user = POSUser.objects.get(id=user_id)
            if check_password(pin, user.pin):
                request.session['pos_user_id'] = user.id
                return redirect(next_url)
            else:
                messages.error(request, 'PIN sio sahihi. Jaribu tena.')
        except POSUser.DoesNotExist:
            messages.error(request, 'Mtumiaji si halali.')
        return redirect(f'/login/?next={next_url}')
        
    users = POSUser.objects.all().order_by('name')
    return render(request, 'login.html', {'users': users, 'next': next_url})

def pos_logout(request):
    if 'pos_user_id' in request.session:
        del request.session['pos_user_id']
    return redirect('login')

@pos_login_required(allowed_roles=['attendant'])
def attendant_dashboard(request):
    return render(request, 'attendant.html')

@pos_login_required(allowed_roles=['cashier'])
def cashier_dashboard(request):
    return render(request, 'cashier.html')

@pos_login_required(allowed_roles=['dispatcher'])
def dispatcher_dashboard(request):
    return render(request, 'dispatcher.html')

@pos_login_required(allowed_roles=['admin'])
def boss_dashboard(request):
    total_revenue = Order.objects.filter(status__in=['paid', 'dispatched']).aggregate(total=Sum('grand_total'))['total'] or 0.00
    
    profit_calc = Sum(
        ExpressionWrapper(
            (F('items__unit_price') - F('items__unit_cost_price')) * F('items__quantity'),
            output_field=DecimalField()
        )
    )
    total_profit = Order.objects.filter(status__in=['paid', 'dispatched']).aggregate(profit=profit_calc)['profit'] or 0.00
    
    recent_orders_list = Order.objects.filter(status__in=['paid', 'dispatched']).select_related('created_by', 'processed_by', 'dispatched_by').order_by('-created_at')
    
    activity_logs_list = ActivityLog.objects.select_related('user').order_by('-timestamp')
    
    # Pagination for Orders (10 per page)
    paginator_orders = Paginator(recent_orders_list, 10)
    page_orders = request.GET.get('page_orders')
    recent_orders = paginator_orders.get_page(page_orders)
    
    # Pagination for Logs (15 per page)
    paginator_logs = Paginator(activity_logs_list, 15)
    page_logs = request.GET.get('page_logs')
    activity_logs = paginator_logs.get_page(page_logs)
    
    context = {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'recent_orders': recent_orders,
        'activity_logs': activity_logs,
    }
    return render(request, 'boss_dashboard.html', context)

@pos_login_required(allowed_roles=['admin'])
def store_dashboard(request):
    products = Product.objects.all().order_by('name')
    
    # Low stock (between 1 and 9)
    low_stock_products = products.filter(stock_quantity__gt=0, stock_quantity__lt=10)
    low_stock_count = low_stock_products.count()
    
    # Out of stock (0 or less)
    out_of_stock_products = products.filter(stock_quantity__lte=0)
    out_of_stock_count = out_of_stock_products.count()
    
    # Sales volume calculation (fast/slow moving)
    # Only counting orders that are paid or dispatched
    products_with_sales = Product.objects.annotate(
        total_sold=Coalesce(
            Sum('orderitem__quantity', filter=Q(orderitem__order__status__in=['paid', 'dispatched'])),
            0
        )
    )
    
    # Fast moving (Top 3 by volume)
    fast_moving = products_with_sales.filter(total_sold__gt=0).order_by('-total_sold')[:3]
    
    # Slow moving (Bottom 3 by volume)
    slow_moving = products_with_sales.order_by('total_sold', 'name')[:3]
    
    context = {
        'products': products,
        'low_stock_products': low_stock_products[:3], # Just pass top 3 for the card
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'fast_moving': fast_moving,
        'slow_moving': slow_moving,
    }
    return render(request, 'store_dashboard.html', context)

# API Endpoints

@pos_login_required()
def api_products(request):
    products = Product.objects.all().values('id', 'name', 'price', 'stock_quantity')
    return JsonResponse({'products': list(products)})

@csrf_exempt
@require_http_methods(["POST"])
@pos_login_required(allowed_roles=['attendant'])
def api_create_order(request):
    try:
        data = json.loads(request.body)
        customer_name = data.get('customer_name')
        items = data.get('items', [])
        
        if not customer_name or not items:
            return JsonResponse({'error': 'Invalid data'}, status=400)
            
        with transaction.atomic():
            order = Order.objects.create(customer_name=customer_name, status='pending', created_by=request.pos_user)
            total = 0
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                qty = int(item['quantity'])
                price = product.price
                total += price * qty
                OrderItem.objects.create(order=order, product=product, quantity=qty, unit_price=price, unit_cost_price=product.cost_price)
            
            order.grand_total = total
            order.save()
            
            ActivityLog.objects.create(
                user=request.pos_user,
                action=f"Ametengeneza oda mpya kwa ajili ya {order.customer_name} (Jumla: Tsh {order.grand_total})"
            )
            
        return JsonResponse({'success': True, 'order_id': order.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@pos_login_required(allowed_roles=['admin'])
def api_add_product(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        price = data.get('price')
        cost_price = data.get('cost_price', 0.00)
        stock = data.get('stock')
        
        if not name or price is None or stock is None:
            return JsonResponse({'error': 'Taarifa hazijakamilika'}, status=400)
            
        product = Product.objects.create(
            name=name,
            price=price,
            cost_price=cost_price,
            stock_quantity=stock
        )
        ActivityLog.objects.create(
            user=request.pos_user,
            action=f"Ameongeza bidhaa mpya: {product.name} (Idadi: {product.stock_quantity})"
        )
        return JsonResponse({'success': True, 'product_id': product.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@pos_login_required(allowed_roles=['cashier'])
def api_pending_orders(request):
    orders = Order.objects.filter(status='pending').order_by('created_at')
    result = []
    for o in orders:
        items = [{'name': i.product.name, 'qty': i.quantity, 'price': i.unit_price} for i in o.items.all()]
        result.append({
            'id': o.id,
            'customer_name': o.customer_name,
            'grand_total': o.grand_total,
            'items': items
        })
    return JsonResponse({'orders': result})

@csrf_exempt
@require_http_methods(["POST"])
@pos_login_required(allowed_roles=['cashier'])
def api_pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='pending')
    order.status = 'paid'
    order.processed_by = request.pos_user
    order.generate_token() # also calls save()
    
    ActivityLog.objects.create(
        user=request.pos_user,
        action=f"Amepokea malipo ya oda #{order.id} (Tsh {order.grand_total})"
    )
    return JsonResponse({
        'success': True,
        'token': order.token,
        'order_id': order.id
    })

@pos_login_required(allowed_roles=['cashier'])
def api_cashier_paid_orders(request):
    # Fetch recently paid orders that haven't been dispatched yet (for reprinting)
    orders = Order.objects.filter(status='paid').order_by('-created_at')[:10]
    result = []
    for o in orders:
        items = [{'name': i.product.name, 'qty': i.quantity, 'price': i.unit_price} for i in o.items.all()]
        result.append({
            'id': o.id,
            'customer_name': o.customer_name,
            'grand_total': o.grand_total,
            'token': o.token,
            'items': items,
            'created_at': o.created_at.isoformat()
        })
    return JsonResponse({'orders': result})

@pos_login_required(allowed_roles=['dispatcher'])
def api_paid_orders(request):
    orders = Order.objects.filter(status='paid').order_by('created_at')
    result = []
    for o in orders:
        items = [{'name': i.product.name, 'qty': i.quantity} for i in o.items.all()]
        result.append({
            'id': o.id,
            'customer_name': o.customer_name,
            'items': items
        })
    return JsonResponse({'orders': result})

@csrf_exempt
@require_http_methods(["POST"])
@pos_login_required(allowed_roles=['dispatcher'])
def api_dispatch_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='paid')
    data = json.loads(request.body)
    token = data.get('token')
    
    if order.token != token:
        return JsonResponse({'error': 'Invalid token'}, status=403)
        
    with transaction.atomic():
        # Decrement inventory
        for item in order.items.all():
            product = item.product
            product.stock_quantity -= item.quantity
            product.save()
            
        order.status = 'dispatched'
        order.dispatched_by = request.pos_user
        order.save()
        
        ActivityLog.objects.create(
            user=request.pos_user,
            action=f"Amesafirisha oda #{order.id}"
        )
        
    return JsonResponse({'success': True})
