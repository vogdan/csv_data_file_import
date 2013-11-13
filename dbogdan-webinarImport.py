
from csv import reader, writer
from os import listdir
from os.path import join

INPUT_DIR = "/mnt/mare/CodingWork/eLance/Data file import/input"
OUTPUT_PARTICIPANTS = 'oput-Participants.csv'
OUTPUT_WEBINARS = 'oput-Webinars.csv'
DETAILS_MARK = "Session Details"


def clear_empty_from_list(my_list):
    """
    Remove empty string entries from my_list
    
    :input: a list
    :output: a new list with empty string entries removed
    """
    
    return [x for x in my_list if x]


def get_webinar_info(input_file):
    """
    Gather information about the webinar
    
    :input: a csv file of attendees for a GotoWebinar to read from
    :return: a list of two lists containing the webinar details 
             headers and corresponding header values
    """
    
    with open(input_file, 'rb') as csv_file:
        rdr = reader(csv_file)
        # read Generated info and advance to next useful headers
        rdr.next()
        keys = rdr.next()
        vals = rdr.next()
        rdr.next()
        # read the rest of webinar info
        while DETAILS_MARK not in keys:
            try:
                headers += clear_empty_from_list(keys)
                values += clear_empty_from_list(vals)
            except NameError:
                headers = clear_empty_from_list(keys)
                values = clear_empty_from_list(vals)
            keys = rdr.next()
            vals = rdr.next()
    return [headers, values]


def get_participants_info(input_file, webinar_id):
    """
    Gather information about the webinar participants
    
    :input: a csv file of attendees for a GotoWebinar to read from
            the webinar id number
    :return: a list of two lists containing the webinar participants details 
             headers and a list of items representing corresponding header values
    """
    
    reading_details = 0
    values_list = []
    with open(input_file, 'rb') as csv_file:
        rdr = reader(csv_file)
        for row in rdr:
            if not reading_details:
                if DETAILS_MARK in row:
                    headers = ['Webinar ID'] + rdr.next()
                    reading_details = 1
                    continue
            else:
                values_list.append([webinar_id] + row)
    return [headers, values_list]


def get_parameter(param_str, headers, values):
    """
    Get the value of a specific parameter (header entry)
    
    :input: desired header parameter (header entry)
            list representing the full header
            list representing the corresponding header values
    :return: the value of the specified parameter
    :calling example:
              # get webinar id
              w_info = get_webinar_info(INPUT_FILE)
              webinar_id = get_parameter('Webinar ID', w_info[0], w_info[1])
    """
    
    return values[headers.index(param_str)]


def write_to_csv(output_file, headers, values_list):
    """
    Write header and corresponding values to a csv file

   :input: desired output file name
           a list representing the csv file header
           a list of lists, each representing the corresponding values
    :return: nothing
    :calling example:
              # write webinar details to csv
              w_info = get_webinar_info(INPUT_FILE)
              write_to_csv(OUTPUT_WEBINARS, w_info[0], [w_info[1]])
    """
    
    with open(output_file, 'wb') as csv_file:
        wrtr = writer(csv_file)
        wrtr.writerow(headers)
        for values in values_list:
            wrtr.writerow(values)


def find_csv_filenames(input_dir, suffix=".csv"):
    """
    Scan the input directory and return a list containing all the .csv files
    found there.
    """
    
    filenames = listdir(input_dir)
    return [join(input_dir, filename) for filename in filenames 
                                        if filename.endswith(suffix)]


# cycle through files in input dir and gather info
w_dict, p_dict = {}, {}
for input_file in find_csv_filenames(INPUT_DIR):
	# get webinar and participants info
	webinar_info = get_webinar_info(input_file)
	webinar_id = get_parameter('Webinar ID', webinar_info[0], webinar_info[1])
	p_info = get_participants_info(input_file, webinar_id)
	# store info for later writing to files and database
	if webinar_id not in w_dict:
		w_dict[webinar_id] = [webinar_info[1]]
	else:
		w_dict[webinar_id] += [webinar_info[1]]
	if webinar_id not in p_dict:
		p_dict[webinar_id] = p_info[1]
	else:
		p_dict[webinar_id] += p_info[1]
	
# get headers and values for webinars and participants
w_header = webinar_info[0]
w_values = []
p_header = p_info[0]
p_values = []
for key in w_dict:
	w_values += w_dict[key]
for key in p_dict:
	p_values += p_dict[key]

# write output files		
write_to_csv(OUTPUT_WEBINARS, w_header, w_values)
write_to_csv(OUTPUT_PARTICIPANTS, p_header, p_values)

# write to database
import MySQLdb as mdb

DB_NAME = "testdb"
SERVER_NAME = "localhost"
USER = "testuser" 
PASS = "testx"
W_TABLE = "Webinars"
P_TABLE = "Participants"

def write_sql_table(cursor, db_name, table_name, headers_list, values_list):

    print "Dropping table {}.{}...".format(db_name, table_name)
    cursor.execute("DROP TABLE IF EXISTS {}.{}".format(db_name, table_name))

    print "Creating table {}.{}...".format(db_name, table_name)
    db_headers = [x.translate(None, '() ') for x in headers_list]
    create_cmd = "CREATE TABLE {}({})".format(
        table_name,
        ", ".join(["`"+x+"`" + " VARCHAR(500)" for x in db_headers]))
    cursor.execute(create_cmd)

    print "Populating table {}.{}...".format(db_name, table_name)
    header_len = len(headers_list)
    for row in values_list:
        if len(row) > header_len:
            row = row[:header_len]
        insert_cmd = "INSERT INTO {0}({1}) VALUES({2})".format(  
            db_name + "." + table_name,
            ", ".join(["`"+x+"`" for x in db_headers]),
            ", ".join(["'"+x+"'" for x in row]))
        cursor.execute(insert_cmd)

    
conn = mdb.connect(SERVER_NAME, USER, PASS, DB_NAME)
with conn:
    cur = conn.cursor()
    write_sql_table(cur, DB_NAME, W_TABLE, w_header, w_values)
    write_sql_table(cur, DB_NAME, P_TABLE, p_header, p_values)
    
        
