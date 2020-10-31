import sqlite3
import datetime
from User import User
import array

# Class to represent database


class Db:
    def __init__(self):
        self.conn = None

    # Function to setup the connection with the database
    def setup(self):
        dbName = input("Enter db name: ")
        self.conn = sqlite3.connect(dbName + ".db")

    # Function to generate vote number for votes
    def generateVno(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM votes")
        result = c.fetchall()

        return len(result) + 1

    # Function to generate post ID for each post
    def generatePid(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        return str(len(posts) + 1).zfill(4)

    # Function to check user and password validity
    def getUser(self, uid, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE uid = :uid AND pwd = :password",
                  {"uid": uid, "password": password})
        user = c.fetchone()
        if (user == None):
            raise Exception("ERROR: Uid or password is wrong")
        else:
            c.execute("SELECT * FROM privileged WHERE uid = :uid",
                      {"uid": uid})
            return User(user[0], c.fetchone() != None)

    # Function to register new user ID and info
    def register(self, uid, name, password, city):
        c = self.conn.cursor()
        c.execute("SELECT uid FROM users WHERE uid = :uid", {"uid": uid})
        existingUid = c.fetchone()
        if (existingUid == None):
            # create user
            if (len(uid) > 4):
                raise Exception("ERROR: Uid must be less than 5 characters")
            else:
                c.execute(
                    """
                        INSERT INTO users VALUES
                        (:uid, :name, :password, :city, :date)
                    """, {"uid": uid, "name": name, "password": password, "city": city, "date": datetime.date.today()}
                )
                self.conn.commit()
        else:
            raise Exception("ERROR: Uid already registered")

    # Function to record the question post into database

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

    # Function to record the vote of a post into database
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
            raise Exception("ERROR: You already voted on this post")

    # Function to return the a post
    def getPost(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts WHERE pid = :pid", {"pid": pid})
        return c.fetchone()

    # Function to return answer post
    def getAnswer(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM answers WHERE pid = :pid", {"pid": pid})
        return c.fetchone()

    # Function to return question post
    def getQuestion(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM questions WHERE pid = :pid", {"pid": pid})
        return c.fetchone()

    # Function to check matching keyword
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
            q = """UNION
            SELECT pid, :{keyName} AS tag FROM posts
            WHERE title LIKE :{keyPattern}
            OR body LIKE :{keyPattern}
            OR EXISTS (
                SELECT tag FROM tags
                WHERE posts.pid = tags.pid
                AND tag LIKE :{keyPattern}
            )""".format(keyName=keyName, keyPattern=keyPattern)
            valueMap[keyName] = keyword
            valueMap[keyPattern] = '%' + keyword + '%'
            queryStr += q

        return {
            "queryStr": queryStr,
            "valueMap": valueMap
        }

    # Function to search for posts based on matching keyword ( at most 5 post is shown on a page )
    def searchPost(self, keywords, offset):
        c = self.conn.cursor()
        query = self.generateMatchingKeywordQuery(keywords.split())
        valueMap = query["valueMap"]

        queryStr = """
        SELECT p1.pid, postInfo.title, postInfo.body, postInfo.voteCnt, postInfo.ansCnt, p1.matchCnt
        FROM (
            SELECT matching_posts.pid, COUNT(*) AS matchCnt
            FROM ({qStr}) matching_posts
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
        """.format(qStr=query["queryStr"])

        if (offset >= 0):
            valueMap["offset"] = offset
            queryStr += """ORDER BY p1.matchCnt DESC LIMIT 5 OFFSET :offset"""

        c.execute(queryStr, valueMap)
        result = c.fetchall()
        return result

    # Function to record given badge to poster
    def giveBadge(self, bname, pid):
        c = self.conn.cursor()
        c.execute("SELECT poster FROM posts WHERE pid = :pid", {"pid": pid})
        result = c.fetchone()
        poster = result[0]
        c.execute("SELECT * FROM badges WHERE bname = :bname",
                  {"bname": bname})
        if (c.fetchone() == None):
            raise Exception("ERROR: Badge name does not exists")
        try:
            c.execute(
                """
                    INSERT INTO ubadges VALUES
                    (:uid, :bdate, :bname)
                """, {"uid": poster, "bdate": datetime.date.today(), "bname": bname}
            )
            self.conn.commit()
            print("Successfully give badge {bname} to user {poster}".format(
                bname=bname, poster=poster))
        except Exception:
            raise Exception("ERROR: You already gave this user a badge today")

    # Function to return all badges

    def getBadges(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM badges")
        return c.fetchall()

    # Function to return all user's badges
    def getUbadges(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM ubadges")
        return c.fetchall()

    # Function to return an accepted answer
    def getAcceptedAnswer(self, qid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM questions WHERE pid = :qid", {"qid": qid})
        question = c.fetchone()
        if (question != None):
            return question[1]
        else:
            return False

    # Function to record mark answer to database
    def markAnswer(self, qid, aid):
        c = self.conn.cursor()
        c.execute("UPDATE questions SET theaid = :aid WHERE pid = :qid", {
                  "aid": aid, "qid": qid})
        self.conn.commit()

    # Function to return all users
    def getUsers(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users")
        return c.fetchall()

    # Function to return all posts
    def getAllPosts(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts")
        return c.fetchall()

    # Function to delete all posts
    def deleteAllPosts(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM posts")
        c.execute("DELETE FROM answers")
        c.execute("DELETE FROM questions")
        self.conn.commit()

    # Function to delete all badges
    def deleteBadges(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM badges")
        c.execute("DELETE FROM ubadges")
        self.conn.commit()

    # Function to record answer post to database
    def postAnswer(self, uid, qid, title, body):
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts WHERE pid = :qid", {"qid": qid})
        question = c.fetchone()
        # this should never happen
        if (question == None):
            raise Exception("ERROR: Question doesn't exist")
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

    # Function to record tags to database
    def addTag(self, pid, tag):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT * FROM tags
            WHERE pid = :pid
            AND LOWER(tag) != :tag
            """, {"pid": pid, "tag": tag.lower()}
        )
        if (c.fetchone() == None):
            c.execute("INSERT INTO tags VALUES (:pid, :tag)",
                      {"pid": pid, "tag": tag})
            self.conn.commit()
        else:
            raise Exception(
                "ERROR: Post already have tag '{tag}'".format(tag=tag))

    # Function to return all tags of a post
    def getTags(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT tag FROM tags WHERE pid = :pid", {"pid": pid})
        return c.fetchall()

    # Function to record the edited title and body of a post to database
    def editPost(self, pid, title, body):
        c = self.conn.cursor()
        if (len(title) > 0):
            c.execute(
                """
                    UPDATE posts 
                    SET title = :title
                    WHERE pid = :pid
                """, {"title": title, "pid": pid})

        if (len(body) > 0):
            c.execute(
                """
                UPDATE posts 
                SET body = :body
                WHERE pid = :pid
            """, {"body": body, "pid": pid})

        self.conn.commit()

    # Function to close the database connection
    def close(self):
        self.conn.close()
