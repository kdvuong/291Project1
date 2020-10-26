import sqlite3
from datetime import date

class Db:
    def __init__(self):
        self.conn = None
        self.currentUser = None

    def setup(self):
        dbName = input("Enter db name: ")
        self.conn = sqlite3.connect(dbName + ".db")
        self.createPostInfoView()

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

    def postRecord(self, pid, title, body):
        c = self.conn.cursor()
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
        SELECT p1.pid, postInfo.voteCnt, postInfo.ansCnt, p1.matchCnt
        FROM (
            SELECT matching_posts.pid, COUNT(*) AS matchCnt
            FROM ({self.generateMatchingKeywordQuery(keywords.split())}) matching_posts
            GROUP BY matching_posts.pid
        ) p1, postInfo
        WHERE p1.pid = postInfo.pid
        """
        c.execute(query)
        headers = [("pid", "voteCnt", "ansCnt", "matchCnt")]
        self.printTable(headers + c.fetchall())
    
    def isQuestion(postID):
        return False
        
    def answerPost():

    def votePost():

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

    def createPostInfoView(self):
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='postInfo'")
        if (c.fetchone()):
            return

        c.execute(
            """
            CREATE VIEW postInfo AS
            SELECT posts.pid, v_count.voteCnt, a_count.ansCnt
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
            SELECT posts.pid, v_count.voteCnt, 0 AS ansCnt
            FROM answers
            JOIN posts ON posts.pid = answers.pid
            JOIN 
                (SELECT answers.pid, COUNT(votes.pid) AS voteCnt
                FROM answers
                LEFT JOIN votes ON votes.pid = answers.pid
                GROUP BY answers.pid) AS v_count ON v_count.pid = posts.pid
            """
        )

    def printTable(self, data):
        col_width = max(len(str(word)) for row in data for word in row) + 2  # padding
        for row in data:
            print("".join(str(word).ljust(col_width) for word in row))

    def close(self):
        self.conn.close()