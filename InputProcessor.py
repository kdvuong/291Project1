import getpass
from constants import *

# Class to handle input
class InputProcessor:
    # Function to handle uid input
    def getUidInput(self):
        uid = input("Enter uid: ")

        if (len(uid) > 4):
            raise Exception("Uid must be less than 5 characters")

        if (len(uid) == 0):
            raise Exception("Uid cannot be empty")

        return uid
        
    # Function to handle password input
    def getPasswordInput(self):
        password = getpass.getpass("Enter password: ")
        if (len(password) == 0):
            raise Exception("Password cannot be empty")
        return password

    # Function to handle empty input
    def getNonEmptyInput(self, inputName, hint=""):
        formattedHint = ""
        if (len(hint) > 0):
            formattedHint = "(" + hint + ")"
        s = input(f"Enter {inputName.lower()}{formattedHint}: ")
        if (len(s) == 0):
            raise Exception(f"{inputName.capitalize()} cannot be empty")
        return s

    # Function to handle search action input
    def getSearchActionInput(self, noNext, noPrev):
        action = input(
            SEARCH_SUCCESS_ACTION_PROMPT
            .format(**{
                "next": NEXT_PAGE_PROMPT if not noNext else "",
                "prev": PREV_PAGE_PROMPT if not noPrev else ""
            })).lower()
        print("")
        if (action == "next" and noNext):
            raise Exception(
                "ERROR: No availale next page. Please try again with another option.")
        elif(action == "prev" and noPrev):
            raise Exception(
                "ERROR: At page 1, can't go back. Please try again with another option.")
        return action
