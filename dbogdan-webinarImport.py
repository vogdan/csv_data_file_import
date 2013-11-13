
from MySQLdb import connect
from wimport_lib import *


INPUT_DIR = "/mnt/mare/CodingWork/eLance/Data file import/input"
OUTPUT_PARTICIPANTS = 'oput-Participants.csv'
OUTPUT_WEBINARS = 'oput-Webinars.csv'

DB_NAME = "testdb"
SERVER_NAME = "localhost"
USER = "testuser" 
PASS = "testx"
W_TABLE = "Webinars"
P_TABLE = "Participants"


w_dict, p_dict = {}, {}
# cycle through files in input dir and gather info
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
conn = connect(SERVER_NAME, USER, PASS, DB_NAME)
with conn:
    cur = conn.cursor()
    write_sql_table(cur, DB_NAME, W_TABLE, w_header, w_values)
    write_sql_table(cur, DB_NAME, P_TABLE, p_header, p_values)
    
        
