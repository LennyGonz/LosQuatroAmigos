from app import app
from flask import render_template,redirect, request, flash,g,session,url_for,json, Response
from app.models.models import db_connect
from .forms import *
from functools import wraps # for the role_required decorator
from datetime import date, datetime
import ast
import json
###db_connect contains all query methods##
#db = db_connect()
#########################################3

###### LOGIN ########

# Run HomePage


@app.route('/')
def index():
    db = db_connect() # connect to the database
    #print(session.get("user"))
    return render_template('index.html', top_five=db.select_top5_rated())


# Run LogInPage
@app.route('/showLogIn/')
def showLogIn():
    return render_template("Log-In.html")


# Login Logic
@app.route('/login', methods=["GET",'POST'])
def login():
    db = db_connect()
    # Get details from the user
    user_id = request.form['username']
    password = request.form['password']

    # Get details from the db
    user_check = db.select_user_info(user_id)
    empl_check = db.select_employee_info(user_id)

    # Check user details against db
    if user_check and user_check[0][3] == password:
        # only let the user login if the manager has confirmed his registration
        if int(db.is_registered(user_id)[0]) == 1:
            session["user"] = user_id
            session["logged_in"] = True
            session["role"] = "user"
            return view_user_page()
        # user is not registered
        else:
            flash("A manager must register you first!")
            flash("Be Sure to send your $100 Check :)")
            return showLogIn()

    if empl_check and empl_check[0][0] == 'M' and empl_check[1] == password:
        session["user"] = user_id
        session["logged_in"] = True
        session["role"] = "manager"
        return view_management_page()

    if empl_check and empl_check[0][0] == 'C' and empl_check[1] == password:
        session["user"] = user_id
        session["logged_in"] = True
        session["role"] = "chef"
        return view_chef_page()

    if empl_check and empl_check[0][0] == 'D' and empl_check[1] == password:
        session["user"] = user_id
        session["logged_in"] = True
        session["role"] = "deliverer"
        return view_delivery_page()

    else:
        flash("Login Failed :(")
        return showLogIn()

# For relogging in
@app.route('/relogin')
def relogin():
    if session.get("role") == "user":
        return view_user_page()
    if session.get("role") == "manager":
        return view_management_page()
    if session.get("role") == "chef":
        return view_chef_page()
    if session.get("role") == "deliverer":
        return view_delivery_page()




# Role Checking Decorator to Ensure Only Eligible User Has Access
def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if get_current_user_role() not in roles:
                flash('Authentication error, please check your details and try again', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)

        return wrapped

    return wrapper

# Get User
def get_current_user_role():
    return session.get('role')

# Controlling Logging Out
@app.route('/logout/')
def logout():
    flash("You Successfully Logged Out.")
    # remove the un from the session if it is there
    session.pop('user', None)
    session.pop('role', None)
    session["logged_in"] = False
    return index()


# LOGIN AS DELIVERY PERSONS
@app.route('/loginDelivery')
@required_roles('deliverer')
def view_delivery_page():
    db = db_connect()
    # change all_orders later....

    # contents of delivery info.
    delivery_info = db.select_incomplete_delivery_info()
    all_compl_delivery = db.select_completed_delivery_info()
    user_info = db.select_all_registered_users()

    print("COMPLETED")
    print(all_compl_delivery)
    print(user_info)
    return render_template("loginDELIVERY.html", all_delivery=delivery_info, all_users=user_info, all_compl_delivery=all_compl_delivery)

# For the Deliverer to Complete Delivery
@app.route('/fulfill/<order_num>')
def fulfill(order_num):
    db = db_connect()
    db.update_delivery_status(order_num)
    db.update_delivery_emp_id(session.get('user'), order_num)
    flash("**Order Fulfilled & Moved to Completed Orders**")
    return view_delivery_page()

