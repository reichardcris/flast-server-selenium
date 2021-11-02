from flask import Flask
from flask import request
from seleniumModule.SeleniumAutomate import SeleniumAutomate
import json

app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def root():
  return 'Welcome to python selenium!', 200

@app.route('/test',methods = ['POST', 'GET'])
def test():
  return 'All goood to python selenium!', 200

@app.route('/automate',methods = ['POST', 'GET'])
def automate():
  if request.method == 'POST':
    pages = json.loads(request.form['page_location'])
    docs = json.loads(request.form['docs_info'])
    status = SeleniumAutomate(request.form['path'], pages, docs).getStatus()
    return status

  return 'Something went wrong! please try again...', 500

