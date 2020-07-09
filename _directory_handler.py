import os

class D_Handler():

    def __init__(self):
        pass
    
    def is_New_User(self,base_dir,user_dir):
        """ is new user?
        """
        if user_dir not in os.listdir(base_dir):
            return True

        return False

    def make_User_Space(self,user_dir):
        """ make user directory on Server
        """
        try:
            os.makedirs(user_dir)
            os.makedirs(user_dir+'\\metadata')

        except:
            print('User already exists')
            pass

    def is_New_Project(self,user_dir,project_dir):
        """ is new project?
        """
        if project_dir not in os.listdir(user_dir):
            return True
        
        return False

    def make_Project_Space(self,project_dir):
        """ make project directory on Server
        """
        try:
            os.makedirs(project_dir)
        except:
            print('Project already exists')
            pass

    def is_New_Label(self,project_dir,label_dir):
        """ is new label?
        """

        if label_dir not in os.listdir(project_dir):
            return True
        
        return False

    def make_Label_Space(self,label_dir):
        """ make label directory on server
        """
        try:
            os.makedirs(label_dir)
        except:
            print('Label already exists')
            pass