from database import UserManager


class User:
    def __init__(self, user_manager):
        self.user_manager = user_manager
        self.name = ''
        self.email = ''
        self.password = ''
        #add other key variables that we want to look for? (risk appetite, bookmarked sticks etc?)

    def create_account(self, name, email, password):
        print("Hi! We're hapy that you're creating an account with us. Please fill in the following information please.")
        self.name = name
        self.email = email
        self.password = password
        if self.user_manager.add_user(name=self.name, password=self.password, email=self.email):
            print("Your account has been successfully created!")
            return False
        else:
            print("You already have an account with us, please login instead")
            return True

    def login(self, email, password):
        if self.user_manager.email_check(email) == 0:
            return False
        else:
            if self.check_password(email, password):
                self.name = self.user_manager.get_name(email)
                self.email = email
                self.password = password
                return True
            else:
                print('You have entered the wrong password :(')
                return 'wrong password'

    def check_password(self, email, password):
        database_password = self.user_manager.get_password(email)
        if password == database_password:
            return True
        else:
            return False

    def change_password(self, email, new_password):
        self.user_manager.change_password(email, new_password)
        print("You have successfully changed your password! Please login again with your new password thanks")
        return True
