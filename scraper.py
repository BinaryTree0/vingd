from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import codecs
import sched, time

# Strukture potrebne za spremanje podataka
mainlinkList = set()
linkMap = dict()

# Dictionary koji sprema vec postojece clanke
clanci = dict()

# Pocetni URL
target_url = 'https://www.vecernji.hr/'

# Inicjalitiranje schedulera
s = sched.scheduler(time.time, time.sleep)

# Funkcija za dobivanje parsiranog html file-a prima url straanice koju zelimo parsirati
def accessFunction(target_url):
	vecernjiClient = urlopen(target_url)
	html_page_byte = vecernjiClient.read()
	html_page = soup(html_page_byte,'html.parser')
	vecernjiClient.close()
	return html_page;

# Funkcija za dobivanje glavnih linkova prima navigacijsku traku stranice- trenutno nema neku svrhu ali korisno je imati recimo da se svakih 15 minuta updatea jedan od glavnih linkova
def parentlinksFunction( navbar ):
	mainlinks = navbar.findAll("a",{"class":"nav__link"})
	for links in mainlinks:
		link = links["href"]
		if(link[0:1] == "/"):
			value = set()
			key = target_url + link[1:]
			linkMap.update({key:value})
	return;

# Funkcija za dobivanje sporednih linkova prima navigacijsku traku stranice
def childlinksFunction( navbar ):
	sidelinks = navbar.findAll("a",{"class":"nav__link2"})
	for links in sidelinks:
		link = links["href"]
		if(link[0:1] == "/"):
			value = set()
			key = target_url + link[1:]
			linkMap.update({key:value})
			getlinkUrls(key)
	return;

# Funkcija za dobivanje informacija o clancima prima url clanka koji zelimo
def getInfo( url ):
	linkClanak = accessFunction(url)
	clanci.update({url:1})
	print(linkClanak.title.string.replace(",","|") +","+ linkClanak.find("span",{"class":"article__header_date"}).text.strip() + "," + url)
	f.write(linkClanak.title.string.replace("- Večernji.hr","") +","+ linkClanak.find("span",{"class":"article__header_date"}).text.strip() + "," + url+"\n")
	return;

# Funkcija koja pronalazi url-ove clanaka s jednog od danih glavnih linkova
def getlinkUrls( url ):
	linkClanak = accessFunction(url).findAll("a",{"class":"card__link"})
	for links in linkClanak:
		link = links["href"]
		if(link[0:1] == "/"):
			linkClanakKrajnji = target_url+link[1:]
			linkMap.get(url).add(linkClanakKrajnji)
			if (linkClanakKrajnji not in clanci):
				getInfo(linkClanakKrajnji)
	return;

# Funkcija koja ažurira data set svakih sat vremena
def checkNewUpdate():
	for links in linkMap.values():
		for link in links:
			getlinkUrls (link);
	s.enter(3600, 1, checkNewUpdate, (sc,))

# Glavni dio programa - program se nažalost gasi sa ctr^C ili gašenjem console.

filename = "./vecernjiData.csv"
f = codecs.open(filename,"a","utf-8")
headers = "name , date , link\n"
f.write(headers)
navbar = accessFunction(target_url).find("nav")
parentlinksFunction(navbar)
childlinksFunction(navbar)
print("sad cekam malo")
s.enter(3600, 1, checkNewUpdate(), (s,))
s.run()
f.close()
