import requests
import configparser

class Interaction():
    
    def __init__(
        self,
        user_access_token,
        user_id,
        user_name,
        user_surname,
        user_link,
        user_age,
        user_sex,
        user_city,
        version = '5.131'
        ):
        self.UAT = user_access_token
        self.UID = user_id
        self.UN = user_name
        self.USN = user_surname
        self.UL = user_link
        self.UA = user_age
        self.US = user_sex
        self.UC = user_city
        
    def func_1():
        get_user_info = 
        