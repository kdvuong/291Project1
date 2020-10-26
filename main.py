from Db import Db

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


def main():
    db.setup()
    c = db.conn.cursor()
    # db.deleteBadges()
    print(db.getBadges())
    print(db.getUbadges())
    # c.execute(""" INSERT INTO privileged VALUES
    #                 ('kang')
    #             """)
    # db.conn.commit()
    while (True):
        isRegistered = input("Are you registered as a user?(Y/N) ").lower()
        if isRegistered == "y":
            # user name, password
            uid = input("uid: ")
            password = input("password: ")
            loginSuccess = db.login(uid, password)
            if (loginSuccess):
                print("Logged in")
            else:
                print("Uid or password is wrong")
        elif isRegistered == "n":
            uid = input("uid: ")
            password = input("password: ")
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
                    result = db.searchPost(keywords) # searching by keyword
                    if (len(result) == 0):
                        print(f"No posts have the entered keyword(s): {keywords}")
                        continue

                    headers = [("pid", "title", "body", "voteCnt", "ansCnt", "matchCnt")]
                    db.printTable(headers + result)

                    postID = input("Select a post by entering post ID: ")
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
                        continue

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
                            bname = input("Give badge: ")
                            btype = input("Badge type: ")
                            db.giveBadge(bname, btype, postID)
                    elif ((action == 'add' or action == '4') and isPrivileged):
                        db.votePost()
                    elif ((action == 'edit' or action == '5') and isPrivileged):
                        db.votePost()
                    else:
                        print("Invalid action")
            elif (action == "getall"):
                print(db.getAllPosts())
            elif (action == "logout"):
                db.logout()
            else:
                print("Invalid input, please choose one of the options above.")

    db.close()    

def postQuestion():
    title = input("Post title: ")
    body = input("Post body: ")
    db.postRecord(title, body)
    return


if __name__ == "__main__":
    main()