# For the Deliverer to Issue a Warning
@app.route('/issue_warning/<order_num>')
def issue_warning(order_num):
    db = db_connect()
    db.add_cust_warning(order_num)
    print(order_num)
    #now update warnings in user table
    #get user first!
    user = db.select_user_delivery(order_num)
    print(user[0])
    db.add_warning(user[0])
    print(db.select_warnings(user[0]))
    # if user is VIP and has 2 warnings, demote status, and clear cash spent + order count
    if db.select_user_VIP_status(user[0])[0] == '1' and db.select_warnings(user[0])[0] > 1:
        db.update_VIP_status(user[0], "0")
        db.clear_warnings(user[0])
        db.reset_cash_spent(user[0])
        db.reset_order_count(user[0])
    # if regular user and has 3 warnings, deregister, and remove warnings.
    if db.select_user_VIP_status(user[0])[0] == '0' and db.select_warnings(user[0])[0] > 2:
        db.deregister(user[0])
        db.clear_warnings(user[0])
    flash("**Warning Issued**", 'error')
    return view_delivery_page()


# LOGIN AS USER
@app.route('/loginUser/')
@required_roles('user')
def view_user_page():
    db = db_connect()
    user_info = db.select_user_info(session.get("user"))[0]

    # user_top_five = db.select_top5_rated() -- wait to orders is done
    #order_status = db.select_user_order_status(session.get("user"))
    #print(order_status)
    #orders = db.select_user_orders(session.get("user"))
    #print("order1 {}".format(orders))
    orders = db.select_join_orders_status(session.get("user"))

    warnings = db.select_warnings(session.get('user'))
    print(warnings)

    #order = orders[0]#helps the indexing

    # Calculate Top 5 Dishes Ordered - CHIN
    # FOR USER, SAY YOUR TOP MOST ORDERED DISH - what if you ordered less than 5 dishes?
    top_five_all = db.select_top5_rated()

    top_five_user = top5_user(session.get("user"))
    i = 0

    while len(top_five_user) < 5:
        top_five_user.append(top_five_all[i])
        i += 1

    top_five = top_five_user
    print(top_five)
    # top 5 is most popular
    # for registered and VIP = depends on their history

    return render_template("loginUSER.html", warnings = warnings,top_five=top_five, orders=orders, user_info=user_info)  # order_status = order_status)

# LOGIN AS CHEF -- make SURE TO INCLUDE SOME SECURITY
@app.route('/loginChef')
@required_roles('chef')
def view_chef_page():
    db = db_connect()
    print(session.get('user'))
    chef_name = db.select_chef_session(session.get('user'))
    print(chef_name)
    menu = db.select_chef_menu()

    return render_template("loginCHEF.html", menu_info = menu, chef = chef_name)

#@app.route('/saveMenuChanges/<updatedmenu>')
#def SaveMenuChanges(updatedmenu):
#    db = db_connect()
#    menu = request.form["menu"]
#    return view_chef_page()

@app.route('/editMenu/<curr_item>/<curr_price>', methods=['POST'])
def editMenu(curr_item,curr_price):

    db = db_connect()

    new_item = request.form['_menu']
    new_price = request.form['price']
    print(new_item)
    print(curr_item)
    print(curr_price)

    db.update_menu_item(new_item,curr_item)
    db.update_menu_price(new_price,curr_item)

    return view_chef_page()

@app.route('/delete_menu_item/<item_name>')
def delete_menu_item(item_name):
    db = db_connect()
    print(item_name)
    db.delete_menu_item(item_name)
    return view_chef_page()

@app.route('/add_menu_item/<chef>', methods=['POST'])
def add_menu_item(chef):
    db = db_connect()

    item_name = request.form['new_item']
    item_price = request.form['new_price']
    description = request.form['description']


    chef_id = session.get('user')

    menu_id = db.select_menu_id(chef_id)
    print(chef_id)
    print(menu_id)
    #menu_id = (menu_id)
    print(item_price)
    print(item_name)

    if menu_id[0] ==None:
        menu_id = str(0)
    else:
        menu_id = str(int(menu_id[0]) + 1)

    db.insert_menu(chef_id, menu_id, item_name,item_price,"",description,"0")#zero for order_count

    return view_chef_page()

