import sqlite3
from datetime import date
from User import User
import array

class Db:
    def __init__(self):
        self.conn = None
        self.currentUser = None

    def setup(self):
        dbName = input("Enter db name: ")
        self.conn = sqlite3.connect(dbName + ".db")
        self.createPostInfoView()

    def generateVno(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM votes")
        result = c.fetchall()

        return len(result) + 1

    def generatePid(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        return str(len(posts) + 1).zfill(4)

    def generateVno(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM votes")
        votes = c.fetchall()
        return len(votes) + 1

    def login(self, uid, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE uid = :uid AND pwd = :password", {"uid": uid, "password": password})
        user = c.fetchone()
        if (user == None):
            return False
        else:
            privileged = c.execute(f"SELECT * FROM privileged WHERE uid = '{uid}'")
            self.currentUser = User(user[0], c.fetchone() != None)
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
        pid = self.generatePid()
        c.execute(
            """
                INSERT INTO posts VALUES
                (:pid, :pdate, :title, :body, :poster)
            """, {"pid": pid, "pdate": date.today(), "title": title, "body": body, "poster": self.currentUser.uid}
        )

        c.execute(
            """
                INSERT INTO questions VALUES
                (:pid, :theaid)
            """, {"pid": pid, "theaid": None}
        )

        self.conn.commit()
        return
    
    def postVote(self, pid, uid):
        vno = self.generateVno()
        c = self.conn.cursor()
        c.execute(
            """
                INSERT INTO votes VALUES
                (:pid, :vno, :vdate, :uid)
            """, {"pid": pid, "vno": vno, "vdate": date.today(), "uid": uid}
        )
        self.conn.commit()
        return
    
    def getPost(self, pid):
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM posts WHERE pid = '{pid}'")
        return c.fetchone()
    
    def getAnswer(self, pid):
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM answers WHERE pid = '{pid}'")
        return c.fetchone()

    def getQuestion(self, pid):
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM questions WHERE pid = '{pid}'")
        return c.fetchone()

    def generateMatchingKeywordQuery(self, keywords):
        firstKey = keywords.pop(0)
        query = f"""SELECT pid, '{firstKey}' AS tag FROM posts
                WHERE title LIKE '%{firstKey}%'
                OR body LIKE '%{firstKey}%'
                OR '{firstKey}' IN (
                    SELECT tag FROM tags
                    WHERE posts.pid = tags.pid
                )"""
        for keyword in keywords:
            q = f"""UNION
            SELECT pid, '{keyword}' AS tag FROM posts
            WHERE title LIKE '%{keyword}%'
            OR body LIKE '%{keyword}%'
            OR '{keyword}' IN (
                SELECT tag FROM tags
                WHERE posts.pid = tags.pid
            )"""
            query += q
        
        return query

    def searchPost(self, keywords):
        c = self.conn.cursor()
        query = f"""
        SELECT p1.pid, postInfo.title, postInfo.body, postInfo.voteCnt, postInfo.ansCnt, p1.matchCnt
        FROM (
            SELECT matching_posts.pid, COUNT(*) AS matchCnt
            FROM ({self.generateMatchingKeywordQuery(keywords.split())}) matching_posts
            GROUP BY matching_posts.pid
        ) p1, postInfo
        WHERE p1.pid = postInfo.pid
        """
        c.execute(query)
        result = c.fetchall()
        return result

    def giveBadge(self, bname, btype, pid):
        c = self.conn.cursor()
        c.execute(
            """
                INSERT INTO badges VALUES
                (:bname, :btype)
            """, {"bname": bname, "btype": btype}
        )
        c.execute(f"SELECT poster FROM posts WHERE pid = '{pid}'")
        result = c.fetchone()
        poster = result[0]
        c.execute(
            """
                INSERT INTO ubadges VALUES
                (:uid, :bdate, :bname)
            """, {"uid": poster, "bdate": date.now(),"bname": bname}
        )        
        self.conn.commit()
        return

    def getBadges(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM badges")
        return c.fetchall()

    def getUbadges(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM ubadges")
        return c.fetchall()

    def getUsers(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users")
        return c.fetchall()
    
    def getAllPosts(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts")
        return c.fetchall()

    def deleteAllPosts(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM posts")
        c.execute("DELETE FROM answers")
        c.execute("DELETE FROM questions")
        self.conn.commit()

    def deleteBadges(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM badges")
        c.execute("DELETE FROM ubadges")
        self.conn.commit()

    def createPostInfoView(self):
        c = self.conn.cursor()
        c.execute("DROP VIEW IF EXISTS postInfo")
        c.execute(
            """
            CREATE VIEW postInfo AS
            SELECT posts.pid, posts.title, posts.body, v_count.voteCnt, a_count.ansCnt
            FROM questions
            JOIN posts ON posts.pid = questions.pid
            JOIN 
                (SELECT questions.pid, COUNT(votes.pid) AS voteCnt
                FROM questions
                LEFT JOIN votes ON votes.pid = questions.pid
                GROUP BY questions.pid) AS v_count ON v_count.pid = posts.pid
            JOIN 
                (SELECT questions.pid, COUNT(answers.pid) AS ansCnt
                FROM questions
                LEFT JOIN answers ON questions.pid = answers.qid
                GROUP BY questions.pid) AS a_count ON a_count.pid = posts.pid
            UNION
            SELECT posts.pid, posts.title, posts.body, v_count.voteCnt, 0 AS ansCnt
            FROM answers
            JOIN posts ON posts.pid = answers.pid
            JOIN 
                (SELECT answers.pid, COUNT(votes.pid) AS voteCnt
                FROM answers
                LEFT JOIN votes ON votes.pid = answers.pid
                GROUP BY answers.pid) AS v_count ON v_count.pid = posts.pid
            """
        )
        self.conn.commit()
    
    def postAnswer(self, qid, title, body):
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM posts WHERE pid = '{qid}'")
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

    def isVoted(self, pid, uid):
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM votes WHERE pid = '{pid}' AND uid = '{uid}'")
        result = c.fetchone()
        if (result != None):
            return True
        else:
            return False
    

    # source: https://stackoverflow.com/a/12065663
    def printTable(self, data):
        widths = [max(map(len, map(str, col))) for col in zip(*data)]
        for row in data:
            print("  ".join(str(val).ljust(width) for val, width in zip(row, widths)))


    def close(self):
        self.conn.close()