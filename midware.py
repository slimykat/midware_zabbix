import json
import os, sys, datetime, time
from zabbix_query import *

config = {}

def load_config(filename):
    with open(filename) as fd:
        if not fd:
            print("ERROR: config file DNE")
            print("cannot find " , filename)
            exit(0)
        try:
            config.update(json.load(fd))
        except:
            print(filename)
    # login zabbix server
    zabbix = config['zabbix'] 
    login(zabbix['host'], user = zabbix['user'], password = zabbix['password'])

def run(argd):
    # record the query time (AKA current time)
    now_timestamp = datetime.datetime.now()
    now = now_timestamp.strftime("%Y%m%d_%H_%M")

    # get latest data timestamp from argument or from file record
    old_time = argd['time_from']
    if(old_time == "daemon"):
        if os.path.isfile("./_service_last_update"):
            with open("_service_last_update","r") as f_time:
                time_from = f_time.readline()
        else:
            time_from = 0
        time_till = int(datetime.datetime.now().timestamp())
    elif(old_time == "one_minute"):
        t = datetime.datetime.now()
        time_till = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0)
        time_till = int(time_till.timestamp())
        time_from = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0) - datetime.timedelta(minutes=1)
        time_from = int(time_from.timestamp())-1
        #print(time_from, time_till)
    else:
        time_till = int(datetime.datetime.now().timestamp())

    histlist = [item_hist_get(item["id"], item["dtype"], config['zabbix']["host"], limit=argd["limit"], time_from=time_from, time_till=time_till) for item in config["item_list"]]
    
    if DEBUG:
        print(histlist)

    latest_min_time = "0"
    min_len = int(argd["limit"])
    update_stat = False
    for hist in histlist:

        if "error" in hist:
            print("ERROR: query error")
            print(histlist["error"])
            exit(0)

        if not hist["result"]:
            hist['result'] = [{"value":-1, "clock":"0"}for i in range(min_len)]
            continue
        else:
            update_stat = True
        current_len = len(hist['result'])
        current_latest_time = hist['result'][0]['clock']

        if(current_len < min_len):
            min_len = current_len
            latest_min_time = current_latest_time

        elif(current_len == min_len):
            if(current_latest_time > latest_min_time):
                latest_min_time = current_latest_time
    if not update_stat:
        return "zabbix no update"
    
    with open("probe/" + config['probe']['name'] + now +".csv", "a+", newline="") as f:

        for i in range(1,min_len+1):
            csv_line = [config['probe']['target_host'], ] # osprey protocal
            time = "0"
            for hist, setting in zip(histlist, config['item_list']):
                value = hist['result'][-i]['value']
                clock = hist['result'][-i]['clock']
                time = max(time, clock)
                cols = setting['col']

                #####################
                ## data process section
                #####################
                ## you can add any cutom processes in this section
                #####################
                if DEBUG:
                    print(value)
                if cols:
                    if (type(value) == str):
                        value = json.loads(value)
                    csv_line.extend([value[column] for column in cols])
                else:
                    csv_line.append(value)

            time_date = datetime.datetime.fromtimestamp(int(time))
            csv_line.extend([time_date.strftime("%Y%m%d_%H:%M:%S"),time])

            if DEBUG:
                print(csv_line,"\n")
            csv_line = [str(line) for line in csv_line]
            f.write(", ".join(csv_line))
            f.write("\n")

    if(argd['time_from'] == "daemon"):
        with open("_"+config['probe']['name']+"_last_update","w") as f_time:
            f_time.write(latest_min_time)

    return int(now_timestamp.timestamp())

def print_usage():
    print("usage:")
    print(
    "python3 midware.middle.py\n\
    time_from=<timestamp>|daemon|one_minute The latest timestamp for zabbix query,\n\
                                            Set to \"daemon.\" to automatically record query time\n\
                                            Set to \"one_minture\" to query datas in the 1 minute recently\
    limit=<query_max_num>                   How many queries for each probe\n\
    config=<path of dir>                    Config Directory Path\n\
    #don't put space(\s) in any of the arguments"
    )
    exit(0)

if __name__ == "__main__":
    # uncomment this line to get debug message
    #setDEBUG()

    ## read from argument
    if (len(sys.argv) == 0):
        print_usage()

    li1 = ([string.split("=")[0] for string in sys.argv[1:]])
    li2 = ([string.split("=")[1] for string in sys.argv[1:]])
    argd = dict(zip(li1,li2))
    if DEBUG :
        print(argd)
    
    if not "config" in argd:
        print("ERROR: missing \"config\" argument")
        print_usage()
    if not "time_from" in argd:
        print("ERROR: missing \"time_from\" argument")
        print_usage()
    if not "limit" in argd:
        print("WARNING: missing \"limit\" argument")
        print("set to default, limit = 10")
        argd['limit'] = 10
        
    config_dir = argd['config']
    config_dir = config_dir if config_dir.endswith("/") else config_dir+"/"
    while(True):
        for file in os.listdir(config_dir):
            if file.endswith(".json"):
                print(file, ":\n\t",end="")
                load_config(config_dir+file)
                print(run(argd))
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=1) - datetime.timedelta(seconds=now.second, microseconds=now.microsecond)
        time.sleep(delta.total_seconds())
