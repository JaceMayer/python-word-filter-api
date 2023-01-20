from Models import *
from Database import *
import PasswordUtils
from PaypalHandler import cancelSubscription
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta


# User Funcs
# Checks To see if the users package is in date with a grace of 2 hours
def checkPackageInDate(current_user):
    return current_user.package[0].endDate > (datetime.now() + timedelta(hours=2))


# Get a user by ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# Gets a user by their Email address
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Get Users between skip and limit
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


# Creates a User
def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, password=PasswordUtils.get_password_hash(user.password), fname=user.fname,
                   lname=user.lname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Deletes a user and cancel their package with paypal
def delete_user(db: Session, user: User):
    # cancelSubscription
    if checkPackageInDate(user):
        # User has a running subscription - end it
        if not cancelSubscription(user.package[0].subscriptionId):
            print("Error Cancelling user subscription")
    db.delete(user)
    db.commit()


# Cancels the users package with paypal
def cancelUserPackage(db: Session, user: User):
    if checkPackageInDate(user):
        if cancelSubscription(user.package[0].subscriptionId):
            user.package[0].subscriptionId = ""
            db.commit()
            db.refresh(user)
            return True
        return False
    return False


# Word Funcs
# Checks to see if the user can edit words
def checkWordEditsAllowed(current_user):
    if current_user.package is None or len(current_user.package) == 0:
        return False
    if current_user.package[0] is None:
        return False
    if current_user.package[0].package.defaultListOnly:
        return False
    return True


# Creates a word linked to the users account
def create_word(db: Session, current_user: User, word_data: WordCreate):
    word = Words(word=word_data.word,
                 type=word_data.type.value)
    word.owner = current_user
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


# Updates a word
def update_word(db: Session, word_id: int, word_data: WordCreate):
    word = db.query(Words).filter(Words.id == word_id).first()
    # Make it so the global list can only be manipulated directly
    if word.owner_id == 1:
        return word
    word.word = word_data.word
    word.type = word_data.type
    db.commit()
    db.refresh(word)
    return word


# Deletes a word
def delete_word(db: Session, id: int, userid: int):
    word = db.query(Words).filter(Words.id == id).first()
    if word.owner_id != userid:
        raise HTTPException(status_code=401,
                            detail="Word is not associated to the user!")
    db.delete(word)
    db.commit()


# Gets all words the user has access to
def get_user_words(db: Session, user):
    if len(user.package) != 0 and not user.package[0].package.defaultListOnly:
        return db.query(Words).filter(Words.owner_id == user.id).all()
    elif len(user.package) != 0 and user.package[0].package.defaultListOnly:
        return db.query(Words).filter(Words.owner_id == 1).all()
    else:
        return []


# Gets a single word by ID
def get_word(db: Session, wordid: int):
    return db.query(Words).filter(Words.id == wordid)


# Get users word paginated
def get_paginated_user_words(db: Session, user, offset: int, limit: int, type: int):
    if len(user.package) != 0 and not user.package[0].package.defaultListOnly:
        return db.query(Words).filter(Words.owner_id == user.id).filter(Words.type == type).offset(offset).limit(
            limit).all()
    elif len(user.package) != 0 and user.package[0].package.defaultListOnly:
        return db.query(Words).filter(Words.owner_id == 1).filter(Words.type == type).offset(offset).limit(limit).all()
    else:
        return []


# Packages
# Get all packages
def get_all_packages(db: Session):
    return db.query(Packages).all()


# Get a package by ID
def package_by_id(db: Session, package_id: int):
    return db.query(Packages).filter(Packages.id == package_id).first()


# Purchases

# Create a purchase for a user
def createPurchase(db: Session, purchase_data: CreatePurchase):
    user = get_user(db, purchase_data.user_id)
    purchase = Purchases(endDate=datetime.strptime(purchase_data.endDate, '%Y-%m-%d %H:%M:%S'),
                         subscriptionId=purchase_data.subscriptionId)
    purchase.user = user
    purchase.package = package_by_id(db, purchase_data.package_id)
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    if len(purchase.user.package) == 1:  # This is our first package
        # Lets add words from the global list
        words = db.query(Words).filter(Words.owner_id == 1).all()
        for word in words:
            newWord = Words(word=word.word, type=word.type)
            newWord.owner = user
            db.add(newWord)
            db.commit()
            db.refresh(newWord)
    return purchase


# Get The ammount of words the user has
def getAmountOfUserWords(db: Session, user, word_type):
    if len(user.package) != 0 and not user.package[0].package.defaultListOnly:
        return len(db.query(Words).filter(Words.owner_id == user.id).filter(Words.type == word_type).all())
    elif len(user.package) != 0 and user.package[0].package.defaultListOnly:
        return len(db.query(Words).filter(Words.owner_id == 1).filter(Words.type == word_type).all())
    else:
        return 0


# Get data about the current user
def get_current_user_data(db, user_data: User):
    r = {}
    r["User"] = {"email": user_data.email, "id": user_data.id}
    r["WordCount"] = {"Blacklist": getAmountOfUserWords(db, user_data, 0),
                      "Whitelist": getAmountOfUserWords(db, user_data, 1)}
    if user_data.package is None or len(user_data.package) == 0:
        r["CurrentPackage"] = None
    else:
        package = user_data.package[0].package
        r["CurrentPackage"] = {"id": package.id, "duration": package.duration, "messagePerHour": package.messagePerHour,
                               "defaultListOnly": package.defaultListOnly, "cost": package.cost, "name": package.name,
                               "endDate": user_data.package[0].endDate.strftime("%d/%m/%Y"),
                               "cancelable": user_data.package[0].subscriptionId != ""}
    return r
