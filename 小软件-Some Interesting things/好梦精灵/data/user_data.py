class UserData:
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_id, sleep_data):
        self.users[user_id] = sleep_data
    
    def get_user_data(self, user_id):
        return self.users.get(user_id, {})