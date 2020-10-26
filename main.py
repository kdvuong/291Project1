from Db import Db
import getpass

db = Db()

options = """-----------------------------------
Choose the following option:
-----------------------------------
POST (post a question)
SEARCH (search for a post)
LOGOUT (log out)
------------------------------------
What do you want to do? """

ordinaryQuestionActionPrompt = """Available actions:
1. Answer - post answer to a question
2. Vote - cast vote for a post

Choose an action (number or text): 
"""

ordinaryAnswerActionPrompt = """Available actions:
1. Vote - cast vote for a post

Choose an action (number or text): 
"""

privilegedQuestionActionPrompt = """Available actions:
1. Answer - post answer to a question
2. Vote - cast vote for a post
3. Give - give a badge to a poster
4. Add - add tags to a post
5. Edit - edit the title and/or the body of the post

Choose an action (number or text): 
"""

privilegedAnswerActionPrompt = """Available actions:
1. Vote - cast vote for a post
2. Mark - mark an answer as accepted
3. Give - give a badge to a poster
4. Add - add tags to a post
5. Edit - edit the title and/or the body of the post

Choose an action (number or text): 
"""

editActionPrompt = """Available actions:
1. Edit both title and body of the post
2. Edit the title only
3. Edit the body only

Choose an action (number):
"""


def main():
    db.setup()
    while (True):
        isRegistered = input("Are you registered as a user?(Y/N) ").lower()
        if isRegistered == "y":
            # user name, password
            uid = input("uid: ")
            password = getpass.getpass("password: ")
            loginSuccess = db.login(uid, password)
            if (loginSuccess):
                print("Logged in")
            else:
                print("Uid or password is wrong")
        elif isRegistered == "n":
            uid = input("uid: ")
            password = getpass.getpass("password: ")
            name = input("name: ")
            city = input("city: ")

            registerSuccess = db.register(uid, name, password, city)
            if (registerSuccess):
                print("Register success")
            else:
                print("Register fail")
        else:
            print("Invalid input, please choose T or F.")

        while (db.currentUser != None):
            action = input(options).lower()

            if (action == "post"):
                postQuestion()

            elif (action == "search"):
                keywords = input("Enter keyword(s) separate by space to search for posts: ")
                if (len(keywords) == 0):
                    print("Keyword must have at least a character")
                else:
                    result = db.searchPost(keywords, 0) # searching by keyword
                    if (len(result) == 0):
                        print(f"No posts have the entered keyword(s): {keywords}")
                        continue

                    headers = [("pid", "title", "body", "voteCnt", "ansCnt", "matchCnt")]
                    db.printTable(headers + result)

                    option = input("Select a post or enter 'more' to see more matches: ")
                    if (option.lower() == 'select'):
                        postID = input("Select a post by entering post ID: ")
                        selectOption(postID, uid)
                    elif (option.lower() == 'more'):
                        result = db.searchPost(keywords, 5) # searching by keyword
                        db.printTable(headers + result)
                        choice = input('Do you want to select a post? Y/N ')
                        if (choice.lower() == 'y'):
                            postID = input("Select a post by entering post ID: ")
                            selectOption(postID, uid)
                        elif (choice.lower() == 'n'):
                            continue
                        else:
                            print("Invalid input, please choose one of the options above.")
            elif (action == "getall"):
                print(db.getAllPosts())
            elif (action == "logout"):
                db.logout()
                print("Logged out")
            else:
                print("Invalid input, please choose one of the options above.")
    db.close()    

def selectOption(postID, uid):
    isQuestion = db.getQuestion(postID) != None
    isAnswer = db.getAnswer(postID) != None
    isPrivileged = db.currentUser.isPrivileged
    actionPrompt = ""

    if (isQuestion):
        print("\nThis post is a question.")
        if (isPrivileged): actionPrompt = privilegedQuestionActionPrompt
        else: action = ordinaryQuestionActionPrompt
    elif (isAnswer):
        print("\nThis post is an answer.")
        if (isPrivileged): actionPrompt = privilegedAnswerActionPrompt
        else: action = ordinaryAnswerActionPrompt
    else:
        print("\nPost does not exist.")
        
    action = input(actionPrompt).lower()
    if (action == 'answer' or action == '1') and isQuestion:
        title = input("Answer title: ")
        body = input("Answer body: ")
        db.postAnswer(postID, title, body)
    elif ((action == 'vote' or action == '1') and isAnswer) or ((action == 'vote' or action == '2') and isQuestion):
        if (not db.isVoted(postID, uid)):
            db.postVote(postID, uid)
        else: 
            print("Already voted")
    elif ((action == 'mark' or action == '2') and isPrivileged and isAnswer):
        answer = db.getAnswer(postID)
        qid = answer[1]
        acceptedAnswer = db.getAcceptedAnswer(qid)
        if (acceptedAnswer == None):
            db.markAnswer(qid, postID)
            print(f"SUCCESS - set {postID} as accepted answer for {qid}")
        elif (acceptedAnswer != None):
            userAccept = input("This question already has an accepted answer, do you want to overwrite it? (Y/N): ").lower()
            if (userAccept == 'y'):
                db.markAnswer(qid, postID)
        else:
            print("Unexpected error occurred")    
    elif ((action == 'give' or action == '3') and isPrivileged):
        bname = input("Badge name: ")
        btype = input("Badge type: ")
        db.giveBadge(bname, btype, postID)
    elif ((action == 'add' or action == '4') and isPrivileged):
        tags = input("Enter tags seperate by a single space : ")
        db.addTags(postID, tags.split())
        print(db.getTag(postID))
    elif ((action == 'edit' or action == '5') and isPrivileged):
        edit = input(editActionPrompt)
        if edit == '1':
            newTitle = input("Enter a new title: ")
            newBody = input("Enter a new body: ")
            db.editPost(postID, newTitle, newBody)
        elif edit == '2':
            newTitle = input("Enter a new title: ")
            db.editTitle(postID, newTitle)
        elif edit == '3':
            newBody = input ("Enter a new body: ")
            db.editBody(postID, newBody)
        else: print("Invalid action")
    else:
        print("Invalid action")


def postQuestion():
    title = input("Post title: ")
    body = input("Post body: ")
    db.postRecord(title, body)
    return


if __name__ == "__main__":
    main()