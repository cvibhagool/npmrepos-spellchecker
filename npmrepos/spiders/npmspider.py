from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from npmrepos.items import NpmreposItem
from scrapy.http import Request
from json import dumps
from BeautifulSoup import BeautifulSoup

class MySpider(BaseSpider):
  #Spider name
  name = "npmrepo"
  #Only allow npmjs and raw.githubusercontent
  allowed_domains = ["npmjs.com", "raw.githubusercontent.com"]
  #Search through first 250 repos in step of 36
  start_urls = ["https://www.npmjs.com/browse/depended?offset=%s" % page for page in range(0,250,36)]

  def __init__(self):
    #Delay 
    self.download_delay = 4

  #Parse the response of each npmjs paginated page
  def parse(self, response):
    sel = Selector(response)
    #Select links to each packages' individual page on npmjs
    packages = sel.xpath('//*[@class="package-details"]/h3/a/@href')
    for package in packages:
      item = NpmreposItem()
      #Get the url to the individual page on npmjs
      packageUrl = 'https://www.npmjs.com' + package.extract()
      #Get the page name
      packageName = package.extract().split('/')[2]
      #Store the url and name
      item['packageUrl'] = packageUrl
      item['packageName'] = packageName
      #Go to the individual page name
      yield Request(url = packageUrl, callback = self.parse_package,meta={'item':item})

  #Parse the response of each package individual page
  def parse_package(self, response):
    sel = Selector(response)
    #Get the github repo url
    repoUrl = sel.xpath('//ul[@class="box"][1]//li[3]//a/@href').extract()[0]
    item = NpmreposItem(response.request.meta["item"])
    item['repoUrl'] = repoUrl
    #Grab the username
    gitUsername = repoUrl.split('/')[3]
    #Grab the repo url
    gitReponame = repoUrl.split('/')[4]
    #Construct the url for the ReadMe.md at the root directory of the project
    readMeUrl = 'https://raw.githubusercontent.com/' + gitUsername + '/' + gitReponame + '/master/README.md'
    #Store the url
    item['readMeUrl'] = readMeUrl
    #Request the raw ReadMe.md 
    yield Request(url = readMeUrl, callback = self.parse_repo,meta={'item':item})

  #Parse the response of raw ReadMe.md
  def parse_repo(self, response):
    #If the ReadMe.md doesn't exist, then skip the item, and no data is stored
    if response.status == 404:
      return
    item = NpmreposItem(response.request.meta["item"])
    #Store the raw response body
    item['readMeText'] = response.body
    #Yield item, ending the request chain
    yield item




