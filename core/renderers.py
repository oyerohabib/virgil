from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from .models import *


def render_station(notification):
    data = notification.data
    station_list = Station.objects.values('id', 'name').get(pk=data['station_id'])
    data['station_name'] = escape(station_list['name'])
    message = _('<strong>Station Added with success!</strong> %(created)s created, %(updated)s updated') % data
    return mark_safe(message)


def render_transaction(notification):
    data = notification.data
    transaction_list = Transaction.objects.values('id', 'price').get(pk=data['transaction_id'])
    data['transaction_price'] = escape(transaction_list['price'])
    message = _('<strong>Station Added with success!</strong> %(created)s created, %(updated)s updated') % data
    return mark_safe(message)