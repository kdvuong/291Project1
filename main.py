from Db import Db

db = Db()

def main():
    db.setup()
    print(db.getUsers())

if __name__ == "__main__":
    main()