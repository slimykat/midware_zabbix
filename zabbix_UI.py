from flask import Flask, request, json
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
def show(pretty="_deFault"):
	if (pretty=="_deFault"):
		return json.dumps(app._config["probe"])
	else:
		return json.dumps(app._config["probe"],indent=4)

#@app.route('/update', methods=['POST'])