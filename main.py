import requests
import math as Math


##Math.round(Math.random()*100000)*31


x = requests.get('https://netzfrequenzmessung.de:9081/frequenz02a.xml?c=916856')
y = x.text.splitlines()
#print(y)
netzfrequenz = y[1].replace("<f2>", "").replace("</f2>", "")
zeit = y[3].replace("<z> ", "").replace("</z>", "")

print(zeit)
print(netzfrequenz)