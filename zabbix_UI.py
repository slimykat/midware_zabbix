from flask import Flask, request
import json, logging
from zabbix_query import id_validate
from zabbix_query import itemlist_get
app = Flask(__name__)
app._config=""

@app.route('/', methods=['GET'])
def index():
    return(
            "zabbix midware UI:\n"+
            "   index:\n"+
            "[GET]      1. ip:port/zabbix/show\n"+
            "[GET]      2. ip:port/zabbix/init\n"+
            "[POST]     3. ip:port/zabbix/update\n"+
            "[POST]     4. ip:port/zabbix/delete\n"
        )

@app.route('/show', methods=['GET'])
def show():
    pretty = request.args.get('pretty',"deFault")
    if (pretty == "deFault"):
        return json.dumps(app._config)
    else:
        return json.dumps(app._config,indent=4)

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                a[key] = b[key]
                #raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

@app.route("/init", methods=['GET'])
def init():
    probe = app._config["zabbix_probe"]
    for item in itemlist_get()['result']:
        Item = {
            item['value_type']:{
                item['itemid']:{
                    "name":item['name'],
                    "probe_server":"-"
                    }
                }
            }
        merge(probe, Item)    
    return {"message":"init complete"}

@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        itemID = request.form.get("itemID", default=None)
        probe_server = request.form.get("probe_server", default="-")
        item = id_validate(itemID, server=probe_server)
        if "error" not in item:
            probe = app._config["zabbix_probe"]
            merge(probe, item)
            return {"message":"update complete"}
        else:
            return item
    return {"error":{"code":-1,"message":"METHOD:only accepts POST"}}

@app.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        itemID = request.form.get("itemID")
        for group in list(app._config["probe"]["zabbix_probe"].values()):
            #logging.debug("group:"+str(list(group)))
            if itemID in group:
                group.pop(itemID)
                return {"message":"delete complete"}
        return {"error":{"code":0,"message":"EMPTY_RESULT:item_DNE"}}
    return {"error":{"code":-1,"message":"METHOD:only accepts POST"}}
