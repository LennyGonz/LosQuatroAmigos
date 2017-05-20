import sqlite3 as sql


def delete_account(user_id):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE user_id = '%s'" %user_id)
        con.commit()

