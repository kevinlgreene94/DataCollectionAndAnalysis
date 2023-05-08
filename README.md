# Data Collect
SWDV data collection effort

# Install & Run

1. source bin/activate
2. pip3 install -r requirements.txt
3. python3 dbconnection.py

# Optional

To run the file navigate to the directory of the dbconnection.py file in your terminal. Type the command 'export FLASK_APP=dbconnection.py'.
After running the command, enter 'flask run'. You will be able to navigate to http://localhost:5000/ and view the running application.

## Todo

- [ ] Put on class server
- [ ] Add delete company route, corresponding button is on modify modal
- [ ] Add a city option in company info
- [ ] Periodically auto-save notes as they are entered in textbox
- [ ] Can we contact in future should be 'yes', 'no', 'unknown' instead of 0, 1
- [ ] Update tech modal


## Done

- [x] Link the sidebar modify company to open the modify company dialog
- [x] Create a modal like create company but with the modify company page
- [x] Add an api route for techs and add to sidebar display
- [x] Add table like structure to show techs
- [x] Edit/Delete icon next to each tech
- [x] Consolate company card info so it is more readable
- [x] Delete contact (maybe on same modal)
- [x] Add new contact form and js
- [x] Create new tech modal
- [x] Button to add new tech at bottom of tech list
- [x] Modify contact in sidebar brings up form
- [x] Modify contact modal needs to get the right id
