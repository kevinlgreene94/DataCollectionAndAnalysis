# Before Run
1. Connect and run CREATE_DATABASE.sql within a MariaDB server.
2. Change connection settings in dbconnection.py dbConnect().

# Install & Run

1. source bin/activate
2. pip3 install -r requirements.txt
3. python3 dbconnection.py

# Optional

To run the file navigate to the directory of the dbconnection.py file in your terminal. Type the command 'export FLASK_APP=dbconnection.py'.
After running the command, enter 'flask run'. You will be able to navigate to http://localhost:5000/ and view the running application.

# Packages

1. Flask
2. MariaDB Connector/Python
