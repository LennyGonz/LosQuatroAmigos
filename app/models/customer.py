import sqlite3 as sql


#get users top 5 rated foods.
def select_top5_rated(user_id):
    with sql.connect("losquatroamigos.db") as con:
        cur = con.cursor()
        result = cur.execute("SELECT menu_item,rating FROM ratings WHERE user_id = '%s' ORDER BY rate DESC LIMIT 5" %user_id).fetchall()
    return result


#retrieve complaints
def select_complaints(user_id):
    with sql.connect("losquatroamigos.db") as con:
        cur = con.cursor()
        result = cur.execute("SELECT complaint, date_posted FROM complaints WHERE user_id = '%s'" %user_id).fetchall()
    return result

#retrive compliments
def select_compliments(user_id):
    with sql.connect("losquatroamigos.db") as con:
        cur = con.cursor()
        result = cur.execute("SELECT compliment, date_posted FROM compliments WHERE user_id = '%s'" %user_id).fetchall()
    return result
