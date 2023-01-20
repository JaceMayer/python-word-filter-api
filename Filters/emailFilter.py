import re


# Filters email addresses from the text
class emailFilter:
    def __init__(self):
        self.filter = re.compile("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$")

    def getMatchesInText(self, string):
        r = []
        for word in string.split(" "):
            if len(self.filter.findall(word)) == 0:
                continue
            r.append(self.filter.findall(word)[0])
        return r
