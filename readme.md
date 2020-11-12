NAME : Sarvesh Bodakhe
MIS : 111803149
TY COMP DIV 2

HTTP WEB SERVER IN PYTHON

GET, POST, PUT, HEAD, DELETE, Cookies, Headers, non-persistent connections, Multiple clients at the same time (with a sepearate program to test this), logging with levels of logging, handling file permissions; Server configuration - config file with DocumentRoot, log file name, max simulateneous connections ;

==========================================================================================================================

- How to run the server ?
  \$ python3 server.py port_number
  Ex : python3 server.py 2000

===========================================================================================================================

This testing program is for testing multithreading

- How to run multiple client testing program ?
  \$ python3 testing.py port_number
  Ex : python3 requests_testing.py 2000 (same port number on which server has started)

==========================================================================================================================

RUN THE SERVER BEFORE AUTOMATED TESTING
This Automated testing tests differents requests made to the server

- How to run Automated testing program ?
  \$ python3 stress_testing.py port_number

===========================================================================================================================

CONFIGURE THE server_config.py FILE BEFORE RUNNING THE SERVER
MAKE CHANGES ACCORDINGLY

===========================================================================================================================

ALL FILE PERMISSIONS ARE HANDLED FOR EVERY METHOD IMPLEMENTED
MOST OF THE HEADERS ARE HANDLED

METHODS IMPLEMENTED :

1. GET
2. HEAD
3. POST
4. PUT
5. DELETE

- Multithreaded Web Server

- GET METHOD

1. All types of files can be requested from the server. Ex : text files, .png files, .jpeg files
2. Implemented Conditional Get
3. Queried GET request is also handle by the server for json files
4. Whenever a directory is requested all the files are listed
5. Try URLS:
   "http://localhost:2000/form.html"
   "http://localhost:2000/form2.html"
   "http://localhost:2000/"

- HEAD METHOD

1. All get methods implemented

- POST METHOD

1. Created a simple form at "http://localhost:2000/form.html"
2. Form data submitted is stored in the specified csv file
3. If file is not there then a new file is created
4. Accordinly status codes are handled
5. Form with files is handled at url : "http://localhost:2000/form2.html"

- PUT METHOD

1. Implemented for any type of file data of any length

- DELETE METHOD

1. Delete files which are requested(All file types have been handled)
2. Authorization is required
3. If file not found then give status codes accordingly

==================================================================================================================================
Log file locations in config file
There are two logs:

1. ACCESS LOG
2. ERROR LOG

===================================================================================================================================

- Cookies :
  Whenever a new page is requested a cookie is set if cookie is not present in request headers .
  Checks for a cookie header when client connects again
