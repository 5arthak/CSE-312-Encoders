from pymongo import MongoClient
import bcrypt
from hashlib import sha256

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]

# MongoDB collections
users_id_collection = db["id"]
users_collection = db["users"]
comments_collection = db["comments"]
chats_collection = db["chats"]


grocery_items_id_collection = db["grocery_id"]
grocery_items_collection = db["grocery_items"]

def add_item(list_name: str, item_name: str, quantity: str):
    quantity_num = int(quantity) if quantity != "" else 0
    name = {"list_name": list_name}
    item = {"item_name": item_name,
            "quantity": quantity_num}
    # item["id"] = get_next_groceryid(list_name)
    grocery_list = grocery_items_collection.find_one(name)
    if grocery_list:
        grocery_list["items"].append(item)
        grocery_items_collection.update_one(name, {'$set': {"items": grocery_list["items"]}})
    else:
        name["items"] = [item]
        grocery_items_collection.insert_one(name)
    return grocery_items_collection.find_one(name)


def get_next_groceryid(list_name: str):
    id_object = users_id_collection.find_one({"name": list_name})
    if id_object:
        next_id = int(id_object["last_id"]) + 1
        users_id_collection.update_one({"name": list_name}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        users_id_collection.insert_one({"name": list_name, "last_id": 1})
        return 1


# MongoDB for Comments and picture file location
def insert_comment(comment):
    """
    Insert comment = {"comment": "comment_message", 
                      "img_name": "image1.jpg"
                      } to collection
    """ 
    comments_collection.insert_one(comment)
    return comment

def list_all_comments():
    all_comments = comments_collection.find({}, {"_id": 0})
    return list(all_comments)

# MongoDB for chat comments featuring username
def insert_chat(chat):
    """
    Insert comment = {"username": "username", 
                      "comment": "hello world"
                      } to collection
    """ 
    chats_collection.insert_one(chat)
    # return chat

def list_all_chats():
    all_chats = chats_collection.find({}, {"_id": 0})
    return list(all_chats)


# MongoDB for adding user after registration 
def insert_new_user(user_info):
    """
    Insert user_info = {"email": "address", 
                        "pwd": "hello world"
                    } to collection
    """ 
    find_user_info = users_collection.find({"email": user_info["email"]}, {"_id": 0, "pwd": 0})
    find_user_info = list(find_user_info)
    if len((list(find_user_info))) == 0:
        users_collection.insert_one(user_info)
        return True
    return False


# MongoDB authenticating user after login 
def auth_user(user_info):
    """
    Find email in db and check if the inputed password with 
    Insert user_info = {"email": "email", 
                        "pwd": "hello world"
                        "auth_token": "token"
                    } to collection
    """ 
    find_user_info = users_collection.find({"email": user_info["email"]}, {"_id": 0})
    pwd = list(find_user_info)
    if bcrypt.checkpw(bytes(user_info["pwd"], 'utf-8'), pwd[0]["pwd"]):
        # Must hash the generated auth_token and then store in db
        hash_token = sha256(str(user_info["auth_token"]).encode()).hexdigest()
        users_collection.update_one({"email": user_info["email"]}, {"$set": { 'auth_token': hash_token}})
        return True
    return False


def user_token(token):
    # Return user info from auth token
    hash_token = sha256(str(token).encode()).hexdigest()
    user_info = users_collection.find({"auth_token": hash_token}, {"_id": 0})
    user_info = list(user_info)
    if len(user_info) == 1:
        return user_info
    return []