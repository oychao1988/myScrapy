import json
from flask import Flask
from flask import request
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'scrapydb',
    'host': '127.0.0.1',
    'port': 27017,
    'username': 'cino',
    'password': 'cino',
}
db = MongoEngine(app)

# 指纹集合
class FingerPrint(db.Document):
    meta = {
        'collection': 'fingerPrint'
    }
    fp = db.StringField()


@app.route('/duplicateChecking/<fp>', methods=['GET', 'POST'])
def duplicateChecking(fp):
    result = FingerPrint.objects(fp=fp)
    # GET查询指纹
    if request.method == 'GET':
        if result:
            # print(result.all(), fp)
            return json.dumps({'result': False, 'msg': 'already exist'})
        else:
            return json.dumps({'result': True, 'msg': 'not exist'})
    # POST保存指纹
    if request.method == 'POST':
        if result:
            return json.dumps({'result': False, 'msg': 'already exist'})
        else:
            try:
                fingerprint = FingerPrint(fp=fp).save()
            except Exception as e:
                return json.dumps({'result': False, 'msg': 'MongoDB Error'})
            return json.dumps({'result': True, 'msg': fingerprint.fp})


if __name__ == '__main__':
    app.run()