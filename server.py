from flask import Flask, render_template, request, redirect
from datetime import datetime
import re 

# a cursor is the object we use to interact with the database
import pymysql.cursors
# this class will give us an instance of a connection to our database
class MySQLConnection:
    def __init__(self, db):
        connection = pymysql.connect(host = 'localhost',
                                    user = 'root', # change the user and password as needed
                                    password = 'root', 
                                    db = db,
                                    charset = 'utf8mb4',
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
        # establish the connection to the database
        self.connection = connection
    # the method to query the database
    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                query = cursor.mogrify(query, data)
                print("Running Query:", query)
     
                executable = cursor.execute(query, data)
                if query.lower().find("insert") >= 0:
                    # INSERT queries will return the ID NUMBER of the row inserted
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    # SELECT queries will return the data from the database as a LIST OF DICTIONARIES
                    result = cursor.fetchall()
                    return result
                else:
                    # UPDATE and DELETE queries will return nothing
                    self.connection.commit()
            except Exception as e:
                # if the query fails the method will return FALSE
                print("Something went wrong", e)
                return False
            finally:
                # close the connection
                self.connection.close() 

# connectToMySQL receives the database we're using and uses it to create an instance of MySQLConnection
def connectToMySQL(db):
    return MySQLConnection(db)

class Validator: # Validation check
    def pw_check(self, password = "", confirm_pw = ""): # password and confirm_pw values from request.form
        flag = False
        while True:
            if (len(password)<8):
                flag = True
                return flag
            elif password != confirm_pw:
                flag = True
                return flag
            elif not re.search("[a-z]", password):
                flag = True
                return flag
            elif not re.search("[A-Z]", password):
                flag = True
                return flag
            elif not re.search("[0-9]", password):
                flag = True
                return flag
            elif not re.search("[_@$]", password):
                flag = True
                return flag
            elif re.search("\s", password):
                flag = True
                return flag
            else: 
                return flag

    def reg_check(self, email): # email values from request.form
        mysql = connectToMySQL("travel_bug")
        query = next((item for item in mysql.query_db("SELECT * FROM users") if item["email"] == email), None)
        flag = False
        if query:
            if email == query['email']:
                flag = True
                return flag
        return flag

    def name_check(self, first_name, last_name): # first & last name from request.form
        flag = False
        name = [first_name, last_name]
        while True:
            if (len(name[0])<2 or len(name[1])<2): 
                flag = True
                return flag
            elif not re.search("[a-z]", name[0]) or not re.search("[a-z]", name[1]):
                flag = True
                return flag
            elif (not re.search("[A-Z]", name[0]) or not re.search("[A-Z]", name[1])):
                flag = True
                return flag
            elif (re.search("[0-9]", name[0]) or re.search("[0-9]", name[1])):
                flag = True
                return flag
            elif (re.search("[_@$]", name[0]) or re.search("[_@$]", name[1])):
                flag = True
                return flag
            else: 
                return flag

    def pin_owner(self, user_id, pin_id):
        flag = True
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT * FROM pins WHERE id like %(pin_id)s")
        if query:
            if query[0]["user_id"] == user_id:
                flag = False
                return flag 
        return flag
    
    def pin_check(self, pin_form):
        flag = False
        if pin_form["user_id"] == "":
            flag = True
            return flag
        if pin_form["post"] == "":
            flag = True
            return flag
        if pin_form["go"] == "":
            pin_form["go"] = None
        if pin_form["avoid"] == "":
            pin_form["avoid"] = None
        if pin_form["picture"] == "":
            pin_form["picture"] = "default_pin.jpg"
        return pin_form

class QuerySearch:
    def add_user_to_db(self, form): # add user to db
        if form["avatar"] == "":
            form["avatar"] = "default.jpg"
        try:
            mysql = connectToMySQL("travel_bug")
            query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at, avatar) VALUES (%(fn)s, %(ln)s, %(email)s, NOW(), NOW(), %(avatar)s);"
            data = {
            "first_name": form["first_name"],
            "last_name": form["last_name"],
            "email": form["email"].lower(),
            "password": form["password"],
            "avatar": form["avatar"]
            }
            add_user = mysql.query_db(query, data)
            mysql = connectToMySQL("travel_bug")
            user = next((item for item in mysql.query_db("SELECT id, first_name, last_name, email, avatar FROM users") if item["email"] == email), None)
            return user
        except:
            return False

    def user_check(self, email, password): # does user exist
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT id, email, password FROM users WHERE email like '%(email)s'")
        if query:
            query
        user = next((item for item in mysql.query_db("SELECT * FROM users") if item["email"] == email), None)
        return user

    def pins(self): # gets 10 most recent pins
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT pins.post, pins.created_date, pins.updated_date, pins.go, pins.avoid, pins.picture, users.first_name, users.last_name, locations.location FROM pins LEFT JOIN users ON pins.user_id = users.id LEFT JOIN locations ON pins.location_id = locations.id SORT BY pins.created_date DESC LIMIT 10;")
        # print(query)
        return query

    def users_table(self):
        print(request.form)
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT id, email, first_name, last_name FROM users;")
        return query

    def new(self, form):
        validated = Validator.pin_check(form)
        if validated:
            return validated
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT location FROM locations;")
        if validated["location"] not in query:
            mysql = connectToMySQL("travel_bug")
            query = "INSTERT INTO locations (location) VALUE ('%(location)s')"
            data = {
                "location": validated['location']
            }
            add_location = mysql.query_db(query, data)
        mysql = connectToMySQL("travel_bug")
        query = "INSERT INTO pins (user_id, location_id, post, go, avoid, created_at, updated_at, picture) VALUES (%(user_id)s, %(location_id)s, %(email)s, NOW(), NOW(), %(picture)s);"
        data = {
            "user_id": validated["user_id"],
            "location_id": add_location,
            "post": validated["post"],
            "go": validated["go"],
            "avoid": validated["avoid"],
            "picture": validated["picture"]
        }
        add_pin = mysql.query_db(query, data)
        return False



