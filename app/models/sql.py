import sqlite3
from datetime import datetime, date

with sqlite3.connect("losquatroamigos.db") as connection:
    c = connection.cursor()

    ##TABLES##

    #restaurant##
    c.execute('DROP TABLE if EXISTS restaurant')
    c.execute("""CREATE TABLE restaurant (
    res_id nchar(1) not null,
    name varchar(20) not null,
    address varchar(40) not null,
    city varchar(20) not null,
    state nchar(2) not null,
    postal nchar(5) not null,
    phone nchar(10) not null,
    PRIMARY KEY (res_id)
    )""")

    #employees##
    c.execute('DROP TABLE if EXISTS employees')
    c.execute("""CREATE TABLE employees (
    emp_id VARCHAR(5) not null,
    password varchar(20) not null,
    emp_fname varchar(20) not null,
    emp_lname varchar(20) not null,
    address varchar(40) not null,
    city varchar(20) not null,
    state nchar(2) not null,
    postal char(5) not null,
    apt varchar(5),
    phone nchar(10) not null,
    ssn varchar(9),
    birthdate DATE not null,
    salary decimal(5,2) not null,
    date_hired [timestamp] timestamp,
    hired nchar(1) not null,
    demotions int,
    compliments int,
    complaints int,
    last_ordered [timestamp] timestamp,
    PRIMARY KEY (emp_id)
    )""")

    #users##
    c.execute('DROP TABLE if EXISTS users')
    c.execute("""CREATE TABLE users (
    user_id VARCHAR(9) not null,
    f_name varchar(20) not null,
    l_name varchar(40) not null,
    password VARCHAR(20) NOT NULL,
    address varchar(40) not null,
    city varchar(20) not null,
    state nchar(2) not null,
    postal nchar(5) not null,
    apt varchar(5),
    longitude decimal(9,6),
    latitude decimal (9,6),
    phone nchar(10) not null,
    memb_since DATE not null,
    acc_funds decimal(7,2) not null,
    registered nchar(1) not null,
    warnings int,
    VIP nchar(1) not null,
    order_count nchar(5) not null,
    cash_spent nchar(5) not null,
    PRIMARY KEY (user_id)
    )""")

    #ratings##
    c.execute('DROP TABLE if EXISTS foodrating')
    c.execute("""CREATE TABLE foodrating (
    user_id VARCHAR(9) not null,
    menu_id VARCHAR(5) not null,
    menu_item varchar(50) not null,
    rating nchar(1),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")

    #complaints##
    c.execute('DROP TABLE if EXISTS complaints')
    c.execute("""CREATE TABLE complaints (
    complaint_id INTEGER PRIMARY KEY,
    user_id VARCHAR(9) not null,
    emp_id VARCHAR(5) not null,
    complaint text,
    approval nchar(1),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
    )""")

    #compliments##
    c.execute('DROP TABLE if EXISTS compliments')
    c.execute("""CREATE TABLE compliments (
    compliment_id INTEGER PRIMARY KEY,
    user_id VARCHAR(9) NOT NULL,
    emp_id VARCHAR(5) NOT NULL,
    compliment text,
    approval boolean,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
    )""")

    #orders##
    c.execute('DROP TABLE if EXISTS orders')
    c.execute("""CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id VARCHAR(9) not null,
    menu_item text not null,
    total_price decimal(5,2) not null,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")

    #figuring out how autoincrement works.
    #c.execute('INSERT INTO orders VALUES(NULL,"U0001","C0001","M0001","STEAK", "10.00")')
    #select_top5_ratings("U0001")


    ##chefs##chef rating will be average of all menu item ratings.
    c.execute('DROP TABLE if EXISTS chefs')
    c.execute("""CREATE TABLE chefs (
    chef_id VARCHAR(5) NOT NULL,
    emp_id VARCHAR(5) NOT NULL,
    menu_name varchar(20) NOT NULL,
    chef_rating nchar(1),
    PRIMARY KEY (chef_id),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
    )""")

    ##delivery information##
    c.execute('DROP TABLE if EXISTS deliveryinfo')
    c.execute("""CREATE TABLE deliveryinfo (
    order_id INT PRIMARY KEY,
    emp_id VARCHAR(5),
    user_id VARCHAR(9) not null,
    status char(1) not null,
    cust_warning char(1) not null,
    delivery_rating char(1),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")

    ##menu/menu items##
    c.execute('DROP TABLE if EXISTS menus')
    c.execute("""CREATE TABLE menus (
    chef_id VARCHAR(5) not null,
    item_pic text,
    menu_id VARCHAR(5) not null,
    item_name text not null,
    price decimal(5,2) not null,
    rating varchar(1),
    rating_quantity varchar(5),
    item_description text not null,
    order_count varchar(5) not null,
    FOREIGN KEY (chef_id) REFERENCES chefs(chef_id)
    )""")

    ##checkout-cart
    c.execute('DROP TABLE if EXISTS cart')
    c.execute("""CREATE TABLE cart (
    user_id varchar(5) not null,
    chef_id varchar(5) not null,
    menu_id varchar(5) not null,
    item_name text not null,
    qty int not null )""")

    ##sample data!##
    #RESTAURANT##
    c.execute('INSERT INTO restaurant VALUES("1","Los Quatro Amigos","160 Convent Ave","New York","NY","10031","2126507000")')

    ##END OF RESTAURANT DATA###

    ##EMPLOYEES##
    ##CHEFS##
        #CHEF JUAN#
    c.execute('INSERT INTO employees VALUES ("C1","pizza","Juan","Gonzalez","160 Convent Ave",'
              '"New York","NY", "10031","4L","2126507000","123456789","1985-05-21","25.50","2017-01-01", 1,0,0,0,"2017-01-01")')
    c.execute('INSERT INTO chefs VALUES ("1","C1","Juan\'s Mole","")')

        #CHEF MIGGY#
    c.execute('INSERT INTO employees VALUES ("C2","pizza","Miguel","Dominguez","160 Convent Ave",'
              '"New York", "NY", "10031", "5L","2126507000","123456789","1979-02-02","25.50","2017-01-01", 1,0,0,0,"2017-01-01")')
    c.execute('INSERT INTO chefs VALUES("2","C2","Miggy\'s Seafood","")')

        #Chef Monica#
    c.execute('INSERT INTO employees VALUES ("C3","pizza","Monica","Gonzalez","160 Convent Ave",'
              '"New York","NY", "10031","6L","2126507000","123456789","1991-08-21","25.50","2017-01-01", 1,0,0,0,"2017-01-01")')
    c.execute('INSERT INTO chefs VALUES ("3","C3","Monica\'s Sweets","")')

        #Chef Rosita#
    c.execute('INSERT INTO employees VALUES ("C4","pizza","Rosita","Rodriguez","160 Convent Ave",'
              '"New York","NY", "10031","2L","2126507000","123456789","1980-05-21","25.50","2017-01-01", 1,0,0,0,"2017-01-01")')
    c.execute('INSERT INTO chefs VALUES ("4","C4","Rosita\'s Gill Grill","") ')

    ##Delivery Personnel##

        #Delivery Boy Dave
    c.execute('INSERT INTO employees VALUES ("D1","pizza","David","Jones","160 Convent Ave",'
              '"New York","NY", "10031","4A","2126507000","123456789","1994-08-21","10.50","2017-01-01", 1,0,0,0,"2017-01-01")')

        #Delivery Boy Max
    c.execute('INSERT INTO employees VALUES ("D2","pizza","Max","Young","160 Convent Ave",'
              '"New York","NY", "10031","2P","2126507000","123456789","1990-09-11","10.50","2017-01-01", 1,0,0,0,"2017-01-01")')

    ##END OF DELIVERY PERSONNEL DATA##

    ##Managers##
        #Manager Emily#
    c.execute('INSERT INTO employees VALUES ("M1","pizza","Emily","Dickerson","160 Convent Ave",'
              '"New York","NY", "10031","4B","2126507000","123456789","1985-01-21","27.50","2017-01-01", 0,0,0,0,"2017-01-01")')

        #Manager Jeff#
    c.execute('INSERT INTO employees VALUES ("M2","pizza","Jeff","Edwards","160 Convent Ave",'
              '"New York","NY", "10031","1C","2126507000","123456789","1994-08-21","10.50","2017-01-01", 0,0,0,0,"2017-01-01"   )')


    ###### END OF MANAGER DATA##

    ### END OF EMPLOYEES DATA##

    #MENUS/MENU ITEMS

        #CHEF MIGUEL#
    #insert_menu(chef_id, menu_id, item_name, price, rating)
    c.execute('INSERT INTO menus VALUES '
              '("C2","Tacos de Bistec.jpg","1","Bistec (Steak)","14.00","2", "2","Tacos de Bistec are simply steak tacos! Perfect for anytime of the day","0"),'
              '("C2","Tacos de Pollo.jpg","2","Pollo (Chicken)","11.00","4", "2","Tacos de Pollo are simply chicken tacos! Perfect for anytime of the day","0"),'
              '("C2","Tacos de Chorizo.jpg","3","Chorizo (Sausage)","9.00","5", "2","Tacos de Chorizo are tacos with mexican sausage. The perfect amount of spiceness complemented by freshly chopped onion and celantro","0"),'
              '("C2","Tacos de Cecina.jpg","4","Cecina (Jerky Style Beef)","13.00","5", "2","Tacos de Cecina are similar to steak tacos, but the meat is jerky styled beef","0"),'
              '("C2","Tacos de Carnitas.jpg","5","Carnita (Deep Fried Pork)","9.00","3", "2","Tacos de Carnitas are Pork Tacos which come with an extra kick of spicyness","0"),'
              '("C2","Tacos de Lengua.jpg","6","Lenuga (Beef Tounge)","12.00","4", "2","Tacos de Lengua are Tongue Tacos, very delicious","0"),'
              '("C2","Torta de Queso Blanco.jpg","7","Queso Blanco (Fresh White Cheese)","5.00","3", "2","Torta de Queso Blano, is basically a grilled cheese, but with avacado beans and jalapeno!","0"),'
              '("C2","Torta de Milanesa.jpg","8","Milanesa (Breaded Steak)","15.00","4", "2","Torta de Milanesa, is sandwich with chicken milanese","0"),'
              '("C2","Torta de Jamon.jpg","9","Jamon (Ham)","11.00","4", "2","Torta de Jamon, is a Ham sandwich","0"),'
              '("C2","Torta de Carne Enchilada.jpg","10","Carne Enchilada (Hot and Spicy Pork)","14.00","4", "2","Torta de Carne Enchilada is a sandwich with a slice of spicy pork! A great lunch option","0")')

        #CHEF MONICA#
    c.execute('INSERT INTO menus VALUES '
              '("C3","Lobster Ceviche.jpg","1","Lobster Ceviche","24.00","2", "2", "A delicious South American dish of marinated lobster and shrimp","0"),'
              '("C3","Yelllow Tail Sashimi.jpg","2","Yellowtail Sashimi with Dry Miso and Yuza Sauce","24.00","2", "2","Bite-sized pieces of raw yellow tail eaaten with soy sauce and wasabi paste","0"),'
              '("C3","Shiromi Usuzukari.jpg","3","Shiromi Usuzukari","9.00","4", "2","This thinly sliced fish is amazing, dipped in ponzu sauce with a bit of green onion.","0"),'
              '("C3","Bigeye Tuna Tataki.jpg","4","Bigeye Tuna Tataki with Tosazu","19.00","4", "2","This dish consists of fish steak, served slightly raw","0"),'
              '("C3","Sea Urchin Tempura.jpg","5","sea Urchin Tempura","9.00","4", "2","Sea Urchin that has been battered and deep fried","0"),'
              '("C3","Rock Shrimp Tempura.jpg","6","Rock Shrimp Tempura with Ponzu","11.00","5", "2","Rock Shrimp that has been battered and deep fried","0"),'
              '("C3","Chilean Sea Bass.jpg","7","Chilean Sea Bass with Black Bean Sause","24.00","", "2","Perfectly boiled Lobster served with wasabi paste","0"),'
              '("C3","Lobster with Wasabi.jpg","8","Lobster with Wasabi Pepper Sause","28.00","5", "2","LOL","0"),'
              '("C3","Kaki Age Donburi.jpg","9","Kaki Age Donburi","16.00","4", "2","Perfect for lunch, this meal is a rice bowl with vegetables","0"),'
              '("C3","Tempura Donburi.jpg","10","Tempura Donburi","14.00","4", "2","Donburi that has been battered and deep fried","0"),'
              '("C3","Ribeye Anticucho.jpg","11","Ribeye Anticucho","21.00","3", "2","Ribeye cooked to your liking served in thin slices with antichucho sauce","0")')

        #CHEF Rosita#
    c.execute('INSERT INTO menus VALUES '
              '("C4","Pechuga de Pollo a la parrilla.jpg","1","Pechuga De Pollo A La Parrilla (Grilled Chicken Cutlet)","12.00","4", "2","Grilled Chicken Breast with a side of rice and beans.","0"),'
              '("C4","Milanesa De res.jpg","2","Milanesa De Res (Breaded Steak)","15.00","4", "2","Beef Milanese served with rice","0"),'
              '("C4","Carne de Enchilada.jpg","3","Carne Enchilada (Hot and Spicy Pork)","14.00","4", "2","Slice of pork with a spicy paste served with rice.","0"),'
              '("C4","Medio Pollo Rostizado.jpg","4","Medio Pollo Rostizado (Half Roasted Chicken)","12.00","4", "2","Half of Rotisserie Chicken served with plantains rice and beans","0"),'
              '("C4","Pernil Horneado.jpg","5","Pernil Horneado (Roasted Pork)","14.00","4", "2","Roasted Pork with spicy sauce","0"),'
              '("C4","Bistec Encebollado.jpg","6","Bistec Encebollado (Steak with Onions)","17.00","3", "2","Steak served with a side of spicy sauce and rice","0"),'
              '("C4","Carne de Cecina.jpg","7","Carne De Cecina (Jerky Beef Steak)","13.00","5", "2","Jerky Styled Beef with a side salad and rice","0"),'
              '("C4","Mole Poblano.jpg","8","Mole Poblano (Chicken with Mole)","15.00","5", "2","Chicken served with Mole sauce, which is chocolate based, and sprinkled with sunflower seeds","0")')


    #USERS###
    c.execute('INSERT INTO users VALUES '
              '("test","Kristen","Sedor","test","580 St Nicholas Ave","New York","NY","10030","34", "34","random", "sdf","4L","2121234567","1","50.00", "0","0","0")')
    c.execute('INSERT INTO users VALUES '
              '("some","Count","Olaf","one","580 St Nicholas Ave","New York","NY","10030","34", "34","random", "sdf","4L","2121234567","1","50.00","0","0","0")')
    #template:(user_id, user_fname, user_lname, password, email, address, city, state, postal, apt, phone, memb_since, acc_funds)
    # c.execute('INSERT INTO users VALUES '
    #           '("woozycake","Kristen","Sedor","a1lk3j4","frostman@att.net","580 St Nicholas Ave","New York","NY","10030","4L","2121234567","2017-01-01","50.00"),'
    #           '("waryquiche","Chance","Mee","LK0912","mbrown@icloud.com","69-92 Edgecombe Ave","New York","NY","10030","2M","2121234567","2017-01-01","50.00"),'
    #           '("poisedpolenta","Minna","Sapien","PO23ks","gemmell@att.net","1649 Amsterdam Ave","New York","NY","10031","7C","2127696649","2017-01-01","50.00"),'
    #           '("trainedsyrup","George","Loller","LOsaM3","zeller@mac.com","630 St Nicholas Ave","New York","NY","10030","2L","2122190755","2017-01-01","50.00"),'
    #           '("jazzycheese","Brendon","Pulsifer","LJk5k","dleconte@optonline.net","1508 Amsterdam Ave","New York","NY","10031","2P","2123491649","2017-01-01","50.00"),'
    #           '("highapples","Ernie","Sol","M1N3l","bigmauler@outlook.com","1518 Amsterdam Ave","New York","NY","10031","7D","2121654987","2017-01-01","50.00"),'
    #           '("cuddlyrice","Antoinette","Tropoea","mK2n3","wkrebs@icloud.com","1701 Amsterdam Ave","New York","NY","10031","3C","2126597316","2017-01-01","50.00"),'
    #           '("draftyclam","Gergory","Crane","oL245","jandrese@att.net","628-628 Riverside Dr","New York","NY","10031","4T","2124697315","2017-01-01","50.00"),'
    #           '("thesedoughnuts","Dorie","Chastain","0n9n1","raines@sbcglobal.net","601-625 W 133rd St","New York","NY","10027","3D","2127986459","2017-01-01","50.00"),'
    #           '("screechinglard","Graciela","Winfrey","en34l","kingjoshi@outlook.com","2450 Frederick Douglass Blvd","New York","NY","10027","8C","2126482379","2017-01-01","50.00"),'
    #           '("vitalchile","Lashawn","Lafleur","y1x23","fbriere@yahoo.com","501 W 133rd St","New York","NY","10027","2C","2124578126","2017-01-01","50.00"),'
    #           '("gaseoussausage","Bettina","Molter","4k2k1","eabrown@msn.com","603 W 129th St","New York","NY","10027","4D","2129878654","2017-01-01","50.00")')
