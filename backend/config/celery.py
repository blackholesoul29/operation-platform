import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('enerflow')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-document-expiry': {
        'task': 'apps.notificaciones.tasks.check_document_expiry',
        'schedule': crontab(hour=8, minute=0),
    },
    'check-deal-stagnation': {
        'task': 'apps.notificaciones.tasks.check_deal_stagnation',
        'schedule': crontab(hour=9, minute=0),
    },
    'check-contract-unsigned': {
        'task': 'apps.notificaciones.tasks.check_contract_unsigned',
        'schedule': crontab(hour=8, minute=30),
    },
    'check-pending-tasks': {
        'task': 'apps.notificaciones.tasks.check_pending_tasks',
        'schedule': crontab(hour=7, minute=0),
    },
}
