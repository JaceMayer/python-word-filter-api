from Database import *
from Settings import app_title, app_desc, app_ver, ACCESS_TOKEN_EXPIRE_MINUTES, API_PREFIX, SHOW_SECURED_ENDPOINTS
from Models import *
from Utils import *
from Filtering import *
import JWebToken
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from fastapi.responses import JSONResponse


# Method to get a database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# oauth scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=API_PREFIX + "token")


# Gets the current user from their token
def get_current_user(db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)):
    return JWebToken.decode_access_token(db, token)


# Initiate FastAPI
app = FastAPI(
    title=app_title,
    description=app_desc,
    version=app_ver)


# User Endpoints
# Endpoint to allow user to register
@app.post(API_PREFIX + "users", response_model=RegisterStatus, include_in_schema=SHOW_SECURED_ENDPOINTS)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """add new user"""
    user = get_user_by_email(db, user_data.email)
    if user:
        return {"success": False, "error_text": "A User with that email address already exists."}
    signedup_user = create_user(db, user_data)
    return {"success": signedup_user is not None, "error_text": ""}


# Gets the current users information
@app.get(API_PREFIX + "@me")
def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content=get_current_user_data(db, current_user))


# Deleted current user
@app.delete(API_PREFIX + "@me", include_in_schema=SHOW_SECURED_ENDPOINTS)
def delete_user_by_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delete_user(db, current_user)
    return JSONResponse(status_code=200, content={"Message": "OK"})


# Cancel users Package
@app.delete(API_PREFIX + "@me/package", include_in_schema=SHOW_SECURED_ENDPOINTS)
def cancel_package_by_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content={"Success": cancelUserPackage(db, current_user)})


# Logs in user by Access Token
@app.post(API_PREFIX + "token", response_model=Token)
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    user = PasswordUtils.authenticate_user(get_user_by_email(db, form_data.email), form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = JWebToken.create_access_token(data={"sub": user.email},
                                                 expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# Turns Object into dictionary
def objectToDict(obj, values):
    r = {}
    for value in values:
        if value == "type":
            if obj.__dict__[value] == 0:
                r[value] = WordType.Blacklist
            else:
                r[value] = WordType.Whitelist
        else:
            r[value] = obj.__dict__[value]
    return r


# Turns many objects into a dictionary
def manyObjectsToDict(objs, values):
    r = []
    for obj in objs:
        r.append(objectToDict(obj, values))
    return r


# Word Endpoints
# Gets the users own words
@app.get(API_PREFIX + "@me/words", response_model=list[WordUpdate])
def get_own_words(current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db),
                  ):
    words = get_user_words(db, current_user)
    return manyObjectsToDict(words, ["id", "word", "type"])


# Gets users words of type, between offset and limit
@app.get(API_PREFIX + "@me/words/{word_type}/{offset}/{limit}", response_model=list[WordUpdate])
def get_own_words_paginated(word_type: int,
                            offset: int,
                            limit: int,
                            current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    words = get_paginated_user_words(db, current_user, offset, limit, word_type)
    return manyObjectsToDict(words, ["id", "word", "type"])


# Adds a word for user
@app.post(API_PREFIX + "@me/words", response_model=WordCreate, responses={401: {"model": OutOfPackageError}})
def add_a_word(word_data: WordCreate,
               current_user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    if not checkWordEditsAllowed(current_user):
        return JSONResponse(status_code=401, content={"message": "Editing the blocked word list is currently not "
                                                                 "allowed on your package."})
    word = create_word(db, current_user, word_data)
    return objectToDict(word, ["id", "word", "type"])


# Updates a word for the user
@app.put(API_PREFIX + "@me/words/{word_id}", response_model=WordCreate, responses={401: {"model": OutOfPackageError}})
def update_a_word(word_id: int,
                  word_data: WordCreate,
                  current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    if not checkWordEditsAllowed(current_user):
        return JSONResponse(status_code=401, content={"message": "Editing the blocked word list is currently not "
                                                                 "allowed on your package."})
    updated_word = update_word(db, word_id, word_data)
    return objectToDict(updated_word, ["word", "type"])


# Deletes the users word
@app.delete(API_PREFIX + "@me/words/{word_id}", responses={401: {"model": OutOfPackageError}})
def delete_a_word(word_id: int,
                  current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    if not checkWordEditsAllowed(current_user):
        return JSONResponse(status_code=401, content={"message": "Editing the blocked word list is currently not "
                                                                 "allowed on your package."})
    delete_word(db, word_id, current_user.id)
    return {"detail": "Word Deleted"}


# List All Packages
@app.get(API_PREFIX + "packages/all", response_model=list[Package])
def get_packages(db: Session = Depends(get_db)):
    packages = get_all_packages(db)
    return manyObjectsToDict(packages, ["id", "duration", "messagePerHour", "defaultListOnly", "cost", "name"])


# Get package by id
@app.get(API_PREFIX + "packages/{package_id}", response_model=Package)
def get_package(package_id: int, db: Session = Depends(get_db)):
    package = package_by_id(db, package_id)
    return objectToDict(package, ["id", "duration", "messagePerHour", "defaultListOnly", "cost", "name"])


# Add purchase for user (PayPal IPN)
@app.post(API_PREFIX + "purchasing/createpurchase", include_in_schema=SHOW_SECURED_ENDPOINTS)
def addPurchase(purchase_data: CreatePurchase,
                db: Session = Depends(get_db)):  # , current_user: User = Depends(get_current_user)):
    createPurchase(db, purchase_data)
    return JSONResponse(status_code=200, content={"message": "OK"})


# Filter text for user
@app.post(API_PREFIX + "@me/filter", response_model=FilterOutput, responses={401: {"model": OutOfPackageError}})
def filter_text(filter_data: FilterRequest,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return FilterText(db, current_user, filter_data)


if __name__ == "__main__":
    # Start Uvicorn server
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
