from flask import Flask, request
import json
from zabbix_query import id_validate

app = Flask(__name__)
app._config=""

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
	pretty = request.args.get('pretty',"deFault")
	if (pretty == "deFault"):
		return json.dumps(app._config["probe"])
	else:
		return json.dumps(app._config["probe"],indent=4)

@app.route('/update', methods=['POST'])
def update():
	if request.method == 'POST':
		item = zq.id_validate(itemID)
	    if "error" not in item:
	        probe = app._config["probe"]["zabbix_probe"]
	        item = item["result"]
	        if item[0] in probe:
	            probe = probe[item[0]]
	            probe.update({item[1]:{"name":item[2],"probe_server":item[3]}})
	        else:
	            probe.update({item[0]:{item[1]:{"name":item[2],"probe_server":item[3]}}})
	        return True
	    else:
	        return item
    return False