# LOGIN AS MANAGER
@app.route('/loginManager')
@required_roles('manager')
def view_management_page():
    db = db_connect()

    unregistered_users = db.select_all_unregistered_users()
    registered = db.select_all_registered_users()
    hired_employees = db.select_all_hired_employees()
    unhired_employees = db.select_all_pending_employees()
    list_of_complaints = db.select_all_pending_complaints()
    list_of_compliments = db.select_all_pending_compliments()

    # this function runs everytime manager opens his personal page
    # we use this to find out if how long its been since a chef's item has last been ordered.
    # if its been 3 or more days, we indicate that and let the manager know
    for employee in hired_employees:
        emp_id = employee[0]
        # only check the time if the employee is a chef
        if emp_id[0] == 'C':
            time_last_ordered = db.select_time_last_ordered(emp_id)[0]
            get_time_elaspsed_between_orders(time_last_ordered)

    return render_template("loginMANAGER.html", registered_users=registered, unregistered=unregistered_users,
                           hired_employees=hired_employees, unhired_employees=unhired_employees, complaints=list_of_complaints,
                           compliments=list_of_compliments)

def get_time_elaspsed_between_orders(time_last_ordered):
    current_date = datetime.today()



# Run SignUpPage
@app.route('/showSignUp/')
def showSignUp():

    return render_template('signup.html')


# Run Register
@app.route('/signup/', methods=["GET",'POST'])
def sign_up():
    db = db_connect()
    # read the values from the UI
    _firstName = request.form['first_name']
    _lastName = request.form['last_name']
    _userName = request.form['user_name']
    _password = request.form['password']
    _address = request.form['address']
    _city = request.form['city']
    _state = request.form['state']
    _postal = request.form['postal']
    _apt = request.form['apt']
    _phone = request.form['phone']

    # Check if username exists
    user_check = db.select_user_info(_userName)

    # Checks if the address is valid for geopy
    try:
        db.eval_geo_coords(_address,_city,_postal)
    except: # Note This Captures All Exceptiosn
        flash("Make Sure Your Address is Correct", "error")
        return showSignUp()


    # If the username exists
    if user_check and user_check[0][0] == _userName:
        flash("Sorry, Username Exists", 'error')
        return showSignUp()
    # If the key fields are not entered
    elif not _firstName or not _lastName or not _userName or not _password or not _address or not _city or not _state:
       flash("Please Enter All Info with Asterisks")
       return showSignUp()
    # Insert User
    else:
        db.insert_users(_userName, _firstName, _lastName, _password, _address, _city, _state, _postal, _apt, _phone, acc_funds=0)
        flash("Your Account is Now Pending Manager Approval.")
        flash("Please send a $100 check to us so we can approve.")
        return index()


###### DISPLAY COMPLIMENT/COMPLAINT FORM ##############

@app.route('/show_complaint_form/')
def show_complaint_form():
    db = db_connect()
    hired_employees = db.select_all_hired_employees()
    return render_template("/complaints.html", employees=hired_employees)

@app.route('/submit_complaint', methods=["GET",'POST'])
def submit_complaint():
    db = db_connect()

    # insert_complaints function needs emp_id not name so we convert it here
    employee = request.form.get("employee")
    employee = employee.strip().split(" ")
    emp_fname = str(employee[0])
    if len(employee) > 1:
        emp_lname = employee[1]

    user = session.get("user")
    complaint = request.form.get("complaint")


    try:
        emp_id = db.select_employee_id_from_name(emp_fname, emp_lname)[0]
        db.insert_complaints(user, emp_id, complaint)
    except:
        print("failed")
        flash("Submission failed")
        return render_template("complaints.html", employees=db.select_all_hired_employees())

    return redirect("/")

@app.route('/show_compliment_form')
def show_compliment_form():
    db = db_connect()
    print(session.get("user"))
    return render_template("compliments.html", employees=db.select_all_hired_employees())


@app.route('/submit_compliment', methods=["GET",'POST'])
def submit_compliment():
    db = db_connect()
    # convert employee name to emp_id which is nec for insert function
    employee = request.form.get("employee")
    employee = employee.strip().split(" ")
    print(employee)
    emp_fname = str(employee[0])
    if len(employee) > 1:
        emp_lname = employee[1]


    user = session.get("user")
    compliment = request.form.get("compliment")

    try:
        emp_id = db.select_employee_id_from_name(emp_fname, emp_lname)[0]

        db.insert_compliments(user, emp_id, compliment)
    except:
        print("failed")
        flash("Submission failed")
        return render_template("compliments.html", employees=db.select_all_hired_employees())

    return redirect("/")


######### MENU SECTION ###########

