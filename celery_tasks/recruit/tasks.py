from celery_tasks.main import app
from runmyScrapy import get_tencent_position, get_lagou_position


@app.task(name='tencent_recruit')
def tencent_recruit():
    get_tencent_position()


@app.task(name='lagou_recruit')
def lagou_recruit(city, keyword, pageSise):
    get_lagou_position(city, keyword, pageSise)