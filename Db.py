import sqlite3
import datetime
from User import User
import array


class Db:
    def __init__(self):
        self.conn = None

    def setup(self):
        dbName = input("Enter db name: ")
        self.conn = sqlite3.connect(dbName + ".db")

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

    def getUser(self, uid, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE uid = :uid AND pwd = :password",
                  {"uid": uid, "password": password})
        user = c.fetchone()
        if (user == None):
            raise Exception("Uid or password is wrong")
        else:
            c.execute("SELECT * FROM privileged WHERE uid = :uid",
                      {"uid": uid})
            return User(user[0], c.fetchone() != None)

    def register(self, uid, name, password, city):
        c = self.conn.cursor()
        c.execute("SELECT uid FROM users WHERE uid = :uid", {"uid": uid})
        existingUid = c.fetchone()
        if (existingUid == None):
            # create user
            if (len(uid) > 4):
                raise Exception("Uid must be less than 5 characters")
            else:
                c.execute(
                    """
                        INSERT INTO users VALUES
                        (:uid, :name, :password, :city, :date)
                    """, {"uid": uid, "name": name, "password": password, "city": city, "date": datetime.date.today()}
                )
                self.conn.commit()
        else:
            raise Exception("Uid already registered")

    def postRecord(self, uid, title, body):
        c = self.conn.cursor()
        pid = self.generatePid()
        c.execute(
            """
                INSERT INTO posts VALUES
                (:pid, :pdate, :title, :body, :poster)
            """, {"pid": pid, "pdate": datetime.date.today(), "title": title, "body": body, "poster": uid}
        )

        c.execute(
            """
                INSERT INTO questions VALUES
                (:pid, :theaid)
            """, {"pid": pid, "theaid": None}
        )

        self.conn.commit()
        return

    def postVote(self, uid, pid):
        vno = self.generateVno()

        c = self.conn.cursor()
        c.execute("SELECT * FROM votes WHERE pid = :pid AND uid = :uid",
                  {"pid": pid, "uid": uid})
        result = c.fetchone()

        if (result == None):
            c.execute(
                """
                    INSERT INTO votes VALUES
                    (:pid, :vno, :vdate, :uid)
                """, {"pid": pid, "vno": vno, "vdate": datetime.date.today(), "uid": uid}
            )
            self.conn.commit()
        else:
            raise Exception("You already voted on this post")

    def getPost(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts WHERE pid = :pid", {"pid": pid})
        return c.fetchone()

    def getAnswer(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM answers WHERE pid = :pid", {"pid": pid})
        return c.fetchone()

    def getQuestion(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM questions WHERE pid = :pid", {"pid": pid})
        return c.fetchone()

    def generateMatchingKeywordQuery(self, keywords):
        valueMap = {}
        valueMap["key0"] = keywords.pop(0)
        valueMap["pattern0"] = '%' + valueMap["key0"] + '%'
        queryStr = """SELECT pid, :key0 AS tag FROM posts
                WHERE title LIKE :pattern0
                OR body LIKE :pattern0
                OR EXISTS (
                    SELECT tag FROM tags
                    WHERE posts.pid = tags.pid
                    AND tag LIKE :pattern0
                )"""
        for index, keyword in enumerate(keywords):
            keyName = "key" + str(index + 1)
            keyPattern = "pattern" + str(index + 1)
            q = f"""UNION
            SELECT pid, :{keyName} AS tag FROM posts
            WHERE title LIKE :{keyPattern}
            OR body LIKE :{keyPattern}
            OR EXISTS (
                SELECT tag FROM tags
                WHERE posts.pid = tags.pid
                AND tag LIKE :{keyPattern}
            )"""
            valueMap[keyName] = keyword
            valueMap[keyPattern] = '%' + keyword + '%'
            queryStr += q

        return {
            "queryStr": queryStr,
            "valueMap": valueMap
        }

    def searchPost(self, keywords, offset):
        c = self.conn.cursor()
        query = self.generateMatchingKeywordQuery(keywords.split())
        valueMap = query["valueMap"]

        queryStr = f"""
        SELECT p1.pid, postInfo.title, postInfo.body, postInfo.voteCnt, postInfo.ansCnt, p1.matchCnt
        FROM (
            SELECT matching_posts.pid, COUNT(*) AS matchCnt
            FROM ({query["queryStr"]}) matching_posts
            GROUP BY matching_posts.pid
        ) p1, 
        (
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
            SELECT posts.pid, posts.title, posts.body, v_count.voteCnt, 'N/A' AS ansCnt
            FROM answers
            JOIN posts ON posts.pid = answers.pid
            JOIN 
                (SELECT answers.pid, COUNT(votes.pid) AS voteCnt
                FROM answers
                LEFT JOIN votes ON votes.pid = answers.pid
                GROUP BY answers.pid) AS v_count ON v_count.pid = posts.pid
        ) postInfo
        WHERE p1.pid = postInfo.pid
        """

        if (offset >= 0):
            valueMap["offset"] = offset
            queryStr += """ORDER BY p1.matchCnt DESC LIMIT 5 OFFSET :offset"""

        c.execute(queryStr, valueMap)
        result = c.fetchall()
        return result

    def giveBadge(self, bname, pid):
        c = self.conn.cursor()
        c.execute("SELECT poster FROM posts WHERE pid = :pid", {"pid": pid})
        result = c.fetchone()
        poster = result[0]
        c.execute("SELECT * FROM badges WHERE bname = :bname",
                  {"bname": bname})
        if (c.fetchone() == None):
            raise Exception("Badge name does not exists")
        try:
            c.execute(
                """
                    INSERT INTO ubadges VALUES
                    (:uid, :bdate, :bname)
                """, {"uid": poster, "bdate": datetime.date.today(), "bname": bname}
            )
            self.conn.commit()
            print(f"Successfully give badge {bname} to user {poster}")
        except Exception:
            raise Exception("You already gave this user a badge today")

    def getBadges(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM badges")
        return c.fetchall()

    def getUbadges(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM ubadges")
        return c.fetchall()

    def getAcceptedAnswer(self, qid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM questions WHERE pid = :qid", {"qid": qid})
        question = c.fetchone()
        if (question != None):
            return question[1]
        else:
            return False

    def markAnswer(self, qid, aid):
        c = self.conn.cursor()
        c.execute("UPDATE questions SET theaid = :aid WHERE pid = :qid", {
                  "aid": aid, "qid": qid})
        self.conn.commit()

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

    def postAnswer(self, uid, qid, title, body):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts WHERE pid = :qid", {"qid": qid})
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
            """, {"pid": pid, "pdate": datetime.date.today(), "title": title, "body": body, "poster": uid}
            )
            c.execute(
                """
                INSERT INTO answers VALUES
                (:pid, :qid)
            """, {"pid": pid, "qid": qid}
            )
            self.conn.commit()

    def addTag(self, pid, tag):
        c = self.conn.cursor()
        c.execute("INSERT INTO tags VALUES (:pid, :tag)",
                  {"pid": pid, "tag": tag})
        self.conn.commit()

    def getTags(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT tag FROM tags WHERE pid = :pid", {"pid": pid})
        return c.fetchall()

    def editPost(self, pid, title, body):
        c = self.conn.cursor()
        c.execute(
            """
                UPDATE posts 
                SET title = :title, body = :body
                WHERE pid = :pid
            """, {"title": title, "body": body, "pid": pid})
        self.conn.commit()

    def editTitle(self, pid, title):
        c = self.conn.cursor()
        if (len(title) == 0):
            raise Exception("Title cannot be empty")
        c.execute(
            """
                UPDATE posts 
                SET title = :title
                WHERE pid = :pid
            """, {"title": title, "pid": pid})
        self.conn.commit()

    def editBody(self, pid, body):
        c = self.conn.cursor()
        if (len(body) == 0):
            raise Exception("Body cannot by empty")
        c.execute(
            """
                UPDATE posts 
                SET body = :body
                WHERE pid = :pid
            """, {"body": body, "pid": pid})
        self.conn.commit()

    def close(self):
        self.conn.close()
