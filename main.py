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
        isLoggedIn = False
        if isRegistered == "t":
            # user name, password
            uid = input("uid: ")
            password = input("password: ")
            loginSuccess = db.login(uid, password)
            if (loginSuccess):
                print("Logged in")
                isLoggedIn = True
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

        while (isLoggedIn):
            action = input(options).lower()

            if (action == "post"):
                print("Posting a question")
                pid = db.generatePid()
                title = input("Post title: ")
                body = input("Post body: ")
                db.postRecord(pid, title, body, uid)
            elif (action == "search"):
                print("Searching a post")
            elif (action == "answer"):
                print("Answering a question")
            elif (action == "vote"):
                print("Voting a post")
            elif (action == "logout"):
                isLoggedIn = False
                break
            else:
                print("Invalid input, please choose one of the options above.")

    db.close()    


if __name__ == "__main__":
    main()