# Run MenuPage
@app.route('/menu', methods=["GET",'POST'])
def showMenu():
    db = db_connect()

    try:
        items_in_cart = db.select_user_cart(session.get("user"))
    except:
        items_in_cart = []
    total_price = 0
    for item in items_in_cart:
        item_price = db.select_menu_price(item[1],item[2])
        # total price so far = price * quantity
        total_price += item_price[0] * item[4]
    return render_template('Menu.html',databaseitems = db.select_menu_items(),item_description = db.select_menu_items_description(), numbers=db.select_menu_rating_numbers(),
                           menu_items=db.select_menu(), cart=items_in_cart, sum_of_items=total_price, user_id=session.get("user")) #Lenny added the item_description stuff here, I may be doing this wrong#

@app.route('/add_to_cart', methods=["GET",'POST'])
def add_to_cart():
    db = db_connect()
    # taken from menu form
    list_of_quantities = request.form.getlist("quantity")

    menu_items = db.select_menu()
    # loop through quantity list and list of menu items simultaneously
    # the index value value should match up, so the first quantity should be referring to
    # the first quantity in list of menu

    for count,menu_item in zip(list_of_quantities,menu_items):
        # if the quantity from the menu form is not empty we convert it to an integer and
        # insert it into the cart
        if count != '':

            quantity = int(count)
            try:
                db.insert_cart_items(session.get("user"), menu_item[0], menu_item[2], menu_item[3], quantity)
            except:
                flash("You need to login to do that")
                return showLogIn()

    return showMenu()

@app.route('/empty_cart', methods=["GET",'POST'])
def empty_cart():
    db = db_connect()
    user = session.get("user")

    try:
        db.empty_cart(user)
    except:
        flash("you need to login")
        return showLogIn()

    return showMenu()

# Given String from Orders Database, Retrieve list of menu_item and qty
# Precondition: s is a string
# Postcondition: returns a, a list of menu_item and quantity where quantity is
# following odd index
def strip_orders(s):

    item_name = s.lstrip('[')
    item_name = item_name.rstrip(']')
    item_name = item_name.replace('\'', '')

    a = item_name.split(', ')
    num_items = int(len(a)/2)

    b = [[] * x for x in range(num_items)]

    for i in range(len(a)):
        if i % 2 == 0:

            b[int(i/2)].append(a[i].lstrip('('))
        else:
            b[int((i-1) / 2)].append(a[i].rstrip(')'))

    return b


# Returns a 2D list with the total number of items the user bought of each
# Precondition: user id
def top5_user(user):
    db = db_connect()
    user_orders = db.select_user_orders(user)

    top5 = []

    for x in range(len(user_orders)): # for every order
        a = strip_orders(user_orders[x][2]) # get the string array
        print("A")
        print(a)
        for y in range(len(a)):  # for every item in the string array
            if any(a[y][0] in c for c in top5):
                top5[next((i for i, sublist in enumerate(top5) if a[y][0] in sublist), -1)][2] += int(a[y][1])
            else:  # int a
                top5.append([a[y][0], db.select_menu_pic(a[y][0])[0], int(a[y][1])])

    top5 = sorted(top5, key=lambda z: z[2], reverse=True)

    return top5

