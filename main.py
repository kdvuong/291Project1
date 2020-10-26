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
                print("Searching a post")
                keyword = input("Enter a keyword to search for posts:")
                if (len(keyword) == 0):
                    print("Keyword must have at least a character")
                else:
                    result = db.searchPost(keyword) # searching by keyword
                    postID = input("Select a post by entering post ID: ")
                    if (db.getQuestion(postID) != None):
                        print("This post is a question.")
                        action = input("You can answer(A) or vote(V) this question: A/V: ")
                        if (action.lower() == 'a'):
                            db.answerPost()
                        elif (action.lower() == 'v'):
                            db.votePost()
                    elif (db.getAnswer(postID) != None):# the post is an answer, user can only vote
                        action = input("This is a question. Do you want to vote it? Y/N: ")
                        if (action.lower() == 'y'):
                            db.votePost()
                    else: 
                        print("Post does not exist")
                               
            elif (action == "answer"):
                print("Answering a question")
            elif (action == "vote"):
                print("Voting a post")
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