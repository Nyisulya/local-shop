from django.db import migrations

def seed_wholesale_products(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    wholesale_items = [
        {'name': 'Sukari Kilombero (50kg Mfuko)', 'cost_price': 135000.00, 'price': 148000.00, 'stock_quantity': 50},
        {'name': 'Mchele Super Mbeya (50kg Mfuko)', 'cost_price': 125000.00, 'price': 138000.00, 'stock_quantity': 40},
        {'name': 'Unga wa Sembe Dona (25kg Mfuko)', 'cost_price': 32000.00, 'price': 38000.00, 'stock_quantity': 70},
        {'name': 'Ngano Namba 1 Bakhresa (25kg Mfuko)', 'cost_price': 38000.00, 'price': 44000.00, 'stock_quantity': 60},
        {'name': 'Mafuta ya Kula Korie (20L Dumu)', 'cost_price': 85000.00, 'price': 94000.00, 'stock_quantity': 30},
        {'name': 'Sabuni ya Mche Jamaa (Katoni 24)', 'cost_price': 28000.00, 'price': 34000.00, 'stock_quantity': 45},
        {'name': 'Sabuni ya Powder Omo 1kg (Bando 10)', 'cost_price': 45000.00, 'price': 52000.00, 'stock_quantity': 25},
        {'name': 'Azam Energy Drink (Kasha/Treya 24)', 'cost_price': 18000.00, 'price': 22000.00, 'stock_quantity': 90},
        {'name': 'Soda Coca-Cola 350ml (Kasha 24)', 'cost_price': 14000.00, 'price': 17500.00, 'stock_quantity': 80},
        {'name': 'Soda Pepsi 350ml (Kasha 24)', 'cost_price': 13500.00, 'price': 17000.00, 'stock_quantity': 75},
        {'name': 'Maji ya Kandoro 1.5L (Katoni 12)', 'cost_price': 6500.00, 'price': 8500.00, 'stock_quantity': 120},
        {'name': 'Maji ya Kilimanjaro 500ml (Katoni 24)', 'cost_price': 7500.00, 'price': 9500.00, 'stock_quantity': 100},
        {'name': 'Biskuti Mo Extra (Katoni 48)', 'cost_price': 16000.00, 'price': 20000.00, 'stock_quantity': 55},
        {'name': 'Chai ya Kilimanjaro Packets (Katoni 24)', 'cost_price': 22000.00, 'price': 27000.00, 'stock_quantity': 35},
        {'name': 'Maziwa ya Tanga Fresh 500ml (Katoni 12)', 'cost_price': 24000.00, 'price': 29000.00, 'stock_quantity': 40},
        {'name': 'Chumvi ya Mawe Sea Salt (Bando 20)', 'cost_price': 12000.00, 'price': 15500.00, 'stock_quantity': 60},
        {'name': 'Kiberiti cha Farasi (Bando 10)', 'cost_price': 8000.00, 'price': 11000.00, 'stock_quantity': 50},
        {'name': 'Kanga za Mlimani (Bando la Jozi 6)', 'cost_price': 48000.00, 'price': 58000.00, 'stock_quantity': 35},
        {'name': 'Vitenge vya Super Wax (Bando 5)', 'cost_price': 120000.00, 'price': 145000.00, 'stock_quantity': 25},
        {'name': 'Pampers za Watoto Huggies (Katoni 4)', 'cost_price': 55000.00, 'price': 68000.00, 'stock_quantity': 30},
    ]

    for item in wholesale_items:
        Product.objects.create(
            name=item['name'],
            cost_price=item['cost_price'],
            price=item['price'],
            stock_quantity=item['stock_quantity']
        )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_seed_users'),
    ]

    operations = [
        migrations.RunPython(seed_wholesale_products),
    ]
