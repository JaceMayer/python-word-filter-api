from Models import *
from Utils import get_user, checkPackageInDate
from Database import *
from enum import Enum, IntEnum
import time
from fastapi.responses import JSONResponse
from datetime import datetime


# Logs a users filter request
def create_request(db, input_text, output_text, user):
    request = Requests(input_text=input_text,
                       output_text=output_text)
    request.user = user
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


# Checks that the users current package is valid and in date
class FilterType(IntEnum):
    NoneAllowed = 0
    FilterDefaultList = 1
    FilterOwnList = 2


def getFilterTypeAllowed(current_user):
    if current_user.package is None or len(current_user.package) == 0:
        return FilterType.NoneAllowed
    if current_user.package[0] is None:
        return FilterType.NoneAllowed
    if current_user.package[0].package.defaultListOnly:
        return FilterType.FilterDefaultList
    return FilterType.FilterOwnList


def checkUserHasMoreRequests(db, current_user):
    if current_user.package[0].package.messagePerHour == 0:
        return True
    Reqs = db.query(Requests).filter(Requests.user_id == current_user.id).filter(
        Requests.filter_epoch > int(time.time() - 3600)).all()
    return len(Reqs) < current_user.package[0].package.messagePerHour


# Import filter classes and instantiate them

from Filters.linkFilter import linkFilter
from Filters.emailFilter import emailFilter
from Filters.basicWordFilter import basicWordFilter
from Filters.randomCharFilter import randomCharFilter
from Filters.discordLinkFilter import discordLinkFilter

Link = linkFilter()
Email = emailFilter()
basicWord = basicWordFilter()
randChar = randomCharFilter()
discord = discordLinkFilter()


# Gets word Lists for the user
def getListsForUser(db, user_id=-1, user=None):
    if user_id != -1:
        user = get_user(db, user_id)
    blacklist = []
    whitelist = []
    for word in user.user_words:
        if word.type == 0:
            blacklist.append(word.word)
        elif word.type == 1:
            whitelist.append(word.word)
    return [blacklist, whitelist]


# Filter Package for a user
def FilterText(db, current_user, filter_data):
    FilteringType = getFilterTypeAllowed(current_user)
    if FilteringType == FilterType.NoneAllowed:
        return JSONResponse(status_code=401, content={"message": "You do not have an active package on your account, "
                                                                 "please purchase one and try again."})
    if not checkPackageInDate(current_user):
        return JSONResponse(status_code=401, content={"message": "Your package has expired and did not renew "
                                                                 "please purchase one and try again."})
    if not checkUserHasMoreRequests(db, current_user):
        return JSONResponse(status_code=401, content={"message": "You have used all your filter requests for this hour "
                                                                 "please wait and try again."})
    Matches = []
    if filter_data.filter_urls:
        Matches += Link.getMatchesInText(filter_data.text)
    if filter_data.filter_emails:
        Matches += Email.getMatchesInText(filter_data.text)
    if filter_data.filter_discordInvite:
        Matches += discord.getMatchesInText(filter_data.text)
    if filter_data.filter_words:
        if FilteringType == FilterType.FilterOwnList:
            blacklist, whitelist = getListsForUser(db, user=current_user)
        else:
            blacklist, whitelist = getListsForUser(db, user_id=1)
        Matches += basicWord.getMatchesInText(filter_data.text, blacklist)
        Matches += randChar.getMatchesInText(filter_data.text, blacklist)
        for Match in Matches:
            if Match in whitelist:
                Matches.remove(Match)
    output = filter_data.text
    for match in Matches:
        output = output.replace(match, "*" * len(match))
    create_request(db, filter_data.text, output, current_user)
    return {"input_text": filter_data.text, "matches": Matches, "output_text": output}
