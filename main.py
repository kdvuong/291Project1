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
                print("Posting a question")
                postQuestion(db.currentUser)

            elif (action == "search"):
                print("Searching a post")
                keyword = input("Enter a keyword to search for posts:")
                if (len(keyword) == 0):
                    print("Keyword must have at least a character")
                else:
                    db.searchPost(keyword)
            elif (action == "answer"):
                print("Answering a question")
            elif (action == "vote"):
                print("Voting a post")
            elif (action == "logout"):
                db.logout()
            else:
                print("Invalid input, please choose one of the options above.")

    db.close()    

def postQuestion(poster):
    pid = db.generatePid()
    title = input("Post title: ")
    body = input("Post body: ")
    db.postRecord(pid, title, body, poster)
    return


if __name__ == "__main__":
    main()