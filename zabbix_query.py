import json, os, requests, logging, sys, datetime, threading
from c2v import json2csv

prot = {"jsonrpc":"2.0","auth":None,"id":0}
zabbix_host = ""
User = "Admin"
Password = "zabbix"

def query(jsonrpc):
    #test start
    url = "http://"+zabbix_host+"/zabbix/api_jsonrpc.php"
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, data=json.dumps(jsonrpc), headers=headers).json()
    if("error" in response):
        logging.error(str(response['error']))

        sys.exit(1)
    return response

def login(host="", user = "", password=""):
    # write to global variable if given any
    global zabbix_host, User, Password
    if host :
        zabbix_host = host
    if user:
        User = user
    if password:
        Password = password

    # reset auth key, empty auth key is required for zabbix login
    prot.update({"auth":None})

    jsonrpc = {**prot,**{
        "method":"user.login",
        "params":{
            "user": User,
            "password": Password
    }}}
    result = query(jsonrpc)

    if 'result' in result:
        key = result['result']
        logging.debug("keytoken=" + key)
        prot.update({"auth":key})
    else:
        logging.error("Loging_failed")
        return False
    return True

def extend_lifetime():
    life_rpc = {
        "jsonrpc": "2.0",
        "method": "user.checkAuthentication",
        "params": {
            "sessionid": prot["auth"]
        },
        "id": 1
    }
    if life_rpc["params"]["sessionid"]:
        query(life_rpc)
    else:
        logging.warning("Run_Without_Login")

def item_hist_get(itemid, dtype, limit=None, time_from=0, time_till = None):
    history_jsonrpc = {**prot, **{
        "method": "history.get",
        "params":{
            "itemids":itemid,
            "output":["itemid","clock","value"],
            "history":dtype,
            "limit":limit,
            "time_from": time_from,
            "time_till" : time_till,
            "sortfield": ["itemid","clock"],
            "sortorder": "DESC"
    }}}
    result = query(history_jsonrpc)
    if not result['result']:
        logging.info("Empty_result")
    return result['result']
"""
History object types to return. (dtype)

Possible values:
0 - numeric float;
1 - character;
2 - log;
3 - numeric unsigned;
4 - text. 
"""
def bulk_query(c):
    # extract from config
    config = c.copy()
    probe = config["probe"]
    zabbix = config["zabbix"]
    outpath = zabbix["out_Dir"]
    if not outpath.endswith("/"):
        outpath += "/"

    # record the query time (AKA current time)
    t = datetime.datetime.now()
    now = t.strftime("%Y%m%d_%H_%M")

    # request for all the data within the one minute
    time_till = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0)
    time_till = int(time_till.timestamp())
    time_from = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0) - datetime.timedelta(minutes=1)
    time_from = int(time_from.timestamp())

    logging.info("Start_query")
    # bulk query for each group
    for probe_type, groups in probe.items():        # for the definition of the layout
        # set up for file IO
        file_name = outpath+str(probe_type)+"@"+now+".csv"
        
        for dtype, itemlist in groups.items():  # plz check the document

            # send query message, arguments contains these information:
            # def history_get(target(s), group, start_time, end_time)
            itemids = list(itemlist.keys())
            payload = item_hist_get(itemids, dtype, time_from=time_from, time_till=time_till)            

            # assign the task to another thread
            t = threading.Thread(
                target=json2csv, 
                args=(payload, itemlist, file_name),
                kwargs=zabbix["csv_entry"]
            )
            t.start() # no need to join
    logging.debug("Query_complete")

def id_validate(itemid):
    if type(itemid) != int:
        return {"error":{"code":-1,"message":"INPUT_ERROR:only_accept_int"}}
    result = item_attr_get(itemid)["result"]
    if result:
        dtype = result[0]['value_type']
        name = result[0]['name']
        itemid = result[0]['itemid']
        probe_server = result[0]["applications"][0]["name"]
        return {dtype:{itemid:{"name":name,"probe_server":probe_server}}}
    else:
        return {"error":{"code":0,"message":"EMPTY_RESULT:item_DNE"}}

##################################################
# the following functions are used for dev ->
##################################################
def hostid_get(host_name_list):
    id_jsonrpc = {**prot, **{
        "method":"host.get", 
        "params":{
            "output":["hostid","name"],
            "filter":{ "host": host_name_list }
    }}}
    return query(id_jsonrpc)

def itemlist_get(host_name=None, host_id=None, filter_dict={}):
    itemlist_jsonrpc = {**prot, **{
        "method": "item.get",
        "params":{
            "hostids": host_id,
            "host":host_name,
            "filter": filter_dict,
            "output":["itemids","name","value_type","host","host_id"]
    }}}
    return query(itemlist_jsonrpc)

def item_get(item_id):
    item_jsonrpc = {**prot, **{
        "method": "item.get",
        "params":{
            "itemids": item_id,
            "output":"extend"
    }}}
    return query(item_jsonrpc)

def itemid_get(item_name, host_name):
    attr_get_jsonrpc = {**prot, **{
        "method": "item.get",
        "params":{
            "filter": {"name":item_name},
            "host": host_name,
            "output":["itemids","name","value_type", "hostid"]
    }}}
    return query(attr_get_jsonrpc)

def item_attr_get(itemid):
    attr_get_jsonrpc = {**prot, **{
        "method": "item.get",
        "params":{
            "itemids":itemid,
            "selectApplications":["name"],
            "output":["itemids","name","value_type"]
    }}}
    return query(attr_get_jsonrpc)

if __name__ == "__main__":
    print("usage : ")
    print("login(host:ip) -> query(jsonrpc, host)")


