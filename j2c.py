import csv, os, datetime, logging

def word_replace(line):
    if isinstance(line, str):
        line.replace("\"", "|")
    return str(line)

def json2csv(json_list, attribute, file_name, value_entry=["value"], attr_entry=None, clock_entry=None):
    if not value_entry:
        logging.error('Missing_value_entry')
        exit(1)
    if json_list:
        # if not empty
        try:
            logging.debug("writing_to_"+file_name)
            # open the given file in append+ mode
            
            with open(file_name, "a+") as fp:
                counter = 0
                writer = csv.writer(fp)
                for line in json_list:
                    csv_line = [word_replace(line[entry]) for entry in value_entry]    # recode the values
                    
                    # appended information, these attributes should be passed from the config file
                    if attr_entry:
                        csv_line.extend(list(attribute[line[attr_entry]].values()))
                        
                    # if needed, translate and record the timestamp
                    if clock_entry:
                        clock = datetime.datetime.fromtimestamp(int(float(line[clock_entry])))
                        csv_line.append(clock.strftime("%Y%m%d_%H:%M:%S"))
                    
                    # write to file in csv format
                    writer.writerows([csv_line])
                    
                    # to prevent page swap, flush the buffer every 20 row
                    counter += 1
                    if counter > 20:
                        fp.flush()
                        counter = 0
                        
        except:
            logging.exception("Fail_on_write")
