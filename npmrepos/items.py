from scrapy import Item, Field

class NpmreposItem(Item):
    packageName = Field()
    packageUrl = Field()
    repoName = Field()
    repoUrl = Field()
    readMeUrl = Field()
    readMeText = Field()
    pass