# @app.route('/register', methods=["POST"])
# def register():
#     is_valid = True
#     print(request.form)
#     print(request.form.keys())
#     for i in key_list:
#         if i not in request.form.keys():
#             is_valid = False
#             flash('All fields required!')
#     if len(request.form['username']) < 2 or len(request.form['name']) < 2:
#         is_valid = False
#         flash('Name and Username needs to be at least 3 characters.')
#     if request.form['password'] and request.form['confirm_pw']:
#         if request.form['password'] != request.form['confirm_pw']:
#             is_valid = False
#             flash('Passwords do not match.')
#         elif request.form['password'] == request.form['confirm_pw'] and len(
#                 request.form['password']) < 7:
#             is_valid = False
#             flash('Password must be at least 8 characters.')
#     if request.form['username']:
#         mysql = connectToMySQL('wish_list')
#         user_query = next(
#             (item for item in mysql.query_db("SELECT * FROM users")
#              if item["username"] == request.form['username']), None)
#         if user_query:
#             if request.form['username'] == user_query['username']:
#                 is_valid = False
#                 flash(
#                     'Username already in use. Please login or use another username.'
#                 )
#     if is_valid == False:
#         return redirect('/main')
#     else:
#         flash('Account created! Please login.')
#         mysql = connectToMySQL("wish_list")
#         query = mysql.query_db(
#             "INSERT INTO users (name, username, password, date_hired) VALUES ('%s', '%s', '%s', '%s');"
#             % (request.form['name'], request.form['username'],
#                request.form['password'], request.form['date_hired']))
#         return redirect('/dashboard')

# UPDATE table_name SET column_name1 = 'some_value', column_name2='another_value' WHERE condition(s)
# @app.route('/login', methods=["POST"])
# def login():
#     is_valid = True
#     if request.form['username']:
#         mysql = connectToMySQL('wish_list')
#         user_query = next(
#             (item for item in mysql.query_db("SELECT * FROM users")
#              if item["username"] == request.form["username"]), None)
#         if user_query:
#             if request.form['username'] == user_query['username']:
#                 if request.form['password'] == user_query['password']:
#                     session['user'] = user_query['id']
#                     session['name'] = user_query['name']
#                     session['key'] = secrets.token_urlsafe(16)
#                     return redirect('/dashboard')
#                 else:
#                     is_valid = False
#             else:
#                 is_valid = False
#         else:
#             is_valid = False
#     else:
#         is_valid = False
#         flash('Email or Password is not valid.')
#     return redirect('/')


