from celery import Celery

app = Celery()
app.config_from_object('tasks.celeryconfig')


if __name__ == '__main__':
    app.start()
