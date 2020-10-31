class InputProcessor:
    def getRegisterUid(self):
        uid = input("Enter uid: ")

        if (len(uid) > 4):
            raise Exception("Uid must be less than 5 characters")

        if (len(uid) == 0):
            raise Exception("Uid cannot be empty")

        return uid
