import sqlite3 as sql
from datetime import datetime, date
from geopy import Nominatim


# import certifi


class db_connect:
    def __init__(self):
        #establish connection.
        with sql.connect("losquatroamigos.db")as self.con:
            self.cur = self.con.cursor()


    ###################INSERT INTO DATABASE###################################
    ##########################################################################
    def insert_restaurant(self,res_id,name, address, city, state, postal, phone):
        self.cur.execute("INSERT INTO restaurant (res_id,name,address, city, state, postal, phone) VALUES(?,?,?,?,?,?,?)",
                     (res_id, name,address,phone,postal) )
        self.con.commit()

    def insert_employees(self,emp_id,emp_fname, emp_lname, address, city, state, postal, apt, phone, ssn, birthdate,salary,date_hired, hired=0):
        today = datetime.today()
        self.cur.execute("INSERT INTO employees (emp_id,emp_fname,emp_lname,address,city, state, postal, apt, phone, ssn, birthdate, salary, date_hired, hired, last_ordered) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (emp_id, emp_fname, emp_lname, address, city, state, postal, apt, phone, ssn, birthdate, salary, date_hired,hired, today) )
        self.con.commit()

    def insert_users(self,user_id,f_name, l_name, password, address, city, state, postal, apt, phone, acc_funds=100,registered=0,VIP=0,order_count=0,cash_spent=0):
        memb_since = datetime.now()
        self.cur.execute("INSERT INTO users (user_id,f_name, l_name,password,address, city,state,postal,apt,phone,memb_since,acc_funds,registered,VIP,order_count,cash_spent) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (user_id, f_name, l_name, password, address, city, state, postal, apt, phone, memb_since, acc_funds,registered,VIP,order_count,cash_spent))
        self.con.commit()


        #Store longitude and latitude for google API
        coords = db_connect.eval_geo_coords(self,address,city,postal)


        #update longitude and latitude
        self.cur.execute("UPDATE users SET longitude = '{0}' WHERE user_id = '{1}'".format(coords[0],user_id))
        self.cur.execute("UPDATE users SET latitude = '{0}' WHERE user_id = '{1}'".format(coords[1],user_id))
        self.con.commit()

    #get geo coordinates
    def eval_geo_coords(self,address,city,postal):
        nom = Nominatim()
        n = nom.geocode("{},{},{}".format(address,city,postal))
        return n.longitude, n.latitude


    #INSERT MORE MONEY INTO ACCOUNT
    def insert_funds(self,user_id,new_funds):
        self.cur = self.con.cursor()
        self.cur.execute("UPDATE users set acc_funds = acc_funds + '{}' WHERE user_id = '{}'".format(new_funds,user_id))
        self.con.commit()

    def insert_ratings(self, chef_id, menu_id, rating):
        self.cur = self.con.cursor()
        # number of times menu item rated so far
        rating_quantity = db_connect.select_menu_rating_quantity(self, chef_id, menu_id)
        old_rating = db_connect.select_menu_rating(self, chef_id, menu_id)
        if not rating_quantity[0] or not old_rating[0]:
            rating_quantity = 0
            old_rating = 0
        else:
            rating_quantity = round(float(rating_quantity[0]), 2)
            old_rating = round(float(old_rating[0]), 2)
        rating = round(float(rating), 2)

        #math function to find the new average rating based on a new rating
        new_rating = ((rating_quantity*old_rating) + rating) / (rating_quantity+1)

        self.cur.execute("UPDATE menus SET rating = '{0}' WHERE chef_id='{1}' and menu_id='{2}'".format( new_rating, chef_id,menu_id))
        self.cur.execute(
            "UPDATE menus SET rating_quantity = {} + 1 WHERE chef_id='{}' and menu_id='{}'".format(rating_quantity, chef_id, menu_id))
        self.con.commit()



    def insert_complaints(self,user_id, emp_id, complaint, approved=0):
        self.cur = self.con.cursor()
        self.cur.execute("INSERT INTO complaints (user_id, emp_id, complaint, approval) VALUES(?,?,?,?)", (user_id, emp_id, complaint, approved) )
        self.con.commit()

    def insert_compliments(self,user_id, emp_id, compliment, approved=0):
        date = datetime.now()
        self.cur = self.con.cursor()
        self.cur.execute("INSERT INTO compliments (user_id, emp_id, compliment, approval) VALUES(?,?,?,?)", (user_id, emp_id, compliment, approved) )
        self.con.commit()

    def increment_compliment_count(self,emp_id):
        self.cur.execute("UPDATE employees SET compliments = compliments + 1 where emp_id = '{}'".format(emp_id))
        self.con.commit()

    def reset_compliments(self,emp_id):
        self.cur.execute("UPDATE employees SET compliments = 0 WHERE emp_id = '{}'".format(emp_id))
        self.con.commit()


    def insert_orders(self,user_id,menu_item,total_price):
        self.cur = self.con.cursor()
        self.cur.execute("INSERT INTO orders (user_id,menu_item,total_price) VALUES(?,?,?)",
                    (user_id,menu_item,total_price))
        self.con.commit()

    def insert_chefs(self,chef_id,emp_id,menu_name,chef_rating):
        self.cur = self.con.cursor()
        self.cur.execute("INSERT INTO chefs(chef_id, emp_id,menu_name, chef_rating) VALUES (?,?,?,?)", (chef_id,emp_id, menu_name, chef_rating) )
        self.con.commit()

    def insert_deliveryinfo(self,order_id,emp_id, user_id, status, cust_warning):
        self.cur = self.con.cursor()
        self.cur.execute("INSERT INTO deliveryinfo (order_id,emp_id, user_id, status, cust_warning) VALUES (?,?,?,?,?)",
                        (order_id,emp_id, user_id, status, cust_warning) )
        self.con.commit()

    def insert_menu(self,chef_id, menu_id, item_name, price, rating,description,order_count):
        self.cur = self.con.cursor()
        self.cur.execute("INSERT INTO menus (chef_id, menu_id, item_name, price, rating,item_description,order_count) "
                         "VALUES (?,?,?,?,?,?,?)",
                        (chef_id, menu_id, item_name, price, rating,description,order_count))
        self.con.commit()

    ################## END OF INSERT INTO DATABASE ###################################
    ##################################################################################

    ################## SELECT FROM DATABASE###########################################


    ################## EMPLOYEE SELECT FUNCTIONS######################################

    #GENERAL EMPLOYEE INFO
    def select_employee_info(self,emp_id):
        result = self.cur.execute("SELECT * FROM Employees where emp_id = '%s';" % emp_id).fetchone()
        return result

    def select_employee_id_from_name(self,f_name, l_name):
        result = self.cur.execute(("SELECT * FROM Employees where emp_fname = '{0}' AND emp_lname = '{1}';").format(str(f_name), l_name)).fetchone()
        return result

    def select_all_hired_employees(self):
        result = self.cur.execute("SELECT * FROM employees WHERE hired = 1").fetchall()
        return result

    def select_all_pending_employees(self):
        result = self.cur.execute("SELECT * FROM employees WHERE hired = 0").fetchall()
        return result

    def select_time_last_ordered(self, emp_id):
        result = self.cur.execute("SELECT last_ordered FROM employees WHERE emp_id = '{}'".format(emp_id)).fetchone()
        return result

    def update_employee_last_ordered(self, emp_id):
        today = datetime.today()
        print("emp")
        print(emp_id)
        self.cur.execute("UPDATE employees SET last_ordered = '{}' WHERE emp_id='{}'".format(today,emp_id))
        self.con.commit()

    ################# USER SELECT FUNCTIONS#########################################
    #SELECT ALL UNREGISTERED USERS
    def select_all_unregistered_users(self):
        result = self.cur.execute("SELECT * FROM users WHERE registered = 0").fetchall()
        return result

    def select_all_registered_users(self):
        result = self.cur.execute("SELECT * FROM users Where registered = 1").fetchall()
        return result

    def is_registered(self,user_id):
        result = self.cur.execute("SELECT registered FROM users Where user_id='{}'".format(user_id)).fetchone()
        return result

        # GENERAL USER INFO
    def select_user_info(self,user_id):
        result = self.cur.execute("SELECT * FROM users WHERE user_id = '%s'" %user_id).fetchall()
        return result


        # USERS CAN DELETE THEIR ACCOUNT IF THEY WISH TO DO SO. (MANAGERS MAY ALSO USE THIS TO REMOVE USER FROM WEBSITE)
    def delete_account(self,user_id):
        print("deleting " + user_id)
        self.cur.execute("DELETE FROM users WHERE user_id = '%s'" % user_id)
        self.con.commit()

        # TOP FIVE RATED FOODS OF USER
    def select_top_user_rated(self, user_id):
        result = self.cur.execute("SELECT item_name, item_pic, rating FROM menus WHERE user_id = '{}' ORDER BY rating DESC LIMIT 5".format(user_id)).fetchall()
        return result

        # VISITORS TOP 5 RATED FOOD (GET THIS FROM ALL RATED FOOD) - CHIN
    def select_top5_rated(self):
        result = self.cur.execute("SELECT item_name, item_pic, rating FROM menus ORDER BY order_count DESC LIMIT 5 ").fetchall()
        return result

    def select_user_cart(self, user_id):
        result = self.cur.execute("SELECT * FROM cart where user_id='{}'".format(user_id)).fetchall()
        return result

############### END OF USER SELECT FUNCTIONS#######################################
###################################################################################
                          ####MENU SELECT FUNCTIONS##############

      # LENNY WROTE SELECT_ITEMS_DESCRIPTION -- IF ITS WRONG MY BAD -- #
    def select_menu_items_description(self):
        result = self.cur.execute("SELECT item_description FROM menus").fetchall()
        return result

    def select_menu_items(self):
        result = self.cur.execute("SELECT item_name FROM menus").fetchall()
        return result

    # Return Picture, by name - CHIN
    def select_menu_pic(self,item_name):
        result = self.cur.execute("SELECT item_pic FROM menus WHERE item_name = '{}'".format(item_name)).fetchone()
        result = self.cur.execute("SELECT item_pic FROM menus WHERE item_name = '{}'".format(item_name)).fetchone()
        return result

    def select_menu_price(self, chef_id, menu_id):
        result = self.cur.execute("SELECT price FROM menus WHERE chef_id='{0}' and menu_id='{1}'".format(chef_id, menu_id)).fetchone()
        return result

    def select_menu_rating_quantity(self, chef_id, menu_id):
        result = self.cur.execute("SELECT rating_quantity FROM menus WHERE chef_id='{0}' and menu_id='{1}'".format(chef_id, menu_id)).fetchone()
        return result

    def select_menu_rating(self, chef_id, menu_id):
        result = self.cur.execute(
            "SELECT rating FROM menus WHERE chef_id='{0}' and menu_id='{1}'".format(chef_id,
                                                                                             menu_id)).fetchone()
        return result

    def select_menu_rating_numbers(self):
        result = self.cur.execute("SELECT rating FROM menus").fetchone()
        return result


    def select_menu(self):
        result = self.cur.execute("Select * from menus").fetchall()
        return result


    def select_item_in_user_cart(self, user_id, chef_id, menu_id):
        result = self.cur.execute("SELECT menu_id from cart where user_id='{0}' and chef_id='{1}' and menu_id='{2}'".format(user_id,chef_id,menu_id)).fetchone()
        return result

####CART FUNCTIONS##############
    def select_menu_id(self,chef_id,):
        result = self.cur.execute("SELECT max(menu_id) FROM menus WHERE chef_id = '{}'".format(chef_id)).fetchone()
        return result

    def select_chef_id(self,chef_name):
        result = self.cur.execute("SELECT emp_id FROM chefs where ")

####UPDATE ACCT FUNDS############## - CHIN
    def subtract_acc_funds(self, amt, user_id):
        self.cur.execute("UPDATE users SET acc_funds = acc_funds-'{}' WHERE user_id = '{}'".format(amt, user_id))
        self.con.commit()

    def inc_acc_funds(self,amt,user_id):
        self.cur.execute("UPDATE users SET acc_funds = acc_funds+'{}' WHERE user_id = '{}'".format(amt, user_id))
        self.con.commit()

####UPDATE ORDER COUNT############## - CHIN
    def inc_ord_count(self, amt, item_name):
        self.cur.execute("UPDATE menus SET order_count = order_count+'{}' WHERE item_name = '{}'".format(amt, item_name))
        self.con.commit()

####CART INSERT FUNCTIONS##############
    def insert_cart_items(self, user_id, chef_id, menu_id, item_name, quantity):
        is_in_cart = db_connect.select_item_in_user_cart(self, user_id, chef_id, menu_id)
        if is_in_cart:
            self.cur.execute("UPDATE cart SET qty = qty + '{0}' WHERE user_id ='{1}' and chef_id='{2}' and menu_id='{3}'"
                                  .format(quantity,user_id,chef_id,menu_id))
        else:
            self.cur.execute("INSERT INTO cart (user_id,chef_id, menu_id, item_name, qty) VALUES(?,?,?,?,?)",
                         (user_id, chef_id, menu_id, item_name, quantity))
        self.con.commit()

    def empty_cart(self, user_id):
        self.cur.execute("DELETE FROM cart WHERE user_id = '{}'".format(user_id))
        self.con.commit()

##############END OF CART INSERT##################

    ###ORDER SELECT FUNCTIONS####
    def select_orders(self):
        result = self.cur.execute("SELECT * FROM orders").fetchall()
        return result

    def select_user_orders(self,user_id):
        result = self.cur.execute("SELECT * FROM orders WHERE user_id='{}'".format(user_id)).fetchall()
        return result

    def select_join_orders_status(self,user_id):
        result = self.cur.execute("SELECT orders.*, deliveryinfo.status FROM orders INNER JOIN "
                                  "deliveryinfo ON orders.order_id = deliveryinfo.order_id WHERE deliveryinfo.user_id ='{}'".format(user_id)).fetchall()
        return result

    def delete_order(self,order_id):
        self.cur.execute("DELETE FROM orders WHERE order_id = '{}'".format(order_id))
        self.con.commit()

    def select_order_items(self,user_id):
        result = self.cur.execute("SELECT menu_item FROM orders WHERE user_id ='{}'".format(user_id)).fetchall()
        return result

    def select_order_status(self,order_id):
        result = self.cur.execute("SELECT status FROM deliveryinfo WHERE order_id = '{}'".format(order_id)).fetchone()
        return result

    def select_user_order_status(self,user_id):
        result = self.cur.execute("SELECT status FROM deliveryinfo WHERE user_id = '{}'".format(user_id)).fetchall()
        return result

    def update_order_count(self,user_id):
        self.cur.execute("UPDATE users SET order_count = order_count +1 WHERE user_id = '{}'".format(user_id))
        self.con.commit()

    def select_order_count(self,user_id):
        result = self.cur.execute("SELECT order_count FROM users WHERE user_id = '{}'".format(user_id)).fetchone()
        return result

    def select_cash_spent(self,user_id):
        result = self.cur.execute("SELECT cash_spent FROM users WHERE user_id = '{}'".format(user_id)).fetchone()
        return result

    def reset_cash_spent(self,user_id):
        self.cur.execute("UPDATE users SET cash_spent = 0 WHERE user_id = '{}'".format(user_id))
        self.con.commit()

    def reset_order_count(self,user_id):
        self.cur.execute("UPDATE users SET order_count = 0 WHERE user_id = '{}'".format(user_id))
        self.con.commit()

    ######### END OF ORDER SELECT FUNCTIONS ############

    ###CHEF SELECTORS###

    #GET chef name##
    def select_chef_name(self):
        result = self.cur.execute("SELECT emp_fname FROM employees where substr(emp_id,1,1) = 'C' ").fetchall()
        return result

    def select_chef_session(self,chef_id):
        result = self.cur.execute("SELECT emp_fname FROM employees WHERE emp_id = '{}'".format(chef_id)).fetchone()
        return result

    def select_chef_menu(self):
        result = self.cur.execute("SELECT item_name, price, rating FROM menus ").fetchall()
        return result

    def update_menu_item(self,new_name,curr_item_name):
        self.cur.execute("UPDATE menus SET item_name = '{}' where item_name = '{}'".format(new_name,curr_item_name))
        self.con.commit()

    def update_menu_price(self,new_price,curr_item):
        self.cur.execute("UPDATE menus SET price = '{}' WHERE item_name = '{}'".format(new_price,curr_item))
        self.con.commit()


    def delete_menu_item(self,item_name):
        self.cur.execute("DELETE FROM menus WHERE item_name = '{}'".format(item_name))
        self.con.commit()

        ###VIP SELECTORS###
    def select_user_VIP_status(self,user_id):
        result = self.cur.execute("SELECT VIP FROM users WHERE user_id = '{}'".format(user_id)).fetchone()
        return result

    def update_VIP_status(self,user,status):
        self.cur.execute("UPDATE users SET VIP ='{}' WHERE user_id = '{}'".format(status,user))
        self.con.commit()

    def set_user_VIP_status(self,user_id):
        self.cur.execute("UPDATE users SET VIP = 1 WHERE user_id ='{}'".format(user_id))
        self.con.commit()

    def select_user_order_count(self,user_id):
        result = self.cur.execute("SELECT order_count FROM users WHERE user_id = '{}'".format(user_id)).fetchone()
        return result

    def select_user_cash_spent(self,user_id):
        result = self.cur.execute("SELECT cash_spent FROM users WHERE user_id = '{}'".format(user_id)).fetchone()
        return result

    def update_user_cash_spent(self, user_id, price):
        self.cur.execute("UPDATE users SET cash_spent = cash_spent + {} WHERE user_id ='{}'".format(price, user_id))
        self.con.commit()

    def update_user_order_count(self, user_id):
        self.cur.execute("UPDATE users SET order_count = order_count + 1 WHERE user_id ='{}'".format(user_id))
        self.con.commit()


########## MANAGEMENT FUNCTIONS ##########################

        #COMPLAINTS - Will be neccessary for managers to review
    def select_complaints(self,user_id):
        result = self.cur.execute("SELECT complaint, date_posted FROM complaints WHERE user_id = '%s'" %user_id).fetchall()
        return result

    def select_all_pending_complaints(self):
        result = self.cur.execute("SELECT * FROM complaints WHERE approval=0").fetchall()
        return result

    def select_all_pending_compliments(self):
        result = self.cur.execute("SELECT * FROM compliments WHERE approval=0").fetchall()
        return result

    def select_userid_complaints(self,complaint_id):
        result = self.cur.execute("SELECT user_id FROM complaints WHERE complaint_id ='{}'".format(complaint_id)).fetchone()
        return result

        #COMPLIMENTS -Will be neccessary for managers to review
    def select_compliments(self,compliment_id):
        result = self.cur.execute("SELECT compliment, date_posted FROM compliments WHERE compliment_id = '%s'" %compliment_id).fetchall()
        return result

    def delete_complaint(self, complaint_id):
        self.cur.execute("DELETE FROM complaints WHERE complaint_id = '%s'" % complaint_id)
        self.con.commit()

    def decrement_complaint(self,emp_id):
        self.cur.execute("UPDATE employees SET complaints = complaints -1 WHERE emp_id = '{}'".format(emp_id))
        self.con.commit()

        #Accept Registration
    def register(self,user_id):
        self.cur.execute("UPDATE users SET registered=1 WHERE user_id = '%s'" %user_id)
        self.con.commit()

    def deregister(self,user_id):
        self.cur.execute("UPDATE users SET registered=0 WHERE user_id = '{}'".format(user_id))
        self.con.commit()

        #hire employee
    def hire_employee(self,emp_id):
        self.cur.execute("UPDATE employees SET hired = 1 where emp_id ='%s'" %emp_id)
        self.con.commit()

    def add_demotions(self,emp_id):
        self.cur.execute("UPDATE employees SET demotions = demotions + 1 WHERE emp_id = '%s'" %emp_id)
        self.con.commit()

    def decrease_complaint(self,emp_id):
        self.cur.execute("UPDATE employees SET complaints = complaints -1 WHERE emp_id = '{}'".format(emp_id))
        self.con.commit()

    def select_demotions(self,emp_id):
        result = self.cur.execute("SELECT demotions FROM employees WHERE emp_id = '{}'".format(emp_id)).fetchone()
        return result


    def decrease_demotions(self,emp_id):
        self.cur.execute("UPDATE employees SET demotions = demotions - 1 WHERE emp_id = '%s'" %emp_id)
        self.con.commit()

    def check_demotions(self,emp_id):
        result = self.cur.execute("SELECT demotions FROM employees WHERE emp_id = '%s'" %emp_id).fetchone()
        return result

    def fire_employee(self,emp_id):
        self.cur.execute("DELETE FROM employees WHERE emp_id = '%s'" %emp_id)
        self.con.commit()

        #Promoting employee increases their salary by 5 dollars.
    def check_compliments(self,emp_id):
        result = self.cur.execute("SELECT compliments FROM employees WHERE emp_id = '%s'" %emp_id).fetchone()
        return result


    def promote_employee(self,emp_id):
        self.cur.execute("UPDATE employees SET salary = salary + 5 where emp_id = '%s'" % emp_id)
        self.con.commit()

        #demoting employee
    def check_complaints(self,emp_id):
        result = self.cur.execute("SELECT complaints FROM employees WHERE emp_id = '{}'".format(emp_id)).fetchone()
        return result

    def demote_employee(self,emp_id):
        self.cur.execute("UPDATE employees SET salary = salary - 5 WHERE emp_id = '%s'" %emp_id)
        self.cur.execute("UPDATE employees SET demotions = demotions +1 WHERE emp_id = '%s'" % emp_id)
        self.con.commit()

    def confirm_complaint(self,complaint_id):
        self.cur.execute("UPDATE complaints SET approval = 1 where complaint_id = '%s'" %complaint_id)
        self.con.commit()

    def add_complaint(self,emp_id):
        self.cur.execute("UPDATE employees SET complaints = complaints +1 WHERE emp_id = '{}'".format(emp_id))
        self.con.commit()

    def confirm_compliment(self,compliment_id):
        self.cur.execute("UPDATE compliments SET approval = 1 where compliment_id = '%s'" % compliment_id)
        self.con.commit()



#update warnings in users table. Do this by counting the number of true boolean values a user has in the warnings column
# of delivery info table.
    #def update_warnings(self,user_id):
    #    self.cur.execute("UPDATE users set warnings = (SELECT count(cust_warning) FROM deliveryinfo where user_id = '%s')"
    #                %user_id)
    #    self.con.commit()

    def add_warning(self,user_id):
        self.cur.execute("UPDATE users SET warnings = warnings+1 WHERE user_id = '{}'".format(user_id))
        self.con.commit()

    def select_warnings(self,user_id):
        result = self.cur.execute("SELECT warnings FROM users WHERE user_id = '{}'".format(user_id)).fetchone()
        return result

    #get user_id from order_id in deliveryinfo
    def select_user_delivery(self,order_id):
        result = self.cur.execute("SELECT user_id FROM deliveryinfo WHERE order_id ='{}'".format(order_id)).fetchone()
        return result

    def clear_warnings(self,user_id):
        self.cur.execute("UPDATE users SET warnings = 0 WHERE user_id = '{}'".format(user_id))
        self.con.commit()

    def select_completed_delivery_info(self):
        result = self.cur.execute("SELECT * FROM deliveryinfo WHERE status = 1").fetchall()
        return result

    def select_incomplete_delivery_info(self):
        result = self.cur.execute("SELECT * FROM deliveryinfo WHERE status = 0").fetchall()
        return result

    def select_delivery_info(self):
        result = self.cur.execute("SELECT * FROM deliveryinfo").fetchall()
        return result

    def update_delivery_status(self, order_id):
        self.cur.execute("UPDATE deliveryinfo SET status = 1 WHERE order_id = '{}'".format(order_id))
        self.con.commit()

    def update_delivery_emp_id(self, empl_id, order_id):
        self.cur.execute("UPDATE deliveryinfo SET emp_id = '{}' WHERE order_id='{}'".format(empl_id, order_id))
        self.con.commit()

    def add_cust_warning(self,order_id):
        self.cur.execute("UPDATE deliveryinfo SET cust_warning = 1 WHERE order_id = '{}'".format(order_id))
        self.con.commit()

    def delete_delivery_items(self):
        self.cur.execute("DELETE FROM deliveryinfo WHERE status = 1 ")
        self.con.commit()

    def select_delivery_rating(self,order_id):
        result = self.cur.execute("SELECT delviery_rating FROM deliveryinfo WHERE order_id = '{}".format(order_id)).fetchone()
        return result

    def update_delivery_rating(self,order_id,rating):
        self.cur.execute("UPDATE deliveryinfo SET delivery_rating = '{}' WHERE order_id = '{}'".format(rating,order_id))
        self.con.commit()


#TESTING SOME INSERT FUNCTIONS
#insert_restaurant("1","Los Quatro Amigos", "160 self.convent Ave","3123456543", "11365")
#inserting to restaurant works
###############################
fname = "Lenny"
lname = "Gonzalez"
address = "160 self.convent Ave"
user_id = "Lenny"
city = "Harlem"
phone = "1234567899"
postal = "11365"
ssn = "123456789"
birthday = "01-01-2017"
salary = "20.25"
date_hired = datetime.now()
emp_id = "C4"
#KEEP COMMENTED.
#insert_employees(emp_id,fname,lname,address,phone,city,ssn,birthday,salary,date_hired)
#print(select_employee_info(emp_id))
#insert_deliveryinfo("1",emp_id, user_id, "0","")

# print(select_delivery_info())
#insert_employees("C0003","Lenny","Gonzalez","160 self.convent Ave","1234567899","Harlem","123456789","01-01-2017",)
#inserting to employees works, just need to figure out auto emp_id creation. or have a counter in views.py and self.concatonate the first letter with counter. e.g C + counter, counter = 1
#db.insert_users(user_id,fname,lname,"poop","e.simkhayev@gmail.com",address,city,postal,phone,birthday,salary)
# = db_connect()
#db.insert_users("edris","eddy","simmy","ilovecake","160 Convent Ave","New York","NY","10031","123","9175555555")
#print(db.select_user_info('edris'))
db = db_connect()
#print(db.select_chef_name())
#db.insert_orders("1","edris","C1","1","10","1","0")
#menu_id = db.select_menu_id('C1')
#print(menu_id[0])