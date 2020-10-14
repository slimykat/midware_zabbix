# midware_zabbix



def query(jsonrpc):
# the core function, would be used in other functions

#########################################################
### functions that were designed for automated queries

def login(zabbix_ip_port, user = "Admin", password="zabbix"):
# log in the given zabbix host, the query would return the token for Authentication

def item_hist_get(itemid, dtype, zabbix_ip_port,\
    limit=1, time_from=-1, time_till = None):
# the function would query the newest ${limit} message(s) in the time segment defined by the two time argument (from ${time_from} to ${time_till})

""" History object types to return. (dtype)

Possible values:
0 - numeric float;
1 - character;
2 - log;
3 - numeric unsigned;
4 - text. 
"""
#########################################################
### functions for inspecting data

def hostid_get(host_name_list, zabbix_ip_port):
# given list of host name, return their ids

def itemlist_get(host_id, zabbix_ip_port):
# given host's id, return the host's every itemid, item name, and thier dtype

def item_get(item_id, zabbix_ip_port):
# given item id, return its every attribute

#########################################################