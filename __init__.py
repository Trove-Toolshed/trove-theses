from flask import Flask
from flask.ext.mongoengine import MongoEngine

from credentials import SECRET_KEY

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {'DB': 'trovetheses'}
app.config['SECRET_KEY'] = SECRET_KEY

db = MongoEngine(app)


if __name__ == '__main__':
    app.run()