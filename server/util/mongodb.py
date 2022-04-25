from pymongo import MongoClient
import sys

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
    
    name = {"list_name": list_name}
    item = {"item_name": item_name,
            "quantity": int(quantity)}

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


def create(user_dict): 
    user_dict['id'] = get_next_id()
    users_collection.insert_one(user_dict)
    return user_dict

def get_next_id():
    id_object = users_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        users_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        users_id_collection.insert_one({'last_id': 1})
        return 1 


def list_all():
    all_users = users_collection.find({}, {"_id": 0})
    return list(all_users)

    
def retrieve(id):
    retrieved_user = users_collection.find({"id": id}, {"_id": 0})
    return list(retrieved_user)


def update(id, email, username):
    if len(retrieve(id)) == 0:
        return False
    users_collection.update_one({"id": id}, {"$set":{"email":email, "username":username}})
    return True

    
def delete(id):
    if len(retrieve(id)) == 0:
        return False
    users_collection.delete_one({"id": id})
    return True

# MongoDB for Comments and picture file location
def insert_comment(comment):
    """
    Insert comment = {"comment": "comment_message", 
                      "img_name": "image1.jpg"
                      "xsrf_token": "xsrf_token"
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


