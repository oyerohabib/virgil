from django.utils.translation import gettext_lazy as _


class Actions:
    STATION_COMPLETED = 1
    TRANSACTION_COMPLETED = 2

    ITEMS = {
        STATION_COMPLETED: {
            'label': _('Subscribers import completed'),
            'icon': 'fas fa-user-check',
        },
        TRANSACTION_COMPLETED: {
            'label': _('Subscribers import failed'),
            'icon': 'fas fa-user-times',
        }
    }

    CHOICES = tuple([(key, options['label']) for key, options in ITEMS.items()])