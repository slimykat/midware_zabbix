import os, datetime, logging

def json2csv(json_list, attribute, file_name, value_entry=["value"], attr_entry=None, clock_entry=None):
    if not value_entry:
        logging.error('Missing_value_entry')
        exit(1)
    if json_list:
        # if not empty
        try:
            fp = os.open(file_name, os.O_RDWR|os.O_APPEND|os.O_CREAT)
            # open the given file in append+ mode
            
            counter = 0
            for line in json_list:
                csv_line = [line[entry] for entry in value_entry]    # recode the values
                
                # appended information, these attributes should be passed from the config file
                if attr_entry:
                    csv_line.extend(list(attribute[line[attr_entry]].values()))
                    
                # if needed, translate and record the timestamp
                if clock_entry:
                    clock = datetime.datetime.fromtimestamp(int(float(line[clock_entry])))
                    csv_line.append(clock.strftime("%Y%m%d_%H:%M:%S"))
                
                # write to file in csv format
                out = str.encode(",".join(csv_line) + "\n")
                
                # to prevent page swap, flush the buffer every 10000 byte
                counter += os.write(fp,out)
                if counter > 10000:
                    os.fsync(fp)
                    counter = 0
                    
            os.fsync(fp)
            os.close(fp)
        except:
            logging.exception("Fail_on_write")