# @app.route('/dashboard')
# def dashboard():
#     if 'user' in session.keys() and 'key' in session.keys(
#     ) and session['key'] != None:
#         likes_dict = {}
#         mysql = connectToMySQL("wish_list")
#         query = mysql.query_db("SELECT * FROM wish_lists")
#         check = False
#         for i in query:
#             if session['user'] == i['user_id']:
#                 check = True
#         if check == True:
#             mysql = connectToMySQL("wish_list")
#             query = mysql.query_db(
#                 "SELECT users.name, items.date_added, items.id as 'item_id', items.user_id as 'item_user_id', items.item, wish_lists.id, wish_lists.user_id, wish_lists.item_id FROM wish_lists LEFT JOIN items ON wish_lists.item_id = items.id LEFT JOIN users ON items.user_id = users.id WHERE wish_lists.user_id LIKE '%s' ORDER BY items.date_added ASC;"
#                 % session['user'])
#             item_wished = ""
#             print(query)
#             for i in query:
#                 if item_wished == "":
#                     item_wished = str(i['item_id'])
#                 else:
#                     item_wished += ("','" + str(i['item_id']))
#             print(item_wished)
#             mysql = connectToMySQL("wish_list")
#             others = mysql.query_db(
#                 "SELECT items.item, items.id as 'item_id', users.name, items.date_added FROM wish_list.items LEFT JOIN wish_list.users ON items.user_id = users.id WHERE items.id NOT IN ('%s') ORDER BY items.date_added ASC;"
#                 % item_wished)
#         else:
#             query = []
#             mysql = connectToMySQL("wish_list")
#             others = mysql.query_db(
#                 "SELECT items.item, items.id as 'item_id', users.name, items.date_added FROM wish_list.items LEFT JOIN wish_list.users ON items.user_id = users.id ORDER BY items.date_added ASC;"
#             )
#         print(query)
#         print(others)
#         return render_template('dashboard.html', query=query, others=others)
#     return redirect('/main')


# @app.route('/wish_items/<item_id>')
# def details(item_id):
#     if 'key' not in session.keys() or session['key'] == None:
#         return redirect('/main')
#     mysql = connectToMySQL("wish_list")
#     item_query = mysql.query_db(
#         "SELECT * FROM wish_list.items WHERE items.id like '%s';" % item_id)[0]
#     print(item_query)
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db(
#         "SELECT * FROM wish_list.wish_lists LEFT JOIN items ON wish_lists.item_id = items.id LEFT JOIN users ON wish_lists.user_id = users.id WHERE wish_lists.item_id like '%s';"
#         % item_id)
#     wish_list_name = []
#     for i in query:
#         wish_list_name.append(i['name'])
#     return render_template('wish_items.html',
#                            item_query=item_query,
#                            wish_list_name=wish_list_name)


# @app.route('/wish_items/create')
# def new_item():
#     if 'key' not in session.keys() or session['key'] == None:
#         return redirect('/main')
#     return render_template('create.html')


# @app.route('/create_new_item', methods=["POST"])
# def create_new_item():
#     if 'key' not in session.keys() or session['key'] == None:
#         return redirect('/main')
#     is_valid = True
#     print(request.form)
#     if request.form['item']:
#         if len(request.form['item']) < 2 or request.form['item'].strip() == "":
#             is_valid = False
#             flash(
#                 "Invalid Item/Product input. Must be not empty and must be longer than 3 characters."
#             )
#     if not request.form['item']:
#         is_valid = False
#         flash(
#             "Invalid Item/Product input. Must be not empty and must be longer than 3 characters."
#         )
#     if is_valid == False:
#         return redirect('/wish_items/create')
#     else:
#         mysql = connectToMySQL("wish_list")
#         query = mysql.query_db(
#             "INSERT INTO items (item, date_added, user_id) VALUES ('%s', '%s', '%s');"
#             % (request.form['item'], datetime.now().date(), session['user']))
#         new_item_id = query
#         mysql = connectToMySQL("wish_list")
#         query = mysql.query_db(
#             "INSERT INTO wish_lists (item_id, user_id) VALUES ('%s', '%s');" %
#             (new_item_id, session['user']))
#     return redirect('/dashboard')


# @app.route('/add/<item_id>')
# def add_item(item_id):
#     if 'key' not in session.keys() or session['key'] == None:
#         return redirect('/main')
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db(
#         "INSERT INTO wish_lists (user_id, item_id) VALUES ('%s', '%s');" %
#         (session['user'], item_id))
#     return redirect('/dashboard')


# @app.route('/delete/<item_id>')
# def delete_item(item_id):
#     if 'key' not in session.keys() or session['key'] == None:
#         return redirect('/main')
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db("SET SQL_SAFE_UPDATES = 0;")
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db(
#         "DELETE FROM wish_lists WHERE wish_lists.item_id LIKE '%s'" % item_id)
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db("DELETE FROM items WHERE items.id LIKE '%s'" %
#                            item_id)
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db("SET SQL_SAFE_UPDATES = 1;")
#     return redirect('/dashboard')


# @app.route('/remove/<item_id>')
# def remove_item(item_id):
#     if 'key' not in session.keys() or session['key'] == None:
#         return redirect('/main')
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db("SET SQL_SAFE_UPDATES = 0;")
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db(
#         "DELETE FROM wish_lists WHERE wish_lists.item_id LIKE '%s' and wish_lists.user_id LIKE '%s'"
#         % (item_id, session['user']))
#     mysql = connectToMySQL("wish_list")
#     query = mysql.query_db("SET SQL_SAFE_UPDATES = 1;")
#     return redirect('/dashboard')