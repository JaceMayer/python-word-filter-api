import re


# Filters a plain word from text
class basicWordFilter:

    def getMatchesInText(self, string, blacklist):
        r = []
        for word in blacklist:
            pattern = r"\w*(?:%s)\w*|%s" % (word, word)
            if len(re.findall(pattern, string, re.IGNORECASE)) != 0:
                r.append(re.findall(pattern, string, re.IGNORECASE)[0])
        return r
