CSV Data File Import
================

Python program to import multiple files of attendees for GotoWebinar webinars and create 2 output files: 
one with a one row per attendee and one with one row per webinar. 
If so specified, the program can also write the information gathered into a database containing two tables 
(the tables are overwritten each timethe program is called)


###Usage
    
      
    python dbogdan-webinarImport.py [-h] -i INPUT_DIR [-d]

    Arguments:
          -h, --help            Show help message and exit
          -i, --input_dir       Directory containing input csv files
          -d, --write_to_db     Write info to database also
          
    Packages needed: MySQLdb, logging.      

###How To

#####Database setup

   For the database writing to work, we need to create a user and a database and grant all privileges to this user 
   for all tables of the database. 

    $ mysql -u root -p
    Enter password: *****
    Welcome to the MySQL monitor.  Commands end with ; or \g.
    Your MySQL connection id is 7
    Server version: 5.6.14 MySQL Community Server (GPL)

    Copyright (c) 2000, 2013, Oracle and/or its affiliates. All rights reserved.

    Oracle is a registered trademark of Oracle Corporation and/or its
    affiliates. Other names may be trademarks of their respective
    owners.

    Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

    mysql> CREATE DATABASE testdb;
    Query OK, 1 row affected (0.02 sec)

    mysql> CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'test623';
    Query OK, 0 rows affected (0.00 sec)

    mysql> USE testdb;
    Database changed

    mysql> GRANT ALL ON testdb.* TO 'testuser'@'localhost';
    Query OK, 0 rows affected (0.00 sec)

    mysql> quit;
    Bye

#####Logging Guidelines

1. Do not use print. Use the logger object instead by 
    importing it in your .py file:

        from config import logger
    
  Only use print if you want messages to be displayed
     at the console but not in the log file
 
2. To log message to console and log file use

        log.info(message)

3. To log message only to log file (debug messages) use     

        log.debug(message)

4. Warning (log.warning )and error (log.error) messages 
    will be automatically logged to both console and log file.


### Program Requirements
  
- program should read from multiple input files (see attachments) and create just the 2 output files.  
Note that some of the input files are slightly different
 
- program should have a command line option "-i <directory>"  where <directory> specifies where the input files 
can be found

- the output file should be written to the current durectory (where the py file is invoked)
 
- if the program is run with a command line option "-d" it should load the output to a database 
(in addition to creating the output file)
The program should create the tables if they don't exist or overwrite everything if they do exist.  
Table and Server names can be specified in variables at inside the python file as DB_NAME and SERVER_NAME

https://www.elance.com/j/data-file-import/48843674/?bidid=48910074


###Others

- The program has been written in Python 2.7.3 and tested on Ubuntu 12.04 and Windows XP
