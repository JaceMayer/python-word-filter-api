import re


# Filters a discord link from the text
class discordLinkFilter:
    def __init__(self):
        self.filter = re.compile("http://|https://discord\.gg/\w{4,}")

    def getMatchesInText(self, string):
        return self.filter.findall(string)
