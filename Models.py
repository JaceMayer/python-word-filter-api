from pydantic import BaseModel, root_validator
from pydantic import EmailStr, SecretStr
from typing import Optional
from enum import Enum, IntEnum
from Database import User, Purchases, Words, Packages, SessionLocal


# Base User Models

class UserBase(BaseModel):
    email: str


# Model that stores the information we sent to create a user
class UserCreate(UserBase):
    lname: str
    fname: str
    password: str


# Model the user sends to login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Model that is sent to show user if registration was successful or not
class RegisterStatus(BaseModel):
    success: bool
    error_text: str


# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Word Models

# WordType Enum
class WordType(str, Enum):
    Blacklist = 0
    Whitelist = 1


# Model to create a word
class WordCreate(BaseModel):
    word: str
    type: WordType = WordType.Blacklist


# Model to Update a word
class WordUpdate(WordCreate):
    id: int


# Package Models
# Package Model
class Package(BaseModel):
    id: int
    duration: int
    messagePerHour: int
    defaultListOnly: bool
    cost: float
    name: str


# Out of package error model
class OutOfPackageError(BaseModel):
    message: str


# Purchase Models

# Model to create a purchase
class CreatePurchase(BaseModel):
    package_id: int
    startDate: str
    endDate: str
    user_id: int
    subscriptionId: str


# Filtering

# Model to request filtering
class FilterRequest(BaseModel):
    text: str
    filter_words = True
    filter_urls = False
    filter_emails = False
    filter_discordInvite = False


# Response Model for filter output
class FilterOutput(BaseModel):
    input_text: str
    matches: list
    output_text: str
