import json, os, requests, logging, sys

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

        ## if the Session has terminated, re-login
        #if(response['error']['data'] == 'Session terminated, re-login, please.'):
        #    logging.warning("Attempt_to_re-login...")
            # attempt to re-login
        #    if login(user="",password=""):
        #        return query(jsonrpc)
        #else:
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

def item_attr_get(item_name, host_name):
    attr_get_jsonrpc = {**prot, **{
        "method": "item.get",
        "params":{
            "filter": {"name":item_name},
            "host": host_name,
            "output":["itemids","name","value_type", "hostid"]
    }}}
    return query(attr_get_jsonrpc)

if __name__ == "__main__":
    print("usage : ")
    print("login(host:ip) -> query(jsonrpc, host)")


