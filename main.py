from flask import Flask, render_template, redirect, request, session, flash, url_for
#from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re
import server
from server import MySQLConnection, Validator, connectToMySQL, QuerySearch
app=Flask(__name__)
app.secret_key = "keepitsecretkeepitsafe"
bcrypt = Bcrypt(app)
import re

#EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
#pass_valid = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*?^])[a-zA-z0-9!@#$%&*?^]+$')

MySQLConnection('travel_bug')
connectToMySQL('travel_bug')
Validator = Validator()
QuerySearch = QuerySearch()
#render login/registration page
@app.route("/")
def registration():
      return render_template("login_register.html")

#registers user
@app.route("/register", methods=['GET','POST'])
def register():
      is_valid = True

      first_name = request.form['f-name']
      last_name = request.form['l-name']
      email = request.form['email']
      password = request.form['password']
      confirm_password = request.form['password-c']

      check_username = Validator.check_name(first_name, last_name)
      check_password = Validator.check_pw(password=password, confirm_pw=confirm_password)
      if check_username == True: #if check_username fails, set is_valid to False
            is_valid = False
            flash("First or last name does not meet requirements")
      if check_password == True: #if check_password fails, set is_valid to False
            is_valid = False 
            flash("Passwords must match and be a minimum of 8 characters long containing one lowercase, one uppercase, one number and one special character")
      #if all validations pass, insert info into users database and retrieve from database
      form = [first_name, last_name, email, password]
      new_user = QuerySearch.user_add(form)
      print(new_user)
      if new_user:
            user_data = new_user[0]
            session['user_id'] = user_data['id']

      if is_valid == False:
            return redirect("/")
      if is_valid == True:
            return redirect("/newsfeed")

#logins in user
@app.route("/login", methods=['POST'])
def login():
      #checks to make sure email is entered
      email = request.form['email']
      password = request.form['password']
      user_data = Validator.check_reg(email, password)
      if user_data == False:
            flash("Email or password incorrect")
            return redirect("/")
      else:
            session['user_id'] = user_data['id']
            print(user_id)
            return redirect("/newsfeed")

#user is brought here if login or registration is successful
#render newsfeed html
@app.route("/newsfeed")
def newsfeed():
      all_pins = QuerySearch.pin_all()
      #connect user name to pins and order by most recent first, return all pins
      #check if user is in session for add pin form
      if 'user_id' in session:
            user_id = session['user_id']
      return render_template("newsfeed.html", all_pins=all_pins, user_id=user_id)


#adds pin
#@app.route("/addpin/<user_id", methods=['POST'])
#def addPin(user_id):
#      is_valid = True
      #check to make sure the pin passes validation
            #if pin doesn't pass validations
            #send flash message
#      if is_valid: #if it passes validations
            #add pin to database
#      return redirect("/newsfeed") #redirect to newsfeed? or profile?

#@app.route("/editpin/<pin_id>", methods = ['GET', 'POST'])
#def edit_pin_page(pin_id):
      #if user is not in session, return to registration/login page
#      if 'user_id' not in session:
#            return redirect("/")
      #query database to find if user exists, select first instance (should only be one)
      #join user_data with pin_data from pin_id
      #send user information and pin information to pin edit html
#      return render_template("PIN_EDIT_HTML.html", user_data=user_data, pin_data=pin_data) #sends user_data and pin_data

#actually edits pin when form is submitted
#@app.route("/pin/edit/<pin_id>")
#def edit_pin(pin_id):
      #select from db using user_id and pin_id
      #check validations for new information submitted
      #if validations fail
#            flash("") #flash messages based on what failed
      #if validations passed
#            flash("Pin updated successfully")
            #query database to update specific pin
#      return redirect(url_for('profile') #returns to profile page or newsfeed?


#deletes pin from db
@app.route("/delete/pin/<pin_id>", methods =['POST'])
def deletePin(pin_id):
      #delete pin from db
      return redirect(url_for('profile')) #redirect to profile or newsfeed?

#render profile page html
#@app.route("/profile/<user_id>")
#def profile(user_id):
      #if user is in session, return to registration/login page
#      if 'user_id' not in session:
#            return redirect("/")
      #query database to find if user_id exists
      #if user exists, select first user (should only be one)
      #join user to pins and other tables that need to be displayed on profile page
      #cycle through all pins to display them
#      return render_template("profile.html")

#edit profile html page
#@app.route("/profile/edit/<user_id>", methods=['POST', 'GET'])
#def edit_profile_page(user_id):
      #if user is not in session, return to registration/login page
#      if 'user_id' not in session:
#            return redirect("/")
      #query database to find if user exists, select first instance (should only be one)
      #send user information to edit profile html
#      return render_template("EDITPROFILE_HTML", user_data=user_data) #sends user_data to html page

#actually edits user when form is submitted
#@app.route("/edit/profile/<user_id>", methods = ['POST'])
#def edit_profile(user_id):
      #select from db using user_id
      #check validations for new information submitted
      #if validations fail
#            flash("") #flash messages based on what failed
      #if validations passed
#            flash("Profile updated successfully")
            #query database to update specific user
#      return redirect(url_for('profile') #returns to profile page

#deletes user from db
#@app.route("delete/profile/<user_id>", methods = ['POST'])
#def delete_profile(user_id):
      #delete user from db
#      return redirect("/") #redirects to login/registration

#logs out user
@app.route("/logout")
def logout():
      session.clear()
      return redirect("/homepage") #return to homepage or profile?

if __name__=="__main__":
  app.run(debug=True)