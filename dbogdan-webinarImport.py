
from MySQLdb import connect
from argparse import ArgumentParser
from wimport_lib import *

OUTPUT_PARTICIPANTS = 'oput-Participants.csv'
OUTPUT_WEBINARS = 'oput-Webinars.csv'
DETAILS_MARK = "Session Details"
DB_NAME = "testdb"
SERVER_NAME = "localhost"
USER = "testuser" 
PASS = "testx"
W_TABLE = "Webinars"
P_TABLE = "Participants"

# parse CLI options 
parser = ArgumentParser(description='''Gather participants and webinars info from 
multiple files of attendees for GotoWebinar webinars''')
parser.add_argument('-i', '--indir', help='Directory containing input csv files', required=True)
parser.add_argument('-d', '--dbout', help='Write info to database also', action="store_true")
args = parser.parse_args()

# cycle through files in input dir and gather info in dictionaries
#    containing lists of lists
w_dict, p_dict = {}, {}
p_headers_list = []
for input_file in find_csv_filenames(args.indir):
    # get webinar and participants info
    webinar_info = get_webinar_info(input_file, DETAILS_MARK)
    webinar_id = get_parameter('Webinar ID', webinar_info[0], webinar_info[1])
    p_info = get_participants_info(input_file, webinar_id, DETAILS_MARK)

    # store info for later writing to files and database
    if webinar_id not in w_dict:
        w_dict[webinar_id] = [webinar_info[1]]
    else:
        w_dict[webinar_id] += [webinar_info[1]]
    if webinar_id not in p_dict:
        p_dict[webinar_id] = p_info[1]
    else:
        p_dict[webinar_id] += p_info[1]
    p_headers_list += [p_info[0]]	

# get headers and values for webinars
w_header = webinar_info[0]
w_values = []
for key in w_dict:
    w_values += w_dict[key]

# get headers and values for participants
p_header, p_values, diffs = p_headers_list[0], [], []
for h in p_headers_list[1:]:
    # try to find differences in participants headers 
    if len(p_header) < len(h):
        diffs = [x for x in h if x not in p_header]
        p_header = h
        break
    elif len(h) < len(p_header):
        diffs = [x for x in p_header if x not in h]
        break
if diffs:
    # handle differences in input files headers
    diffs_pos = [p_header.index(x) for x in diffs]
    for key in p_dict:
        for row in p_dict[key]: 
            if len(row) != len(p_header):
                for pos in diffs_pos:
                    insert_pos = int(pos) + int(diffs_pos.index(pos))
                    row.insert(insert_pos, "")
            else:
                break
p_values += p_dict[key]

# write output files
print "\nWriting output files:"                
write_to_csv(OUTPUT_WEBINARS, w_header, w_values)
write_to_csv(OUTPUT_PARTICIPANTS, p_header, p_values)

# write to database
if args.dbout:
    print "\nWriting do database:"
    conn = connect(SERVER_NAME, USER, PASS, DB_NAME)
    with conn:
        cur = conn.cursor()
        write_sql_table(cur, DB_NAME, W_TABLE, w_header, w_values)
        write_sql_table(cur, DB_NAME, P_TABLE, p_header, p_values)
