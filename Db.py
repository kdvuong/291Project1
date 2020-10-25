import sqlite3
from datetime import date

class Db:
    def __init__(self):
        self.conn = None

    def setup(self):
        dbName = input("Enter db name: ")
        self.conn = sqlite3.connect(dbName + ".db")

    def login(self, uid, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE uid = :uid AND pwd = :password", {"uid": uid, "password": password})
        user = c.fetchone()
        if (user == None):
            return False
        else:
            return True

    def register(self, uid, name, password, city):
        c = self.conn.cursor()
        c.execute("SELECT uid FROM users WHERE uid = :uid", {"uid": uid})
        existingUid = c.fetchone()
        if (existingUid == None):
            #create user
            if (len(uid) > 4):
                print("Uid must be less than 5 characters")
                return False
            else:
                c.execute(
                    """
                        INSERT INTO users VALUES
                        (:uid, :name, :password, :city, :date)
                    """, {"uid": uid, "name": name, "password": password, "city": city, "date": date.today()}
                )
                self.conn.commit()
                return True

        else:
            print("Uid already registered")
            return False

    def searchPost(self, keyword):
        c = self.conn.cursor()
        sql = "SELECT * from posts p, tags t WHERE p.pid = t.pid and p.title LIKE '%s' or p.body LIKE '%s' or t.tag LIKE '%s'"
        placeHolder = keyword
        c.execute(sql, placeHolder, placeHolder, placeHolder)

    def getUsers(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users")
        return c.fetchall()

    def close(self):
        self.conn.close()