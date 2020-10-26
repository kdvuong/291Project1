from Db import Db

db = Db()

options = """-----------------------------------
Choose the following option:
-----------------------------------
POST (post a question)
SEARCH (search for a post)
ANSWER (post answer to a question)
VOTE (vote a post)
LOGOUT (log out)
------------------------------------
What do you want to do? """

ordinaryActionPrompt = """Available actions:
1. Answer - post answer to a question
2. Vote - cast vote for a post

Choose an action (number or text): 
"""

privilegedActionPrompt = """Available actions:
1. Answer - post answer to a question
2. Vote - cast vote for a post
3. Mark - mark an answer as accepted
4. Give - give a badge to a poster
5. Add - add tags to a post
6. Edit - edit the title and/or the body of the post

Choose an action (number or text): 
"""


def main():
    db.setup()
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
                    if (db.getQuestion(postID) != None):
                        print("\nThis post is a question.")
                        action = ""
                        isPrivileged = db.currentUser.isPrivileged
                        if (isPrivileged):
                            action = input(privilegedActionPrompt).lower()
                        else:
                            action = input(ordinaryActionPrompt).lower()

                        if (action == 'answer' or action == '1'):
                            title = input("Answer title: ")
                            body = input("Answer body: ")
                            db.postAnswer(postID, title, body)
                        elif (action == 'vote' or action == '2'):
                            if (not db.isVoted(postID, uid)):
                                db.postVote(postID, uid)
                            else: 
                                print("Already voted")
                        elif ((action == 'mark' or action == '3') and isPrivileged):
                            db.answerPost()
                        elif ((action == 'give' or action == '4') and isPrivileged):
                            db.votePost()
                        elif ((action == 'add' or action == '5') and isPrivileged):
                            db.addTag()
                        elif ((action == 'edit' or action == '6') and isPrivileged):
                            db.votePost()
                        else:
                            print("Invalid action")

                    elif (db.getAnswer(postID) != None):# the post is an answer, user can only vote
                        action = input("This is an answer. Do you want to vote it? Y/N: ")
                        if (action.lower() == 'y'):
                            db.postVote(postID, uid)
                    else:
                        print("Post does not exist")
                               
            # elif (action == "answer"):
            #     print("Answering a question")
            # elif (action == "vote"):
            #     print("Voting a post")
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