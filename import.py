#!/usr/bin/env python

import csv

INPUT_FILE = 'input-FromGotoWebinar.csv'
OUTPUT_PARTICIPANTS = 'oput-Participants.csv'
OUTPUT_WEBINARS = 'oput-Webinars.csv'
GENERAL_MARK = "General Information"
DETAILS_MARK = "Session Details"


def clear_empty_from_list(my_list):
    '''
    Remove empty string entries from my_list
    '''
    return [x for x in my_list if x]


def get_webinar_info(input_file):
    """
    Gather information about the webinar
    
    :input: a csv file of attendees for a GotoWebinar to read from
    :return: a list of two lists containing the webinar details 
             headers and corresponding header values
    """
    with open(input_file, 'rb') as csv_file:
        reader = csv.reader(csv_file)
        # read Generated info and advance to next useful headers
        reader.next()
        keys = reader.next()
        vals = reader.next()
        reader.next()
        # read the rest of webinar info
        while DETAILS_MARK not in keys:
            try:
                headers += clear_empty_from_list(keys)
                values += clear_empty_from_list(vals)
            except NameError:
                headers = clear_empty_from_list(keys)
                values = clear_empty_from_list(vals)
            keys = reader.next()
            vals = reader.next()
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
        reader = csv.reader(csv_file)
        for row in reader:
            if not reading_details:
                if DETAILS_MARK in row:
                    headers = ['Webinar ID'] + reader.next()
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
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for values in values_list:
            writer.writerow(values)


w_info = get_webinar_info(INPUT_FILE)
write_to_csv(OUTPUT_WEBINARS, w_info[0], [w_info[1]])
webinar_id = get_parameter('Webinar ID', w_info[0], w_info[1])
p_info = get_participants_info(INPUT_FILE, webinar_id)
write_to_csv(OUTPUT_PARTICIPANTS, p_info[0], p_info[1])
