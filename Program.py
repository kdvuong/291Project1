import getpass
from constants import *
import sqlite3

class Program:
    def __init__(self, db):
        self.db = db
    
    def login(self):
        # user name, password
        uid = input("uid: ")
        password = getpass.getpass("password: ")
        try:
            self.db.login(uid, password)
            print("Logged in")
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
        self.db.postRecord(title, body)

    def searchGetAll(self, keywords):
        result = self.db.searchPost(keywords, -1)
        if (len(result) == 0):
            raise Exception(f"No posts have the entered keyword(s): {keywords}")
        
        return result
    
    def searchPaginate(self, keywords, currentPage):
        result = self.db.searchPost(keywords, (currentPage - 1) * 5) # searching by keyword
        if (len(result) == 0 and currentPage == 1):
            raise Exception(f"No posts have the entered keyword(s): {keywords}")
        
        return result

    def getPostAction(self, postId):
        isQuestion = self.db.getQuestion(postId) != None
        isAnswer = self.db.getAnswer(postId) != None
        isPrivileged = self.db.currentUser.isPrivileged
        actionType = None
        
        if (isQuestion):
            print("\nThis post is a question.")
            if (isPrivileged): actionType = PRIVILEGED_QUESTION
            else: actionType = ORDINARY_QUESTION
        elif (isAnswer):
            print("\nThis post is an answer.")
            if (isPrivileged): actionType = PRIVILEGED_ANSWER
            else: actionType = ORDINARY_ANSWER
        else:
            raise Exception("\nPost does not exist.")

        postAction = postActions[actionType]    
        userInput = input(postAction["prompt"]).lower()
        if (userInput in postAction["validInput"]):
            return postAction["postActionHandlers"][userInput]
        else:
            raise Exception("\nInvalid action input.")

    def postAnswer(self, postId):
        title = input("Answer title: ")
        body = input("Answer body: ")
        self.db.postAnswer(postId, title, body)
    
    def castVote(self, postId):
        try:
            self.db.postVote(postId)
        except Exception as err: 
            print(err.args[0])
    
    def giveBadge(self, postId):
        bname = input("Badge name: ")
        btype = input("Badge type: ")
        self.db.giveBadge(bname, btype, postId)
    
    def addTags(self, postId):
        tags = input("Enter tags seperate by a single space : ")
        self.db.addTags(postId, tags.split())
        print(self.db.getTag(postId))

    def markAccepted(self, postId):
        answer = self.db.getAnswer(postId)
        qid = answer[1]
        acceptedAnswer = self.db.getAcceptedAnswer(qid)
        if (acceptedAnswer == None):
            self.db.markAnswer(qid, postId)
            print(f"SUCCESS - set {postId} as accepted answer for {qid}")
        elif (acceptedAnswer != None):
            userAccept = input("This question already has an accepted answer, do you want to overwrite it? (Y/N): ").lower()
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
            newBody = input ("Enter a new body: ")
            self.db.editBody(postId, newBody)
        else: print("Invalid action")
    
    # source: https://stackoverflow.com/a/12065663
    def printTable(self, data):
        widths = [max(map(len, map(str, col))) for col in zip(*data)]
        for row in data:
            print("  ".join(str(val).ljust(width) for val, width in zip(row, widths)))

postActions = {
    ORDINARY_QUESTION: {
        "prompt": ORDINARY_QUESTION_ACTION_PROMPT,
        "validInput": ["1", "2", "answer", "vote"],
        "postActionHandlers": {
            "1": Program.postAnswer,
            "answer": Program.postAnswer,
            "2": Program.castVote,
            "vote": Program.castVote
        }
    },
    ORDINARY_ANSWER: {
        "prompt": ORDINARY_ANSWER_ACTION_PROMPT,
        "validInput": ["1", "vote"],
        "postActionHandlers": {
            "1": Program.castVote,
            "vote": Program.castVote
        }
    },
    PRIVILEGED_QUESTION: {
        "prompt": PRIVILEGED_QUESTION_ACTION_PROMPT,
        "validInput": ["1", "2", "3", "4", "5", "answer", "vote", "give", "add", "edit"],
        "postActionHandlers": {
            "1": Program.postAnswer,
            "answer": Program.postAnswer,
            "2": Program.castVote,
            "vote": Program.castVote,
            "3": Program.giveBadge,
            "give": Program.giveBadge,
            "4": Program.addTags,
            "add": Program.addTags,
            "5": Program.editPost,
            "edit": Program.editPost
        }
    },
    PRIVILEGED_ANSWER: {
        "prompt": PRIVILEGED_ANSWER_ACTION_PROMPT,
        "validInput": ["1", "2", "3", "4", "5", "vote", "mark", "give", "add", "edit"],
        "postActionHandlers": {
            "1": Program.castVote,
            "vote": Program.castVote,
            "2": Program.markAccepted,
            "mark": Program.markAccepted,
            "3": Program.giveBadge,
            "give": Program.giveBadge,
            "4": Program.addTags,
            "add": Program.addTags,
            "5": Program.editPost,
            "edit": Program.editPost
        }
    }
}