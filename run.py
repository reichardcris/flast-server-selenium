from flask import Flask
from flask import request
from seleniumModule.SeleniumAutomate import SeleniumAutomate
import json

app = Flask(__name__)

@app.route('/automate',methods = ['POST', 'GET'])
def automate():
  if request.method == 'POST':
    pages = json.loads(request.form['page_location'])
    docs = json.loads(request.form['docs_info'])
    SeleniumAutomate(request.form['path'], pages, docs)
    return request.form
  return request.form

