from django.db import migrations
from django.contrib.auth.hashers import make_password

def seed_pos_users(apps, schema_editor):
    POSUser = apps.get_model('core', 'POSUser')
    users = [
        {'name': 'Admin User', 'role': 'admin', 'pin': '1234'},
        {'name': 'Attendant User', 'role': 'attendant', 'pin': '1111'},
        {'name': 'Cashier User', 'role': 'cashier', 'pin': '2222'},
        {'name': 'Dispatcher User', 'role': 'dispatcher', 'pin': '3333'},
    ]
    for u in users:
        POSUser.objects.create(
            name=u['name'],
            role=u['role'],
            pin=make_password(u['pin'])
        )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_posuser_order_created_by_order_dispatched_by_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_pos_users),
    ]
