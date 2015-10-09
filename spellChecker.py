from enchant import Dict
import re
import csv
import json
from markdown import markdown
from BeautifulSoup import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib import style

#Import repo data from saved json file
with open('reposReadMe.json') as items:
    data = json.load(items)
#Create a spell checker
d = Dict("en_US")
#Create a regex for filtering out special characters
regex = re.compile('[^a-zA-Z]')

def filterWord(word):
  upperCaseCount = sum(1 for c in word if c.isupper())
  #If the word has more than one uppercase character, it's probably a variable
  if upperCaseCount > 1:
    return False
  #If the word has only one uppercase, and it's not the first character, then it's probably a variable
  if upperCaseCount == 1:
    if word[0].upper() != word[0]:
      return False
  #If the word is two characters long or fewer, then it's probably a file extension or a variable
  if len(word) < 3:
    return False
  return True

#Output will be a dictionary where the key is a mispelled word and value contains the word usage count and packages that used the word
#{MispelledWord1 : {freq : k, packages : ['package1','package2']}, MispelledWord2 : {....}, }
output = {}
#Go over each repo
for repo in data:
  #Get package name
  packageName = str(repo['packageName'])
  #Get the raw readme body
  rawBody = repo['readMeText']
  #Convert raw markdown to html
  html = markdown(rawBody)
  soup = BeautifulSoup(html)
  #Remove code tags and its contents from the text
  for tag in soup.findAll('code'):
    tag.replaceWith('')
  htmlNoCode = str(soup)
  #Remove all the tags
  rawText = ''.join(BeautifulSoup(htmlNoCode).findAll(text=True))
  #Replace all the non a-Z characters with a space
  cleanText = regex.sub(' ', rawText)
  #Combine multiple spaces into a single space
  singleSpaceText = ' '.join(cleanText.split())
  words = singleSpaceText.split(' ')
  for word in words:
    word = str(word.strip())
    #If word is not empty, considered misspelled, and pass filterWord
    if (word != "") and (not d.check(str(word))) and filterWord(word):
      if word not in output.keys():
        output[word] = {'freq': 0, 'packages': []}
      #Increase the frequency
      output[word]['freq'] += 1
      #Append the package name
      if packageName not in output[word]['packages']:
        output[word]['packages'].append(packageName)

#Do an nested sort: ascending frequency, and alphabetical of pacakge name  
sortedOutput = sorted(output.items(), key=lambda wordData: (wordData[1]['freq'], wordData[0]))
sortedFreq = sorted([wordTuple[1]['freq'] for wordTuple in sortedOutput], reverse=True)

#For words with only single usage
singleFreq = [wordTuple for wordTuple in sortedOutput if wordTuple[1]['freq'] == 1]
orderedsingleFreq = sorted(singleFreq, key=lambda singleFreq: singleFreq[0])

#Ploting data
style.use('ggplot')
plt.ion()

#Graphing spell corrections
f = plt.figure(1)
plt.plot(sortedFreq)
plt.axis([0,100,0,250])
plt.ylabel('Word Usage Count')
plt.xlabel('Ranking of Word Usage Count, Highest First')
plt.title('Ranked Word Usage Count')
f.show()

#Graphing histrogram of word usage count frequency
g = plt.figure(2)
plt.hist(sortedFreq)
plt.axis([0,250,0,1800])
plt.ylabel('Frequency')
plt.xlabel('Word Usage Count')
plt.title('Word Usage Count')
g.show()

#Graphing histrogram of word usage count frequency between 1 to 5
h = plt.figure(3)
plt.hist(sortedFreq, bins = [0,1,2,3,4,5])
plt.xticks([0 ,1, 2, 3, 4, 5])
plt.axis([1,5,0,1000])
plt.ylabel('Frequency')
plt.xlabel('Word Usage Count')
plt.title('Word Usage Count')
h.show()

#Output data to a csv file
with open('output.csv', 'w') as csvoutput:
  a = csv.writer(csvoutput, delimiter=',')
  a.writerow(['Misspelled Word?', 'Usage Frequency', 'NPM Packages'])
  for s in sortedOutput:
    a.writerow([s[0], s[1]['freq'], " ".join(s[1]['packages'])])







