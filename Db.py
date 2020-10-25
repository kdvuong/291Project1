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
            print(user[0])
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

    def postRecord(self, title, body):
        c = self.conn.cursor()
        pid = db.generatePid()
        c.execute(
            """
                INSERT INTO posts VALUES
                (:pid, :pdate, :title, :body, :poster)
            """, {"pid": pid, "pdate": date.today(), "title": title, "body": body, "poster": self.currentUser[0]}
        )

        c.execute(
            """
                INSERT INTO questions VALUES
                (:pid, :theaid)
            """, {"pid": pid, "theaid": None}
        )

        self.conn.commit()
        return
    
    def getPost(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts")
        return c.fetchall()
    
    def getQuestions(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM questions")
        return c.fetchall()

    def getUsers(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users")
        return c.fetchall()

    def postAnswer(self, qid, title, body):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts WHERE pid = :qid", {"qid", qid})
        question = c.fetchone()
        # this should never happen
        if (question == None):
            print("Question doesn't exist")
        else:
            pid = self.generatePid()
            c.execute(
            """
                INSERT INTO posts VALUES
                (:pid, :pdate, :title, :body, :poster)
            """, {"pid": pid, "pdate": date.today(), "title": title, "body": body, "poster": self.currentUser[0]}
            )
            c.execute(
            """
                INSERT INTO answers VALUES
                (:pid, :qid)
            """, {"pid": pid, "qid": qid}
            )
            self.conn.commit()

    def close(self):
        self.conn.close()