import os
from celery.schedules import crontab

username = os.getenv("RABBITMQ_DEFAULT_USER")
password = os.getenv("RABBITMQ_DEFAULT_USER")

broker_url = f'pyamqp://{username}:{password}@rabbitmq//'
result_backend = 'elasticsearch://elasticsearch:9200/tasks/task'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'America/Sao_Paulo'
enable_utc = False
include = ['tasks.celerytasks']

# populate_db 30 08
# google_forms 45 08
# gsheet_report 50 08
# send_notification 00 09
beat_schedule = {
    'seed_db': {
        'task': 'tasks.celerytasks.seed_db',
        'schedule': crontab(hour=8, minute=30,
                            day_of_week='wed'),
        'args': ()
    },
    'seed_google_forms': {
        'task': 'tasks.celerytasks.seed_google_forms',
        'schedule': crontab(hour=8, minute=45,
                            day_of_week='wed'),
        'args': ()
    },
    'seed_gsheet_report': {
        'task': 'tasks.celerytasks.seed_gsheet_report',
        'schedule': crontab(hour=8, minute=50,
                            day_of_week='wed'),
        'args': ()
    },
    'send_notification': {
        'task': 'tasks.celerytasks.send_notification',
        'schedule': crontab(hour=9, minute=00,
                            day_of_week='wed'),
        'args': ()
    },
}
