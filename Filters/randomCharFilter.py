import re


# Filters words where letters have been repleaced with x character
class randomCharFilter:

    def getMatchesInText(self, string, blacklist):
        r = []
        for word in blacklist:
            for i in range(len(word)):
                wordcp = list(word)
                wordcp[i] = "(?:[^a-zA-Z0-9_\s]|\d)"
                newword = ''.join(wordcp)
                pattern = r"%s" % newword
                if len(re.findall(pattern, string, re.IGNORECASE)) != 0:
                    r.append(re.findall(pattern, string, re.IGNORECASE)[0])
        return r
