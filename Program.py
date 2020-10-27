import getpass
from constants import *
import sqlite3
import math


class Program:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.currentUser = None

    def start(self):
        self.db.setup()
        print("\nWelcome, this is mini project 1!")

    def login(self):
        # user name, password
        uid = input("uid: ")
        password = getpass.getpass("password: ")
        try:
            self.currentUser = self.db.getUser(uid, password)
            print(f"Logged in as {self.currentUser.uid}")
        except Exception as err:
            print(err.args[0])

    def register(self):
        uid = input("uid: ")
        password = getpass.getpass("password: ")
        name = input("name: ")
        city = input("city: ")

        try:
            self.db.register(uid, name, password, city)
            print("Register success")
        except Exception as err:
            print(err.args[0])
            print("Register fail")

    def postQuestion(self):
        title = input("Post title: ")
        body = input("Post body: ")
        self.db.postRecord(self.currentUser.uid, title, body)

    def searchGetAll(self, keywords):
        result = self.db.searchPost(keywords, -1)
        if (len(result) == 0):
            raise Exception(
                f"No posts have the entered keyword(s): {keywords}")

        return result

    def searchPaginate(self, keywords, currentPage):
        result = self.db.searchPost(
            keywords, (currentPage - 1) * 5)  # searching by keyword
        if (len(result) == 0 and currentPage == 1):
            raise Exception(
                f"No posts have the entered keyword(s): {keywords}")

        return result

    def search(self):
        try:
            currentPage = 1
            keywords = input(
                "Enter keyword(s) separate by space to search for posts: ")
            print("")

            headers = [("pid", "title", "body",
                        "voteCnt", "ansCnt", "matchCnt")]

            if (len(keywords) == 0):
                raise Exception("Keyword must have at least a character")

            allResultCount = len(self.searchGetAll(keywords))

            while (True):
                result = self.searchPaginate(keywords, currentPage)
                resultCount = len(result)
                noNext = resultCount < 5 or (
                    resultCount + currentPage * 5 == allResultCount)
                noPrev = currentPage == 1
                if (resultCount > 0):
                    print(
                        f"SEARCH RESULT: Page {currentPage}/{math.ceil(allResultCount / 5)}")
                    self.printTable(headers + result)

                option = input(
                    SEARCH_SUCCESS_ACTION_PROMPT
                    .format(**{
                        "next": NEXT_PAGE_PROMPT if not noNext else "",
                        "prev": PREV_PAGE_PROMPT if not noPrev else ""
                    })).lower()
                print("")

                if (option == 'next'):
                    if (noNext):
                        print(
                            "ERROR: No availale next page. Please try again with another option.")
                    else:
                        currentPage += 1
                elif (option == "prev"):
                    if (noPrev):
                        print(
                            "ERROR: At page 1, can't go back. Please try again with another option.")
                    else:
                        currentPage -= 1
                elif (option == "back"):
                    break
                else:
                    validPid = False
                    for row in result:
                        if (row[0] == option):
                            validPid = True
                            break
                    try:
                        if (validPid):
                            postAction = self.getPostAction(option)
                            postAction(self, option)
                            break
                        else:
                            print(
                                f"ERROR: PID {option} not in search result. Please try again with another option.")
                    except Exception as err:
                        print(err.args[0])
                        break
        except Exception as err:
            print(err.args[0])

    def getPostAction(self, postId):
        isQuestion = self.db.getQuestion(postId) != None
        isAnswer = self.db.getAnswer(postId) != None
        isPrivileged = self.currentUser.isPrivileged
        actionType = None

        if (isQuestion):
            print("\nThis post is a question.")
            if (isPrivileged):
                actionType = PRIVILEGED_QUESTION
            else:
                actionType = ORDINARY_QUESTION
        elif (isAnswer):
            print("\nThis post is an answer.")
            if (isPrivileged):
                actionType = PRIVILEGED_ANSWER
            else:
                actionType = ORDINARY_ANSWER
        else:
            raise Exception("\nPost does not exist.")

        postAction = self.config[actionType]
        userInput = input(postAction["prompt"]).lower()
        if (userInput in postAction["validInput"]):
            return postAction["postActionHandlers"][userInput]
        else:
            raise Exception("\nInvalid action input.")

    def postAnswer(self, postId):
        title = input("Answer title: ")
        body = input("Answer body: ")
        self.db.postAnswer(self.currentUser.uid, postId, title, body)

    def castVote(self, postId):
        try:
            self.db.postVote(self.currentUser.uid, postId)
        except Exception as err:
            print(err.args[0])

    def giveBadge(self, postId):
        bname = input("Badge name: ")
        btype = input("Badge type: ")
        self.db.giveBadge(bname, btype, postId)

    def addTag(self, postId):
        tag = input("Enter tags seperate by a single space : ")
        self.db.addTag(postId, tag)
        print(self.db.getTags(postId))

    def markAccepted(self, postId):
        answer = self.db.getAnswer(postId)
        qid = answer[1]
        acceptedAnswer = self.db.getAcceptedAnswer(qid)
        if (acceptedAnswer == None):
            self.db.markAnswer(qid, postId)
            print(f"SUCCESS - set {postId} as accepted answer for {qid}")
        elif (acceptedAnswer != None):
            userAccept = input(
                "This question already has an accepted answer, do you want to overwrite it? (Y/N): ").lower()
            if (userAccept == 'y'):
                self.db.markAnswer(qid, postId)
        else:
            print("Unexpected error occurred")

    def editPost(self, postId):
        edit = input(EDIT_ACTION_PROMPT)
        if edit == '1':
            newTitle = input("Enter a new title: ")
            newBody = input("Enter a new body: ")
            self.db.editPost(postId, newTitle, newBody)
        elif edit == '2':
            newTitle = input("Enter a new title: ")
            self.db.editTitle(postId, newTitle)
        elif edit == '3':
            newBody = input("Enter a new body: ")
            self.db.editBody(postId, newBody)
        else:
            print("Invalid action")

    # source: https://stackoverflow.com/a/12065663
    def printTable(self, data):
        widths = [max(map(len, map(str, col))) for col in zip(*data)]
        for row in data:
            print("  ".join(str(val).ljust(width)
                            for val, width in zip(row, widths)))

    def logout(self):
        self.currentUser = None
        print("Logged out")

    def end(self):
        self.db.close()
        print("Good bye!")
