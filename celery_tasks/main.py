from celery import Celery

app = Celery('myScrapy')
app.config_from_object('celery_tasks.config')
app.autodiscover_tasks(['celery_tasks.recruit'])
