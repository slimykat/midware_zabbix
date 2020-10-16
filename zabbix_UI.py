from flask import Flask, request
import zabbix_query as zq

app = Flask(__name__)
app._config=""

def show_host():
	return request.host

@app.route('/', methods=['GET'])
def index():
	return(
			"zabbix midware UI:\n"+
			"	index:\n"+
			"		1. ip:port/zabbix/show\n"+
			"		2. ip:port/zabbix/update\n"
		)

@app.route('/show', methods=['GET'])
def show():
	return app._config

#@app.route('/update', methods=['POST'])