import sqlite3
from datetime import date

class Db:
    def __init__(self):
        self.conn = None
        self.currentUser = None

    def setup(self):
        dbName = input("Enter db name: ")
        self.conn = sqlite3.connect(dbName + ".db")

    def generatePid(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        return str(len(posts) + 1).zfill(4)

    def login(self, uid, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE uid = :uid AND pwd = :password", {"uid": uid, "password": password})
        user = c.fetchone()
        if (user == None):
            return False
        else:
            self.currentUser = user
            return True
    
    def logout(self):
        self.currentUser = None

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

    def getUsers(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users")
        return c.fetchall()

    def close(self):
        self.conn.close()