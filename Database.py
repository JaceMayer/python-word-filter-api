from Settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    ForeignKey, Boolean, Float, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import time

# Create the SQL database engine and connection
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# User SQL model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    lname = Column(TEXT)
    fname = Column(TEXT)
    email = Column(String(500), unique=True, index=True)
    password = Column(TEXT)
    superUser = Column(Boolean, default=False)
    user_words = relationship("Words", back_populates="owner", cascade="all, delete-orphan")
    package = relationship("Purchases", back_populates="user", order_by='Purchases.id.desc()',
                           cascade="all, delete-orphan")
    filter_requests = relationship("Requests", back_populates="user", order_by='Requests.id.desc()',
                                   cascade="all, delete-orphan")


# Words SQL Model
class Words(Base):
    __tablename__ = "user_words"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(TEXT, index=False)
    type = Column(Integer, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="user_words")


# Packages SQL Model
class Packages(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True, index=True)
    duration = Column(Integer, index=False)
    messagePerHour = Column(Integer, index=False)
    defaultListOnly = Column(Boolean, index=False)
    cost = Column(Float, index=False)
    name = Column(TEXT, index=False)


# Purchases SQL Model
class Purchases(Base):
    __tablename__ = "user_purchases"
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id"))
    package = relationship("Packages")
    startDate = Column(DateTime, index=False, default=datetime.datetime.now)
    endDate = Column(DateTime, index=False)
    subscriptionId = Column(TEXT(100), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="package")


# API Requests SQL Model
class Requests(Base):
    __tablename__ = "user_requests"
    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(TEXT)
    output_text = Column(TEXT)
    filter_epoch = Column(Integer, default=int(time.time()))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="filter_requests")


Base.metadata.create_all(bind=engine)
