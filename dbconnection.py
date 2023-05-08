from flask import Flask, render_template, request, jsonify
import mariadb
import sys
import datetime
import json
from collections import Counter

app = Flask(__name__, template_folder='templates', static_folder='assets')
app.config["DEBUG"] = True
app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True,
)


def dbConnect():
    try:
        conn = mariadb.connect(
            user="USERNAME",
            password="PASSWORD",
            host="SERVER_IP",
            port=3306,
            database="DATABASE_NAME"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    return conn


# --------------------------API FUNCTIONS--------------------------------------
@app.route('/api/')
def api_get_companies_byID():
    conn = dbConnect()
    cursor = conn.cursor()
    id = request.args.get('id')
    if (id == None):
        cursor.execute(f'SELECT * FROM company')
    else:
        cursor.execute(f'SELECT * FROM company WHERE company_id = {id}')
    data = []
    for id, name, street, state, zip, size, area, hire2year, intern in cursor:
        data.append({
            "id": id,
            "name": name,
            "street": street,
            "state": state,
            "zip": zip,
            "size": size,
            "area": area,
            "hire2year": hire2year,
            "intern": intern
        })
    conn.close()
    return data


@app.route('/api/contacts')
def api_get_contacts():
    conn = dbConnect()
    cursor = conn.cursor()
    id = request.args.get('id')
    if (id != None):
        cursor.execute(f'SELECT * FROM contacts WHERE company_id = "{id}"')
    else:
        return {"Syntax incorrect": "Needs ID in format /api/contacts?id=1"}
    data = []
    for contact_id, company_id, lastname, firstname, area, phone, date, future, notes in cursor:
        data.append({
            "company_id": company_id,
            "lastname": lastname,
            "firstname": firstname,
            "area": area,
            "contact_id": contact_id,
            "phone": phone,
            "date_contacted": date,
            "can_contact_future": future,
            "notes": notes
        })
    conn.close()
    return data


@app.route('/api/tech')
def api_get_tech():
    conn = dbConnect()
    cursor = conn.cursor()
    id = request.args.get('id')
    if (id != None):
        cursor.execute(f'''
        SELECT technologies.tech_name, technologies.tech_area, company_tech.ct_usednow, company_tech.ct_shouldteach, company_tech.ct_topthree, company_tech.ct_continue, company_tech.tc_collectdate, company_tech.ct_id, company.company_id, technologies.tech_id
        FROM company_tech
        INNER JOIN company ON company.company_id = company_tech.company_id
        INNER JOIN technologies ON technologies.tech_id = company_tech.ct_techid
        WHERE company.company_id = '{id}'
        ''')
    else:
        return {"Syntax incorrect": "Needs ID in format /api/tech?id=1"}
    data = []
    for tech_name, tech_area, ct_usednow, ct_shouldteach, ct_topthree, ct_continue, tc_collectdate, ct_id, company_id, tech_id in cursor:
        data.append({
            "tech_name": tech_name,
            "tech_area": tech_area,
            "ct_usednow": ct_usednow,
            "ct_shouldteach": ct_shouldteach,
            "ct_topthree": ct_topthree,
            "ct_continue": ct_continue,
            "tc_collectdate": tc_collectdate,
            "ct_id": ct_id,
            "company_id": company_id,
            "tech_id": tech_id
        })
    conn.close()
    return data


# -----------------------------INDEX PAGE---------------------------------------------
@app.route('/')
def index():
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM company')
    data = cursor.fetchall()
    company_names = []
    for company in data:
        company_names.append(company[1])
    cursor.execute('SELECT * FROM technologies')
    tech_data = cursor.fetchall()

    conn.close()

    return render_template('index.html', data=data, company_names=company_names, tech_data=tech_data)


@app.route('/rendered_companies')
def rendered_companies():
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM company')
    data = cursor.fetchall()
    conn.close()

    return render_template('rendered_companies.html', data=data)


# -----------------------------COMPANY TECH PAGE---------------------------------------
@app.route('/company_answers', methods=["POST"])
def company_answers():
    selection = request.form['item-dropdown']
    conn = dbConnect()
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
        SELECT technologies.tech_name, technologies.tech_area, company_tech.ct_usednow, company_tech.ct_shouldteach, company_tech.ct_topthree, company_tech.ct_continue, company_tech.tc_collectdate, company_tech.ct_id, company.company_id, technologies.tech_id
        FROM company_tech
        INNER JOIN company ON company.company_id = company_tech.company_id
        INNER JOIN technologies ON technologies.tech_id = company_tech.ct_techid
        WHERE company.company_name = '{str(selection)}'
        ''')
        data = cursor.fetchall()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    try:
        cursor.execute(f'''SELECT company_id FROM company WHERE company_name = "{selection}"''')
        new_data = cursor.fetchall()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    company_id = new_data[0][0]
    try:
        cursor.execute(f'SELECT * FROM company WHERE company_id = "{company_id}"')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    company_info = cursor.fetchall()
    conn.close()
    return render_template('answers.html', selection=selection, data=data, company_id=company_id,
                           company_info=company_info)


# -------------------------ADD COMPANY COMPONENT-------------------------------
@app.route('/new_company_form')
def new_company_form():
    tech_areas = ['frontend_lang', 'frontend_frame', 'backend_lang', 'backend_frame', 'mobile', 'network', 'security',
                  'devops', 'analytics', 'database', 'cloud', 'communication']
    cmp_areas = ['technology', 'healthcare', 'manufacturing', 'banking', 'investments', 'marketing', 'architechture',
                 'education', 'government', 'grocery']
    contact_areas = ['it', 'clevel', 'security', 'dev', 'other']
    state_apprevs = ["AL", "AK", "AZ", "AR", "CA", "CZ", "CO", "CT", "DE", "DC", "FL", "GA", "GU", "HI", "ID", "IL",
                     "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
                     "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT",
                     "VT", "VI", "VA", "WA", "WV", "WI", "WY"]
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM company')
    data = cursor.fetchall()
    company_names = []
    for company in data:
        company_names.append({'name': company[1], 'id': company[0]})

    conn.close()
    return render_template('newCompany.html', tech_areas=tech_areas, company_names=company_names,
                           state_apprevs=state_apprevs, cmp_areas=cmp_areas, contact_areas=contact_areas)


# -------------------------ADD CONTACT COMPONENT-------------------------------
@app.route('/new_contact_form')
def new_contact_form():
    tech_areas = ['frontend_lang', 'frontend_frame', 'backend_lang', 'backend_frame', 'mobile', 'network', 'security',
                  'devops', 'analytics', 'database', 'cloud', 'communication']
    cmp_areas = ['technology', 'healthcare', 'manufacturing', 'banking', 'investments', 'marketing', 'architechture',
                 'education', 'government', 'grocery']
    contact_areas = ['it', 'clevel', 'security', 'dev', 'other']
    state_apprevs = ["AL", "AK", "AZ", "AR", "CA", "CZ", "CO", "CT", "DE", "DC", "FL", "GA", "GU", "HI", "ID", "IL",
                     "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
                     "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT",
                     "VT", "VI", "VA", "WA", "WV", "WI", "WY"]
    id = request.args.get('id')
    return render_template('newContact.html', company_id=id, tech_areas=tech_areas, state_apprevs=state_apprevs,
                           cmp_areas=cmp_areas, contact_areas=contact_areas)


# -------------------------ADD COMPANY TECH COMPONENT-------------------------------
@app.route('/new_company_tech_form')
def new_company_tech_form():
    db_techs = []
    company_id = request.args.get('id')
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM technologies')
    data = cursor.fetchall()
    for tech in data:
        db_techs.append(tech)

    conn.close()

    return render_template('newCompanyTech.html', company_id=company_id, db_techs=db_techs) \

# -------------------------ADD TECH COMPONENT-------------------------------
@app.route('/new_tech_form')
def new_tech_form():
    tech_areas = ['frontend_lang', 'frontend_frame', 'backend_lang', 'backend_frame', 'mobile', 'network', 'security',
                  'devops', 'analytics', 'database', 'cloud', 'communication']
    return render_template('newTech.html', tech_areas=tech_areas)


# -----------------------------SUBMIT COMPANY PAGE---------------------------------------
@app.route('/submit_company', methods=['POST'])
def submit_company():
    company_name = request.form['company_name_input']
    add_street = request.form['add_street']
    add_state = request.form['add_state']
    add_zip = request.form['add_zip']
    cmp_size = request.form['cmp_size']
    area = request.form['cmp_area']
    hire2year = request.form['hire2year']
    intern = request.form['intern']
    db_companies = []
    conn = dbConnect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM company")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    for name in cur:
        db_companies.append(name)

    if str(company_name) not in str(db_companies):
        try:
            cur.execute(
                f'''CALL EnterCompanies("{company_name}", "{add_street}", "{add_state}", "{add_zip}", "{cmp_size}", "{area}", "{hire2year}", "{intern}"); ''')
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(2)

    try:
        cur.execute("SELECT company_id  FROM company WHERE company_id =(SELECT MAX(company_id) FROM `company`)")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    id = cur.fetchone()[0]

    conn.commit()

    conn.close()

    return {"id": id, "html": render_template('submit_company.html', id=id, add_street=add_street, add_state=add_state,
                                              add_zip=add_zip,
                                              company_name=company_name,
                                              cmp_size=cmp_size, area=area, hire2year=hire2year, intern=intern)}


# -----------------------------SUBMIT TECHNOLOGY PAGE---------------------------------------
@app.route('/submit_tech', methods=['POST'])
def submit_tech():
    tech_area = request.form['tech_area']
    tech_name = request.form['tech_name']

    conn = dbConnect()
    cur = conn.cursor()
    db_technologies = []
    tech_exists = False

    try:
        cur.execute("SELECT * FROM technologies")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    for name in cur:
        db_technologies.append(name)

    for tech in db_technologies:
        if str(tech_name) == str(tech[2]) and str(tech_area) == str(tech[1]):
            tech_exists = True

    if tech_exists == False:
        try:
            cur.execute(
                f'''CALL EnterTechnologies("{tech_name}", "{tech_area}"); ''')
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(2)

    conn.commit()
    conn.close()
    return {"success"}


# -----------------------------SUBMIT COMPANY TECHNOLOGY PAGE---------------------------------------
@app.route('/submit_company_tech', methods=['POST'])
def submit_company_tech():
    tech_area = request.form['tech_area']
    used_now = request.form['used_now']
    should_teach = request.form['should_teach']
    top_three = request.form['top_three']
    should_continue = request.form['continue']
    today = datetime.date.today()
    company_id = request.form['company_id']
    company_techs = []
    conn = dbConnect()
    cur = conn.cursor()
    db_technologies = []

    try:
        cur.execute("SELECT * FROM technologies")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    for name in cur:
        db_technologies.append(name)
    try:
        cur.execute(f'SELECT * FROM company_tech WHERE company_id = "{company_id}"')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    data = cur.fetchall()
    for row in data:
        company_techs.append(row[2])
    if str(tech_area) not in str(company_techs):
        try:
            cur.execute(
                f'''CALL EnterCompanyTech("{company_id}", "{tech_area}", "{used_now}", 
                    "{should_teach}", "{top_three}", "{should_continue}", "{today}"); ''')
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(2)

    conn.commit()
    conn.close()

    return {"success"}


# -----------------------------SUBMIT CONTACT PAGE---------------------------------------
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    company_id = request.form['company_id']
    contact_last = request.form['contact_last']
    contact_first = request.form['contact_first']
    contact_area = request.form['contact_area']
    contact_phone = request.form['contact_phone']
    contact_future = request.form['contact_future']
    contact_notes = request.form['contact_notes']
    today = datetime.date.today()

    conn = dbConnect()
    cur = conn.cursor()
    try:
        cur.execute(
            f'''CALL EnterContact("{company_id}", "{contact_last}", "{contact_first}", "{contact_area}", "{contact_phone}", "{today}", "{contact_future}", "{contact_notes}"); ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    try:
        cur.execute(
            f'SELECT company_name FROM company WHERE company_id = "{company_id}"')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    data = cur.fetchall()
    company_name = data[0][0]
    conn.commit()
    conn.close()
    return render_template('submit_contact.html', company_name=company_name, contact_last=contact_last,
                           contact_first=contact_first, contact_area=contact_area, contact_phone=contact_phone,
                           contact_future=contact_future, contact_notes=contact_notes, date=today)


# -----------------------------DELETE COMPANY TECH PAGE---------------------------------------
@app.route('/delete_company_tech', methods=['POST'])
def delete_company_tech():
    ct_id = request.form['ct_id']
    conn = dbConnect()
    cur = conn.cursor()
    try:
        cur.execute(
            f'''CALL DeleteCompanyTech("{ct_id}"); ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)

    conn.commit()
    conn.close()
    return {"Success "}


# -----------------------------DELETE CONTACT PAGE---------------------------------------
@app.route('/delete_contact', methods=['POST'])
def delete_contact():
    contact_id = request.form['contact_id']
    company_id = request.form['company_id']
    contact_last = request.form['contact_last']
    contact_first = request.form['contact_first']
    conn = dbConnect()
    cur = conn.cursor()
    try:
        cur.execute(
            f'''CALL DeleteContact("{contact_id}"); ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)

    try:
        cur.execute(
            f'SELECT company_name FROM company WHERE company_id = "{company_id}"')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    data = cur.fetchall()
    company_name = data[0][0]
    conn.commit()
    conn.close()
    return render_template('delete_contact.html', company_name=company_name, contact_last=contact_last,
                           contact_first=contact_first)


# -----------------------------MODIFY COMPANY TECH PAGE---------------------------------------
@app.route('/modify_company_tech')
def modify_company_tech():
    ct_id = request.args.get('id')
    tech_areas = ['frontend_lang', 'frontend_frame', 'backend_lang', 'backend_frame', 'mobile', 'network', 'security',
                  'devops', 'analytics', 'database', 'cloud', 'communication']
    db_techs = []
    conn = dbConnect()
    cur = conn.cursor()
    try:
        cur.execute(
            f'''SELECT ct.*, c.company_name, t.tech_area, t.tech_name 
                FROM company_tech ct 
                JOIN company c ON c.company_id = ct.company_id 
                JOIN technologies t ON ct.ct_techid = t.tech_id 
                WHERE ct_id = "{ct_id}"; ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)

    ct_id, company_id, ct_techid, ct_usednow, ct_shouldteach, ct_topthree, ct_continue, tc_collectdate, company_name, tech_area, tech_name = cur.fetchone()
    data = {
        "ct_id": ct_id,
        "company_id": company_id,
        "company_name": company_name,
        "ct_techid": ct_techid,
        "ct_usednow": ct_usednow,
        "ct_shouldteach": ct_shouldteach,
        "ct_topthree": ct_topthree,
        "ct_continue": ct_continue,
        "tech_area": tech_area,
        "tech_name": tech_name
    }

    try:
        cur.execute(
            f'''SELECT tech_name FROM technologies WHERE tech_id = "{ct_techid}"; ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    new_data = cur.fetchall()
    prev_tech_name = new_data[0][0]
    cur.execute('SELECT * FROM technologies')
    new_data = cur.fetchall()
    for tech in new_data:
        db_techs.append(tech)

    conn.commit()
    conn.close()

    return render_template('modify_company_tech.html', data=data, tech_areas=tech_areas, db_techs=db_techs,
                           prev_tech_name=prev_tech_name)


# -----------------------------MODIFY COMPANY TECH SUBMIT PAGE---------------------------------------
@app.route('/modified_ct', methods=['POST'])
def modified_ct():
    ct_id = request.form['ct_id']
    company_id = request.form['company_name']
    ct_techid = request.form['ct_techid']
    ct_usednow = request.form['used_now']
    ct_shouldteach = request.form['should_teach']
    ct_topthree = request.form['top_three']
    ct_continue = request.form['continue']
    today = datetime.date.today()
    conn = dbConnect()
    cur = conn.cursor()
    try:
        cur.execute(
            f'''CALL ModifyCompanyTech("{ct_id}", "{company_id}", "{ct_techid}", "{ct_usednow}", "{ct_shouldteach}", "{ct_topthree}", "{ct_continue}", "{today}"); ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)

    try:
        cur.execute(
            f'''SELECT company_name FROM company WHERE company_id = "{company_id}"; ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    data = cur.fetchall()
    company_name = data[0][0]

    try:
        cur.execute(f'''SELECT tech_name FROM technologies 
        INNER JOIN company_tech ON company_tech.ct_techid = technologies.tech_id
        WHERE ct_techid = "{ct_techid}"; ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    tech_name = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return render_template('modified_ct.html', ct_id=ct_id, company_name=company_name, ct_usednow=ct_usednow,
                           ct_shouldteach=ct_shouldteach, ct_topthree=ct_topthree, ct_continue=ct_continue, date=today,
                           tech_name=tech_name)


# -----------------------------MODIFY CONTACT PAGE---------------------------------------
@app.route('/modify_contact')
def modify_contact():
    id = request.args.get('id')
    contact_areas = ['it', 'clevel', 'security', 'dev', 'other']
    conn = dbConnect()
    cur = conn.cursor()
    try:
        cur.execute(
            f'''SELECT * FROM contacts WHERE contact_id = {id}; ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    contactid, companyid, lastname, firstname, area, phone, lastcomm, future, notes = cur.fetchone()
    data = {
        "contactid": contactid,
        "companyid": companyid,
        "lastname": lastname,
        "firstname": firstname,
        "area": area,
        "phone": phone,
        "lastcomm": lastcomm,
        "future": future,
        "notes": notes
    }
    conn.close()
    return render_template('modify_contact.html', data=data, contact_areas=contact_areas)


# -----------------------------MODIFY CONTACT SUBMIT PAGE---------------------------------------
@app.route('/modified_contact', methods=['POST'])
def modified_contact():
    contact_id = request.form['contact_id']
    company_id = request.form['company_id']
    contact_last = request.form['contact_last']
    contact_first = request.form['contact_first']
    contact_area = request.form['contact_area']
    contact_phone = request.form['contact_phone']
    contact_future = request.form['contact_future']
    contact_notes = request.form['contact_notes']
    contact_lastcomm = request.form['contact_lastcomm']
    conn = dbConnect()
    cur = conn.cursor()
    try:
        cur.execute(
            f'''CALL ModifyContacts("{contact_id}", "{company_id}", "{contact_last}", "{contact_first}", "{contact_area}", "{contact_phone}", "{contact_lastcomm}", "{contact_future}", "{contact_notes}"); ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)

    try:
        cur.execute(
            f'''SELECT company_name FROM company WHERE company_id = "{company_id}"; ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    data = cur.fetchall()
    company_name = data[0][0]

    conn.commit()
    conn.close()
    return render_template('modified_contact.html', contact_id=contact_id, company_name=company_name,
                           contact_last=contact_last, contact_first=contact_first, contact_area=contact_area,
                           contact_phone=contact_phone, contact_future=contact_future, contact_notes=contact_notes,
                           contact_lastcomm=contact_lastcomm)


# -----------------------------MODIFY COMPANY COMPONENT---------------------------------------
@app.route('/update_company_form')
def update_company_form():
    conn = dbConnect()
    cursor = conn.cursor()
    id = request.args.get('id')
    cursor.execute(f'SELECT * FROM company WHERE company_id = {id}')
    id, name, street, state, zip, size, area, hire2year, intern = cursor.fetchone()
    conn.close()
    state_apprevs = ["AL", "AK", "AZ", "AR", "CA", "CZ", "CO", "CT", "DE", "DC", "FL", "GA", "GU", "HI", "ID", "IL",
                     "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
                     "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT",
                     "VT", "VI", "VA", "WA", "WV", "WI", "WY"]
    cmp_areas = ['technology', 'healthcare', 'manufacturing', 'banking', 'investments', 'marketing', 'architechture',
                 'education', 'government', 'grocery']
    return render_template('updateCompany.html', company_name=name, add_street=street, add_state=state, add_zip=zip,
                           cmp_size=size, area=area, hire2year=hire2year, intern=intern, state_apprevs=state_apprevs,
                           company_id=id, cmp_areas=cmp_areas)


# -----------------------------MODIFY COMPANY SUBMIT PAGE---------------------------------------
@app.route('/modified_company', methods=['POST'])
def modified_company():
    company_id = request.form['company_id']
    company_name = request.form['company_name_input']
    add_street = request.form['add_street']
    add_state = request.form['add_state']
    add_zip = request.form['add_zip']
    cmp_size = request.form['cmp_size']
    area = request.form['cmp_area']
    hire2year = request.form['hire2year']
    intern = request.form['intern']
    conn = dbConnect()
    cur = conn.cursor()
    try:
        cur.execute(
            f'''CALL ModifyCompany("{company_id}", "{company_name}", "{add_street}", "{add_state}", "{add_zip}", "{cmp_size}", "{area}", "{hire2year}", "{intern}"); ''')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    conn.commit()
    conn.close()
    return render_template('modified_company.html', company_name=company_name, add_street=add_street,
                           add_state=add_state, add_zip=add_zip, cmp_size=cmp_size, area=area, hire2year=hire2year,
                           intern=intern, company_id=company_id)


@app.route("/get_piechart_data/<size_id>")
def get_piechart_data(size_id):
    conn = dbConnect()
    cur = conn.cursor()
    tech_ids = []
    percentages = []
    names = []
    other_percentage = 0
    companies = []
    lowest = []
    low = []
    medium = []
    high = []
    higher = []
    highest = []

    try:
        cur.execute(f'SELECT ct_techid, company_id FROM company_tech')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    data = cur.fetchall()
    total = len(data)
    for row in data:
        tech_ids.append(row[0])
        companies.append({"company_id": row[1], "tech_id": row[0]})
    for row in companies:
        try:
            cur.execute(f'SELECT company_size FROM company WHERE company_id = {row["company_id"]}')
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(2)
        data = cur.fetchall()
        if 1 < data[0][0] < 1001:
            lowest.append(row["tech_id"])
        elif 1000 < data[0][0] < 5001:
            low.append(row["tech_id"])
        elif 5000 < data[0][0] < 10001:
            medium.append(row["tech_id"])
        elif 10000 < data[0][0] < 50001:
            high.append(row["tech_id"])
        elif 50000 < data[0][0] < 100000:
            higher.append(row["tech_id"])
        elif 100000 < data[0][0]:
            highest.append(row["tech_id"])
    if int(size_id) == 0:
        counter = Counter(tech_ids)
        number_count = counter.most_common(3)
        for i in number_count:
            percentages.append(i[1] / total * 100)
            other_percentage += i[1] / total * 100
            try:
                cur.execute(f'SELECT tech_name FROM technologies WHERE tech_id = {i[0]}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            names.append(data[0][0])
    if int(size_id) == 1:
        counter = Counter(lowest)
        total = len(lowest)
        number_count = counter.most_common(3)
        for i in number_count:
            percentages.append(i[1] / total * 100)
            other_percentage += i[1] / total * 100
            try:
                cur.execute(f'SELECT tech_name FROM technologies WHERE tech_id = {i[0]}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            names.append(data[0][0])
    if int(size_id) == 2:
        counter = Counter(low)
        total = len(low)
        number_count = counter.most_common(3)
        for i in number_count:
            percentages.append(i[1] / total * 100)
            other_percentage += i[1] / total * 100
            try:
                cur.execute(f'SELECT tech_name FROM technologies WHERE tech_id = {i[0]}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            names.append(data[0][0])
    if int(size_id) == 3:
        counter = Counter(medium)
        total = len(medium)
        number_count = counter.most_common(3)
        for i in number_count:
            percentages.append(i[1] / total * 100)
            other_percentage += i[1] / total * 100
            try:
                cur.execute(f'SELECT tech_name FROM technologies WHERE tech_id = {i[0]}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            names.append(data[0][0])
    if int(size_id) == 4:
        counter = Counter(high)
        total = len(high)
        number_count = counter.most_common(3)
        for i in number_count:
            percentages.append(i[1] / total * 100)
            other_percentage += i[1] / total * 100
            try:
                cur.execute(f'SELECT tech_name FROM technologies WHERE tech_id = {i[0]}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            names.append(data[0][0])
    if int(size_id) == 5:
        counter = Counter(higher)
        total = len(higher)
        number_count = counter.most_common(3)
        for i in number_count:
            percentages.append(i[1] / total * 100)
            other_percentage += i[1] / total * 100
            try:
                cur.execute(f'SELECT tech_name FROM technologies WHERE tech_id = {i[0]}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            names.append(data[0][0])
    if int(size_id) == 6:
        counter = Counter(highest)
        total = len(highest)
        number_count = counter.most_common(3)
        for i in number_count:
            percentages.append(i[1] / total * 100)
            other_percentage += i[1] / total * 100
            try:
                cur.execute(f'SELECT tech_name FROM technologies WHERE tech_id = {i[0]}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            names.append(data[0][0])
    names.append("Remaining Technologies")
    labels = names
    other_percentage = 100 - other_percentage
    percentages.append(other_percentage)
    return jsonify({"chart_data": percentages, "labels": labels})


@app.route("/get_barchart_data/<size_id>")
def get_barchart_data(size_id):
    conn = dbConnect()
    cur = conn.cursor()
    cmp_sizes = []
    names = ["1-1000", "1001-5000", "5001-10000", "10001-50000", "50001-100000"]
    ranges = [0, 0, 0, 0, 0, 0]
    return_data = []
    labels = []

    try:
        cur.execute(f'SELECT company_size, company_name FROM company')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    data = cur.fetchall()
    for row in data:
        cmp_sizes.append({"name": row[1], "size": row[0]})
    for i in cmp_sizes:
        if 1 < int(i["size"]) < 1001:
            ranges[0] += 1
        elif 1000 < int(i["size"]) < 5001:
            ranges[1] += 1
        elif 5000 < int(i["size"]) < 10001:
            ranges[2] += 1
        elif 10000 < int(i["size"]) < 50001:
            ranges[3] += 1
        elif 50000 < int(i["size"]) < 100000:
            ranges[4] += 1
        elif int(i["size"]) > 100000:
            ranges[5] += 1
    if int(size_id) != 0:
        if int(size_id) == 1:
            for row in cmp_sizes:
                if 1 < int(row["size"]) < 1001:
                    return_data.append(row["size"])
                    labels.append(row["name"])
        elif int(size_id) == 2:
            for row in cmp_sizes:
                if 1000 < int(row["size"]) < 5001:
                    return_data.append(row["size"])
                    labels.append(row["name"])
        elif int(size_id) == 3:
            for row in cmp_sizes:
                if 5000 < int(row["size"]) < 10001:
                    return_data.append(row["size"])
                    labels.append(row["name"])
        elif int(size_id) == 4:
            for row in cmp_sizes:
                if 10000 < int(row["size"]) < 50001:
                    return_data.append(row["size"])
                    labels.append(row["name"])
        elif int(size_id) == 5:
            for row in cmp_sizes:
                if 50000 < int(row["size"]) < 100000:
                    return_data.append(row["size"])
                    labels.append(row["name"])
        elif int(size_id) == 6:
            for row in cmp_sizes:
                if int(row["size"]) > 100000:
                    return_data.append(row["size"])
                    labels.append(row["name"])
    else:
        return_data = ranges
        labels = names
    return jsonify({"chart_data": return_data, "labels": labels})


@app.route("/get_tech_data/<size_id>")
def get_tech_data(size_id):
    conn = dbConnect()
    cur = conn.cursor()
    tech_names = []
    values = []
    tech_areas = []
    company_tech = []
    lowest = []
    low = []
    medium = []
    high = []
    higher = []
    highest = []
    try:
        cur.execute(f'SELECT ct_techid, company_id FROM company_tech')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(2)
    data = cur.fetchall()
    for i in data:
        company_tech.append({"tech_id": i[0], "company_id": i[1]})
    for i in company_tech:
        try:
            cur.execute(f'SELECT company_size FROM company WHERE company_id = {i["company_id"]}')
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(2)
        data = cur.fetchall()
        if int(data[0][0]) < 1001:
            lowest.append(i["tech_id"])
        elif 1000 < int(data[0][0]) < 5001:
            low.append(i["tech_id"])
        elif 5000 < int(data[0][0]) < 10001:
            medium.append(i["tech_id"])
        elif 10000 < int(data[0][0]) < 50001:
            high.append(i["tech_id"])
        elif 50000 < int(data[0][0]) < 100000:
            higher.append(i["tech_id"])
        elif int(data[0][0]) > 100000:
            highest.append(i["tech_id"])
    if int(size_id) == 0:
        for i in company_tech:
            try:
                cur.execute(
                    f'SELECT tech_area FROM technologies INNER JOIN company_tech ON company_tech.ct_techid = technologies.tech_id WHERE company_tech.ct_techid = {i["tech_id"]}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            tech_names.append(data[0][0])
            counter = Counter(tech_names)
            number_count = counter.most_common()
    elif int(size_id) == 1:
        for i in lowest:
            try:
                cur.execute(
                    f'SELECT tech_area FROM technologies INNER JOIN company_tech ON company_tech.ct_techid = technologies.tech_id WHERE company_tech.ct_techid = {i}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            tech_names.append(data[0][0])
            counter = Counter(tech_names)
            number_count = counter.most_common()
    elif int(size_id) == 2:
        for i in low:
            try:
                cur.execute(
                    f'SELECT tech_area FROM technologies INNER JOIN company_tech ON company_tech.ct_techid = technologies.tech_id WHERE company_tech.ct_techid = {i}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            tech_names.append(data[0][0])
            counter = Counter(tech_names)
            number_count = counter.most_common()
    elif int(size_id) == 3:
        for i in medium:
            try:
                cur.execute(
                    f'SELECT tech_area FROM technologies INNER JOIN company_tech ON company_tech.ct_techid = technologies.tech_id WHERE company_tech.ct_techid = {i}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            tech_names.append(data[0][0])
            counter = Counter(tech_names)
            number_count = counter.most_common()
    elif int(size_id) == 4:
        for i in high:
            try:
                cur.execute(
                    f'SELECT tech_area FROM technologies INNER JOIN company_tech ON company_tech.ct_techid = technologies.tech_id WHERE company_tech.ct_techid = {i}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            tech_names.append(data[0][0])
            counter = Counter(tech_names)
            number_count = counter.most_common()
    elif int(size_id) == 5:
        for i in higher:
            try:
                cur.execute(
                    f'SELECT tech_area FROM technologies INNER JOIN company_tech ON company_tech.ct_techid = technologies.tech_id WHERE company_tech.ct_techid = {i}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            tech_names.append(data[0][0])
            counter = Counter(tech_names)
            number_count = counter.most_common()
    elif int(size_id) == 6:
        for i in highest:
            try:
                cur.execute(
                    f'SELECT tech_area FROM technologies INNER JOIN company_tech ON company_tech.ct_techid = technologies.tech_id WHERE company_tech.ct_techid = {i}')
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(2)
            data = cur.fetchall()
            tech_names.append(data[0][0])
            counter = Counter(tech_names)
            number_count = counter.most_common()
    for i in number_count:
        values.append(i[1])
        tech_areas.append(i[0])

    labels = tech_areas
    return jsonify({"chart_data": values, "labels": labels})


@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/credits')
def credits():
    return render_template('credits.html')


if __name__ == '__main__':
    app.run()
