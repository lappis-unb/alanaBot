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
enable_utc = True

beat_schedule = {
    'seed_db': {
        'task': 'tasks.seed_db',
        'schedule': crontab(hour=21, minute=17,
                            day_of_week='mon'),
        'args': ()
    },
}
