from Db import Db

db = Db()

def main():
    db.setup()
    print(db.getUsers())
    while (True):
        isRegistered = input("Are you registered as a user?(T/F) ")
        if isRegistered.lower() == "t":
            # user name, password
            uid = input("uid: ")
            password = input("password: ")
            loginSuccess = db.login(uid, password)
            if (loginSuccess):
                print("Logged in")
                break
            else:
                print("Uid or password is wrong")
        elif isRegistered.lower() == "f":
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
            print("Invalid input, please choose T or F")

    db.close()    


if __name__ == "__main__":
    main()