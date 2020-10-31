import getpass
from constants import *
import sqlite3
import math

# Class to represent all the actions in the program
class Program:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.currentUser = None

    # Function to print out welcoming string at the start of the program
    def start(self):
        self.db.setup()
        print("\nWelcome, this is mini project 1!")

    # Function to perform login action
    def login(self):
        # user name, password
        uid = input("uid: ")
        password = getpass.getpass("password: ") # invisible password
        try:
            self.currentUser = self.db.getUser(uid, password)
            print(f"Logged in as {self.currentUser.uid}")
        except Exception as err:
            print(err.args[0])

    # Function to perform register action
    def register(self):
        print("\nREGISTER")
        uid = input("Enter uid: ")

        if (len(uid) > 4):
            print("Uid must be less than 5 characters")
            return

        if (len(uid) == 0):
            print("Uid cannot be empty")
            return

        password = getpass.getpass("Enter password: ") # invisible password
        if (len(password) == 0):
            print("Password cannot be empty")
            return

        name = input("Enter name (optional): ")
        city = input("Enter city (optional): ")

        try:
            self.db.register(uid, name, password, city)
            print("Register success")
        except Exception as err:
            print(err.args[0])
            print("Register fail")

    # Function to perform posting question action
    def postQuestion(self):
        title = input("Post title: ")
        if (len(title) == 0):
            print("Title cannot be empty")
            return

        body = input("Post body: ")
        if (len(body) == 0):
            print("Body cannot be empty")
            return
        try:
            self.db.postRecord(self.currentUser.uid, title, body)
        except Exception as err:
            print(err.args[0])

    # Function to get all the posts with matching keywords
    def searchGetAll(self, keywords):
        result = self.db.searchPost(keywords, -1)
        if (len(result) == 0):
            raise Exception(
                f"No posts have the entered keyword(s): {keywords}")

        return result

    # Function to paginate the searching result ( at most 5 posts per page )
    def searchPaginate(self, keywords, currentPage):
        result = self.db.searchPost(
            keywords, (currentPage - 1) * 5)  # searching by keyword
        if (len(result) == 0 and currentPage == 1):
            raise Exception(
                f"No posts have the entered keyword(s): {keywords}")

        return result

    # Function to perform search action
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

            allResultCount = len(self.searchGetAll(keywords)) # return number of post with matching keyword

            while (True):
                result = self.searchPaginate(keywords, currentPage) # pagnite the result
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
                    if (validPid):
                        while (True):
                            try:
                                postAction = self.getPostAction(option)
                                if (postAction == BACK_ACTION):
                                    break
                                postAction(self, option)
                            except Exception as err:
                                print(err.args[0])
                    else:
                        print(
                            f"ERROR: PID {option} not in search result. Please try again with another option.")
        except Exception as err:
            print(err.args[0])

    # Function to perform selecting a post by post ID action 
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
    
    # Function to perform posting an answer post action
    def postAnswer(self, postId):
        title = input("Answer title: ")
        if (len(title) == 0):
            print("Title cannot be empty")
            return

        body = input("Answer body: ")
        if (len(body) == 0):
            print("Body cannot be empty")
            return
        self.db.postAnswer(self.currentUser.uid, postId, title, body)

    # Function to perform casting a vote to a post action
    def castVote(self, postId):
        try:
            self.db.postVote(self.currentUser.uid, postId)
        except Exception as err:
            print(err.args[0])

    # Function to perform giving a badge to a poster action
    def giveBadge(self, postId):
        bname = input("Badge name: ")
        self.db.giveBadge(bname, postId)

    # Function to perform adding a tag to a post action
    def addTag(self, postId):
        tag = input("Enter tag name: ")
        self.db.addTag(postId, tag)
        print(self.db.getTags(postId))

    # Function to perform marking an accepted answer action
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

    # Function to perform editing a post action
    def editPost(self, postId):
        edit = input(EDIT_ACTION_PROMPT)
        if edit == '1':
            newTitle = input("Enter a new title: ")
            if (len(newTitle) == 0):
                print("Title cannot be empty")
                return
            newBody = input("Enter a new body: ")
            if (len(newBody) == 0):
                print("Body cannot be empty")
                return
            self.db.editPost(postId, newTitle, newBody)
        elif edit == '2':
            newTitle = input("Enter a new title: ")
            if (len(newTitle) == 0):
                print("Title cannot be empty")
                return
            self.db.editPost(postId, newTitle, "")
        elif edit == '3':
            newBody = input("Enter a new body: ")
            if (len(newBody) == 0):
                print("Body cannot by empty")
            self.db.editPost(postId, "", newBody)
        else:
            print("Invalid action")

    # source: https://stackoverflow.com/a/12065663
    # Function to print out the result table in search  
    def printTable(self, data):
        widths = [max(map(len, map(str, col))) for col in zip(*data)]
        for row in data:
            print("  ".join(str(val).ljust(width)
                            for val, width in zip(row, widths)))

    # Function to perform logout action
    def logout(self):
        self.currentUser = None
        print("Logged out")

    # Function to quit the program
    def end(self):
        self.db.close()
        print("Good bye!")
