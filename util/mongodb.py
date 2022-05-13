from pymongo import MongoClient
import bcrypt
from hashlib import sha256
# import sys

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]

# MongoDB collections
users_id_collection = db["id"]
users_collection = db["users"]
deals_collection = db["deals"]
chats_collection = db["chats"]

list_name_collection = db["grocery_items"]
grocery_lists_collection = db["grocery_lists"]

users_messages = db["messages_of_user"]

def add_message(username: str, chat_message: str, sent_by: str):
    ''' add a message to username's chat db'''
    msg_dict = {"message": chat_message, "from": sent_by}
    get_user = users_messages.find_one({"username": username}, {"_id": 0})
    # print("db add msg:", msg_dict, get_user, flush=True)
    if not get_user:
        users_messages.insert_one({"username": username, "messages": [msg_dict]})
    else:
        user_msgs = get_user.get("messages", [])
        user_msgs.append(msg_dict)
        # print("updated", user_msgs, flush=True)
        users_messages.update_one({"username": username}, {'$set': {"messages": user_msgs}})
    return

def get_user_messages(username: str):
    '''gets messages of the given username'''
    # print("fetching user msgs from db of :", username, flush=True)
    get_user = users_messages.find_one({"username": username}, {"_id": 0})
    if get_user:
        user_msgs = get_user.get("messages", [])
        return [user_msgs]
    return []


# MongoDB for chat comments featuring username
def insert_chat(chat):
    """
    Insert comment = {"username": "username", 
                      "comment": "hello world"
                      } to collection
    """ 
    chats_collection.insert_one(chat)

def list_all_chats():
    """ return [{"username": "username", "comment": "hello world"}, ] """
    all_chats = chats_collection.find({}, {"_id": 0})
    return list(all_chats)

# List Stuff, creating list, checking if its a list and getting all the lists names
def create_new_list(list_name):
    # Create new list with list name and an empty items list
    find_list = list_name_collection.find({"list_name": list_name})
    find_list = list(find_list)
    if len((find_list)) == 0:
        list_name_collection.insert_one({"list_name": list_name})
        return True
    return False

def not_a_list(list_name):
    # Returns true if list_name not in database
    output_list = list_name_collection.find({"list_name": list_name}, {"_id": 0})
    output_list = list(output_list)
    if len(output_list) != 0:
        return False
    return True

def get_list_names():
    return list(list_name_collection.find({}, {"_id": 0, "list_name": 1}))


# Insert new grocery list with list name
def insert_grocery_items(item):
    """
    item = {list_name: name, item_name: name, quantity: 00}
    adds to the items of list_name
    """
    grocery_lists_collection.insert_one(item)

def retrieve_items(list_name):
    """
    Return [{'item_name': '', 'quantity': ''}, ]
    """
    try:
        grocery_items = grocery_lists_collection.find({"list_name": list_name}, {"_id": 0, "list_name": 0})                
        grocery_items = list(grocery_items)
        return grocery_items
    except:
        return []



# MongoDB for uploading images and details of a deal
def insert_deal(deal):
    """
    Insert comment = {"comment": "comment_message", 
                      "img_name": "image1.jpg"
                      } to collection
    """ 
    deals_collection.insert_one(deal)
    return deal

def list_all_deals():
    all_deals = deals_collection.find({}, {"_id": 0})
    return list(all_deals)



# Insert registering user 
def insert_new_user(user_info):
    """
    Insert user_info = {"email": "address", 
                        "pwd": "hello world",
                        "pronouns": "",
                    } to collection
    """ 
    find_user_info = users_collection.find({"email": user_info["email"]}, {"_id": 0, "pwd": 0})
    find_user_info = list(find_user_info)
    if len((list(find_user_info))) == 0:
        users_collection.insert_one(user_info)
        return True
    return False


# Authenticating user after login 
def auth_user_login(user_info):
    """
    Find email in db and check if the inputed pwd equal hashed pwd
    If so reset auth_toke, status = True, tcp socket conn 
    Insert user_info = {"email": "email", 
                        "pwd": "hello world",
                        "auth_token": "token",
                        "status": True,
                    } to collection
    """ 
    find_user_info = users_collection.find({"email": user_info["email"]}, {"_id": 0})
    pwd = list(find_user_info)
    if len(pwd) == 0:
        return False
    if bcrypt.checkpw(bytes(user_info["pwd"], 'utf-8'), pwd[0]["pwd"]):
        # hash the generated auth_token and then store in db
        hash_token = sha256(str(user_info["auth_token"]).encode()).hexdigest()
        users_collection.update_one({"email": user_info["email"]}, 
                                    {"$set": { 'auth_token': hash_token, 'status': True}})
        return True
    return False

def user_logoff(email):
    users_collection.update_one({"email": email}, {"$set": { 'status': False}})

def get_online_users():
    find_user_info = users_collection.find({"status": True}, {"_id": 0, 'email': 1, "pronouns": 1})
    return list(find_user_info)

def update_pronouns(email, pronouns):
    users_collection.update_one({"email": email}, {"$set": { 'pronouns': pronouns}})

def user_token(token):
    # Return user info from auth token
    hash_token = sha256(str(token).encode()).hexdigest()
    user_info = users_collection.find({"auth_token": hash_token}, {"_id": 0})
    user_info = list(user_info)
    if len(user_info) == 1:
        return user_info
    return []

def get_email_from_token(token):
    # Return user info from auth token
    hash_token = sha256(str(token).encode()).hexdigest()
    user_info = users_collection.find({"auth_token": hash_token}, {"_id": 0, 'email': 1})
    user_info = list(user_info)
    if len(user_info) == 1:
        return user_info
    return None
