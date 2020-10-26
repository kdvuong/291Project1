from Db import Db
from Program import Program
import constants
import getpass
import math

db = Db()
program = Program(db)

def main():
    db.setup()
    while (True):
        isRegistered = input("Are you registered as a user?(Y/N) ").lower()
        if isRegistered == "y":
            # user name, password
            program.login()
        elif isRegistered == "n":
            program.register()
        else:
            print("Invalid input, please choose T or F.")

        while (db.currentUser != None):
            action = input(constants.ACTION_OPTIONS).lower()

            if (action == "post"):
                program.postQuestion()

            elif (action == "search"):
                try:
                    currentPage = 1
                    keywords = input("Enter keyword(s) separate by space to search for posts: ")
                    print("")

                    headers = [("pid", "title", "body", "voteCnt", "ansCnt", "matchCnt")]

                    if (len(keywords) == 0):
                        raise Exception("Keyword must have at least a character")
                    
                    allResultCount = len(program.searchGetAll(keywords))

                    while (True):
                        result = program.searchPaginate(keywords, currentPage)
                        resultCount = len(result)
                        if (resultCount > 0):
                            print(f"SEARCH RESULT: Page {currentPage}/{math.ceil(allResultCount / 5)}") 
                            program.printTable(headers + result)

                        option = input(constants.SEARCH_SUCCESS_ACTION_PROMPT).lower()
                        print("")

                        if (option == 'next'):
                            if (resultCount < 5 or (resultCount + currentPage * 5 == allResultCount)):
                                print("ERROR: No availale next page. Please try again with another option.")
                            else: currentPage += 1
                        elif (option == "prev"):
                            if (currentPage == 0): print("ERROR: At page 1, can't go back. Please try again with another option.")
                            else: currentPage -= 1
                        elif (option == "back"):
                            break
                        else:
                            validPid = False
                            for row in result:
                                if (row[0] == option): 
                                    validPid = True
                                    break
                            try:
                                if (validPid):
                                    postAction = program.getPostAction(option)
                                    postAction(program, option)
                                    break
                                else:
                                    print(f"ERROR: PID {option} not in search result. Please try again with another option.")
                            except Exception as err:
                                print(err.args[0])
                                break
                except Exception as err:
                    print(err.args[0])
            elif (action == "getall"):
                print(db.getAllPosts())
            elif (action == "logout"):
                db.logout()
                print("Logged out")
            else:
                print("Invalid input, please choose one of the options above.")
    db.close() 

if __name__ == "__main__":
    main()