@app.route('/checkout/<price>/<order_items>', methods=["GET",'POST'])
@required_roles('user')
def checkout(price, order_items):
    db = db_connect()

    items = strip_orders(order_items)
    print(type(order_items))
    print(order_items)


    user = session.get("user")
    is_user_VIP = db.select_user_VIP_status(user)

    list_of_order_items = ast.literal_eval(order_items)

    # update the time someone ordered from this chef
    for order_item in list_of_order_items:
        emp_id = order_items[1][0]
        # print(order_item)
        db.update_employee_last_ordered(emp_id)


    cart = db.select_user_cart(user)
    # print(cart)
    items = []
    # print(len(cart))
    # print(len(order_items))

    for x in range(len(cart)):
        items.append((cart[x][3],cart[x][4]))


    # print(is_user_VIP)

    if is_user_VIP == 1:
        price = float(price) * .9

    items = str(items)

    print("ITEMS")


    # Get User Information - CHIN
    user_info = db.select_user_info(user)[0]

    # Check if there is enough money in the account - CHIN
    # Not enough money - CHIN
    if int(price) > int(user_info[13]):
        flash("You Do Not Have Enough Money In Your Account")
        return relogin()




    db.insert_orders(user,items,price)
    db.update_user_order_count(user)
    db.update_user_cash_spent(user, price)
    db.empty_cart(user)


    order_count = db.select_user_order_count(user)
    cash_spent_so_far = db.select_user_cash_spent(user)


        # Increase Dish Order Count - CHIN
    for num in range(len(cart)):
        db.inc_ord_count(cart[num][4],cart[num][3])

            # VIP check: if this last checkout allowed customer to become VIP
    if int(order_count[0]) >= 50 or float(cash_spent_so_far[0]) >= 500:
        db.set_user_VIP_status(user)
    db.subtract_acc_funds(price, user)

    db.insert_deliveryinfo(len(db.select_orders()), 'None', session.get("user"), status="0", cust_warning="0")

    #update order_count and update VIP status if neccessary
    db.update_order_count(user)
    if db.select_order_count(user)[0] == '50' or  db.select_cash_spent(user)[0] > '500':
        db.update_VIP_status(user,"0")



        # Update Funds in the Account
    #except:
     #   flash("You need to login to do that")
      #  return showLogIn()

    # db.insert_orders(user,items,price)
    # db.empty_cart(session.get("user"))

    # insert item into the deliveryinfo DB


    return render_template("Order Confirmation.html", order=order_items, total_price=price)

@app.route('/show_ratings', methods=["GET",'POST'])
def show_ratings():
    db = db_connect()

    return render_template("ratings.html", databaseitems = db.select_menu_items(),numbers=db.select_menu_rating_numbers(),
                           menu_items=db.select_menu())

@app.route('/submit_rating', methods=["GET",'POST'])
def submit_rating():
    db = db_connect()
    rating = request.form["rating"]

    chef_id = request.values["chef_id"]
    menu_id = request.values["menu_id"]

    if rating != '':
        db.insert_ratings(chef_id,menu_id,rating)

        average_rating = db.select_menu_rating(chef_id, menu_id)[0]
        number_of_ratings = db.select_menu_rating_quantity(chef_id, menu_id)[0]

        # if the chef has consistently low ratings, we demote them. Below are the conditions
        # to check if the ratings are "consistently low"
        if float(rating) <= 2 and float(average_rating) <= 1.5 and float(number_of_ratings) > 15:
            try:
              db.demote_employee(chef_id)

              # if the employee has been demoted twice, fire him
              print(db.check_demotions())[0]
              if db.check_demotions(chef_id)[0] >= 2:
                  db.fire_employee(chef_id)
            except:
                flash("that chef no longer works here")
                redirect("/")
    else:
        flash("enter a number")

    return show_ratings()

@app.route('/delivery_rating/<order_id>',methods=["GET","POST"])
def delivery_rating(order_id):
    #print("hello")
    print(order_id)
    order_id = order_id[0]#for some reason order_id returns a number followed by a " e.g 1"
    db = db_connect()
    status = db.select_order_status(order_id)

    print(status[0])

    if int(status[0]) == 0:
        flash("Your order has not been delivered yet!")

    else:
        rating = request.form["delivery_rating"]
        db.update_delivery_rating(order_id,rating)
        flash("Thank you for rating!")
    return view_user_page()




# EMPLOYEE MANAGEMENT TOOLS
@app.route('/accept_user/<user>', methods=['GET'])
def accept_user(user):
    db = db_connect()
    db.register(user)
    db.insert_funds(user,100)

    return view_management_page()

@app.route('/decline_user/<user>', methods=['GET'])
def decline_user(user):
    db = db_connect()
    db.delete_account(user)
    return view_management_page()


# DEPOSIT MONEY - CHIN
@app.route('/deposit_money/', methods=["POST"])
def deposit_money():
    db = db_connect()
    amount = request.form["money"]
    print(amount)

    db.inc_acc_funds(amount, session.get('user'))
    flash("Funds Deposited: $"+amount)
    return view_user_page()

@app.route('/hire_employee/<empl_name>', methods=['GET'])
def hire(empl_name):
    db = db_connect()
    db.hire_employee(empl_name)
    return view_management_page()

@app.route('/fire/<empl_name>', methods=['GET'])
def fire(empl_name):
    db = db_connect()
    db.fire_employee(empl_name)
    return view_management_page()

