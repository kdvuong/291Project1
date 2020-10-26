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

def main():
    db.setup()
    while (True):
        isRegistered = input("Are you registered as a user?(T/F) ").lower()
        if isRegistered == "t":
            # user name, password
            uid = input("uid: ")
            password = input("password: ")
            loginSuccess = db.login(uid, password)
            if (loginSuccess):
                print("Logged in")
            else:
                print("Uid or password is wrong")
        elif isRegistered == "f":
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
                        print("This post is a question.")
                        action = input("You can answer(A) or vote(V) this question: A/V: ").lower()
                        if (action == 'a'):
                            title = input("Answer title: ")
                            body = input("Answer body: ")
                            db.postAnswer(postID, title, body)
                        elif (action == 'v'):
                            if (not db.isVoted(postID, uid)):
                                db.postVote(postID, uid)
                            else:
                                print("You have voted this post already.")
                    elif (db.getAnswer(postID) != None): # the post is an answer, user can only vote
                        action = input("This is an answer. Do you want to vote it? Y/N: ")
                        if (action.lower() == 'y'):
                            if (not db.isVoted(postID, uid)):
                                db.postVote(postID, uid)
                            else:
                                print("You have voted this post already.")
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
    pid = db.generatePid()
    title = input("Post title: ")
    body = input("Post body: ")
    db.postRecord(pid, title, body)
    return


if __name__ == "__main__":
    main()