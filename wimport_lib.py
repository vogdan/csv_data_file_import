from os import listdir
from csv import reader, writer
from os.path import join

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

    :input: a directory containing input files
            suffix of the input files (by default set to ".csv")
    :return: list containing the csv files in input_dir (full path) 
    """
    
    filenames = listdir(input_dir)
    return [join(input_dir, filename) for filename in filenames 
                                        if filename.endswith(suffix)]


def write_sql_table(cursor, db_name, table_name, headers_list, values_list):
    """
    Write info to an SQL table.

    :input: cursor - MySQLdb cursor object as obtained prior to connecting to the
                     database
            db_name - name of the database to create the table in
            table_name - name of table to be created
            headers_list - table headers
            values_list - list of lists each containing a table row
    :return: Nothing
    :notes: Table will be dropped and recreated if already exists
            Headers (columns) names will have all spaces and round brackets removed
            If values list is longer than headers list, it will be trimmed to 
            headers list length
    """

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