@app.route('/upgrade_user/<user_id>', methods=['GET'])
def upgrade(user_id):
    db = db_connect()
    db.update_VIP_status(user_id, "1")
    return view_management_page()

@app.route('/downgrade_user/<user_id>', methods=['GET'])
def downgrade(user_id):
    db = db_connect()
    db.update_VIP_status(user_id, "0")
    return view_management_page()

@app.route('/deregister_user/<user_id>', methods=['GET'])
def deregister(user_id):
    db = db_connect()
    db.deregister(user_id)
    return view_management_page()

@app.route('/promote/<empl_name>', methods=['GET'])
def promote(empl_name):
    db = db_connect()
    db.promote_employee(empl_name)
    return view_management_page()

@app.route('/demote/<empl_name>', methods=['GET'])
def demote(empl_name):
    #empl_is actually emp_id!
    db = db_connect()
    db.add_demotions(empl_name)


    print(db.check_demotions(empl_name)[0])
    try:
        if db.check_demotions(empl_name)[0] > 1:
            db.fire_employee(empl_name)
    except:
        return view_management_page()
    return view_management_page()

@app.route('/add_warning/<user>', methods=['GET'])
def add_warning(user_id):
    db = db_connect()
    db.update_warnings(user_id)
    return view_management_page()

@app.route('/accept_complaint/<complaint_id>/<emp_id>', methods=['GET'])
def accept_complaint(complaint_id, emp_id):
    db = db_connect()
    db.confirm_complaint(complaint_id)
    db.add_complaint(emp_id)

    employee = emp_id

    # check how many complaints there are against this employee
    # if 3 or greater, demote the employee
    if db.check_complaints(employee)[0] > 2:
        db.demote_employee(employee)

    # if the employee has been demoted twice, fire him
        if int(db.check_demotions(employee)[0]) >= 2:
            db.fire_employee(employee)

    return view_management_page()

@app.route('/decline_complaint/<complaint_id>/<user_id>', methods=['GET'])
def decline_complaint(complaint_id,user_id):
    db = db_connect()
    print(complaint_id)
    user = db.select_userid_complaints(complaint_id)
    print(user)
    db.add_warning(user[0])
    db.delete_complaint(complaint_id)

    #print(db.select_warnings(user[0]))
    #if user is VIP and has 2 warnings, demote status, and clear cash spent + order count
    if db.select_user_VIP_status(user[0])[0] == '1' and db.select_warnings(user[0])[0] >1:
        db.update_VIP_status(user[0],"0")
        db.clear_warnings(user[0])
        db.reset_cash_spent(user[0])
        db.reset_order_count(user[0])
    #if regular user and has 3 warnings, deregister, and remove warnings.
    if db.select_user_VIP_status(user[0])[0] == '0' and db.select_warnings(user[0])[0] >2:
        db.deregister(user[0])
        db.clear_warnings(user[0])


    return view_management_page()

@app.route('/add_compliment/<compliment_id>/<emp_id>', methods=['GET'])
def accept_compliment(compliment_id, emp_id):
    db = db_connect()
    db.confirm_compliment(compliment_id)

    employee = emp_id

    db.increment_compliment_count(emp_id)
    #if int(db.select_employee_info(emp_id)[17]) > 0:
     #   db.decrease_complaint(emp_id)

    # if a customer is customer is VIP, their compliments count twice as much
    is_user_VIP = db.select_user_VIP_status(session.get("user"))
    if is_user_VIP == 1:
        db.increment_compliment_count(emp_id)

    print(db.check_compliments(employee))
    if int(db.check_compliments(employee)[0]) > 2:
        db.promote_employee(employee)
        if int(db.check_complaints(emp_id)[0]) > 0:
            db.decrement_complaint(employee)
        db.reset_compliments(emp_id)#reset compliments once promoted


    return view_management_page()

@app.route('/decline_compliment/<compliment_id>/<user_id>', methods=['GET'])
def decline_compliment(compliment_id,user_id):
    db = db_connect()
    db.delete_compliment(compliment_id)

    return view_management_page()

@app.route('/delete_account')
def delete_account():
    db = db_connect()
    user = session.get('user')
    db.delete_account(user)

    return render_template('index.html')


# Handles Any Page That Doesn't Exist
@app.errorhandler(404)
def PageNotFound(error):
    return render_template('errors/404.html'), 404


