from Db import Db
from Program import Program
from postActionConfig import POST_ACTIONS
import constants
import getpass

program = Program(Db(), POST_ACTIONS)


def main():
    program.start()
    while (True):
        startAction = input(constants.START_ACTION_PROMPT).lower()
        if (startAction == "login" or startAction == "1"):
            # user name, password
            program.login()
        elif (startAction == "register" or startAction == "2"):
            program.register()
        elif (startAction == "exit" or startAction == "3"):
            break
        else:
            print("Invalid input, please try again.")

        while (program.currentUser != None):
            action = input(constants.ACTION_OPTIONS).lower()

            if (action == "post" or action == "1"):
                program.postQuestion()
            elif (action == "search" or action == "2"):
                program.search()
            elif (action == "logout" or action == "3"):
                program.logout()
            else:
                print("Invalid input, please choose one of the options above.")
    program.end()


if __name__ == "__main__":
    main()
