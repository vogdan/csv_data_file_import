
from csv import reader, writer
from os import listdir
from os.path import join

INPUT_DIR = join("C:\\", "Elance", "CSV Data File Import", "input")
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

webinars_dict = {}
participants_dict = {}
for f in listdir(INPUT_DIR):
	input_file = join(INPUT_DIR, f)
	# get webinar and participants info
	webinar_info = get_webinar_info(input_file)
	webinar_id = get_parameter('Webinar ID', webinar_info[0], webinar_info[1])
	participants_info = get_participants_info(input_file, webinar_id)
	if webinar_id not in webinars_dict:
		webinars_dict[webinar_id] = [webinar_info[1]]
	else:
		webinars_dict[webinar_id] += [webinar_info[1]]
	if webinar_id not in participants_dict:
		participants_dict[webinar_id] = participants_info[1]
	else:
		participants_dict[webinar_id] += participants_info[1]
	
# create output files
webinars_header = webinar_info[0]
webinars_values = []
participants_header = participants_info[0]
participants_values = []
for key in webinars_dict:
	webinars_values += webinars_dict[key]
for key in participants_dict:
	participants_values += participants_dict[key]
		
write_to_csv(OUTPUT_WEBINARS, webinars_header, webinars_values)
write_to_csv(OUTPUT_PARTICIPANTS, participants_header, participants_values)


