from MySQLdb import connect
from time import gmtime, strftime
from argparse import ArgumentParser
import os
import wimport_lib 
from config import logger
from config import OUTPUT_PARTICIPANTS, OUTPUT_WEBINARS, DETAILS_MARK
from config import DB_NAME, SERVER_NAME, USER, PASS, W_TABLE, P_TABLE 
from config import LOG_FILE, LOG_FILE_PATH



def parse_cli_opts():
    """
    Creates the cli interface and provids an argument parse handler (args)
    """
    global args

    parser = ArgumentParser(description='''Gather participants and webinars 
info from multiple files of attendees for GotoWebinar webinars and output
data in two output files or/and to a MySQL database.''')
    parser.add_argument('-i', '--input_dir', 
                        help='Directory containing input csv files', 
                        required=True)
    parser.add_argument('-d', '--write_to_db', 
                        help='Write info to database also', 
                        action="store_true")
    args = parser.parse_args()


def gather_csv_info():
    """
    Reads the input files one by one and stores the data in dictionaries
    containing lists of lists.
    """
    global args
    global w_dict, w_info
    global p_dict, p_headers_list, p_no_sum

    w_dict, p_dict = {}, {}
    p_headers_list = []
    p_no_sum = 0

    for input_file in wimport_lib.find_csv_filenames(args.input_dir):
        # get webinar and participants info
        w_info = wimport_lib.get_webinar_info(input_file, DETAILS_MARK)
        if w_info:
            w_id = wimport_lib.get_parameter('Webinar ID', w_info[0], w_info[1])
            p_info = wimport_lib.get_participants_info(input_file, w_id, DETAILS_MARK)
            p_len = len(p_info[1])
            p_no_sum += p_len
            logger.info("Reading {} \n\t --> {} participants.".format(input_file, p_len))
            # store info for later writing to files and database
            if w_id not in w_dict:
                w_dict[w_id] = [w_info[1]]
            else:
                w_dict[w_id] += [w_info[1]]
            if w_id not in p_dict:
                p_dict[w_id] = p_info[1]
            else:
                p_dict[w_id] += p_info[1]
            p_headers_list += [p_info[0]]


def process_csv_info():
    """
    Processes the read information:
        Separate headers form webinars and participants details.
        Detect differences in participants headers and cope with them 
            ( keep the longes header and add empty fields in the right 
              positionfor participants info rows that are shorter than 
              the longest header )        
        Basic error checking and debug messahe logging.
    
    :return: 1 on error and 0 on success
    """
    global w_dict, w_header, w_values, w_info
    global p_header, p_values, p_headers_list

    # get headers and values for webinars
    w_header = w_info[0]
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
        diffs_pos = [p_header.index(x) for x in diffs]
    for key in p_dict:
        for row in p_dict[key]: 
            if len(row) < len(p_header):
                # handle differences in input files headers
                if not diffs:
                    logger.error("Header longer than row but no diffs detected.")
                    return 1
                for pos in diffs_pos:
                    insert_pos = int(pos)
                    row.insert(insert_pos, "")
            elif len(row) > len(p_header):
                logger.error("Participants row longer than header.Exiting...")
                logger.debug('''
webinar id:{}
final_participants_header:{}
row:{}
'''.format(key, p_header, row))
                return 1
            else:
                break
        p_values += p_dict[key]

    return 0


def main():
    global args 
    global w_dict, w_info, w_header, w_values
    global p_dict, p_headers_list, p_no_sum, p_header, p_values

    parse_cli_opts()
    gather_csv_info()

    try:
        logger.info("Processing gathered information...")
        result = process_csv_info()
        if result: 
            return result
    
        # check for data consistency
        p_final_no = len(p_values)
        w_final_no = len(w_values)
        logger.info("Total: {} participants, {} webinars.".format(p_final_no, w_final_no))
        if p_no_sum != p_final_no:
            logger.error('''Total participants number after processing ({}) differs from initial value ({}).
Some lines might have been lost in processing. Exiting...'''.format(p_final_no, p_no_sum))
            return 1

        # write output files
        logger.info("Writing output files:")
        wimport_lib.write_to_csv(OUTPUT_WEBINARS, w_header, w_values)
        wimport_lib.write_to_csv(OUTPUT_PARTICIPANTS, p_header, p_values)

        # write to database
        if args.write_to_db:
            logger.info("Writing do database:")
            conn = connect(SERVER_NAME, USER, PASS, DB_NAME)
            with conn:
                cur = conn.cursor()
                wimport_lib.write_sql_table(cur, DB_NAME, W_TABLE, w_header, w_values)
                wimport_lib.write_sql_table(cur, DB_NAME, P_TABLE, p_header, p_values)

        return 0

    except Exception as e:
        print "\n\tSomething went wrong. Check log for details."
        logger.debug("Exception:\n{}".format(e))
        return 1


if __name__ == "__main__":
    
    # add log run delimiter (only visible in log file)
    log_delimiter = "#"*20 + strftime("%a, %d %b %Y %X +0000", gmtime()) + "#"*10 
    logger.debug("\n"*2 + log_delimiter + "\n")    

    print ""
    main()
    print "\nDebug log: '{}'\n".format(os.path.join(LOG_FILE_PATH, LOG_FILE))
