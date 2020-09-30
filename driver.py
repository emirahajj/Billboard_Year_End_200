#Author: Emira Hajj

#Webscraping python script to extract Billboard 200 end of year chart data from 1970-2019.

#After collecting entries, runs a google search to a music database allmusic.com to extract genre and
#release year since it's more well-formatted than Wikipedia. Exports each chart year to individual csv files.

#The official Billbaord data available on their site is missing over 699 entries (more than 3 years worth of chart entries)

#The end goal is to host data in a DB and create a web app to perform various statistical analysis on each year/decade.

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search
from selenium.common.exceptions import NoSuchElementException

op = webdriver.ChromeOptions()
#headless option prevents the driver chrome window from opening, I don't want 50 open windows!
op.add_argument('headless')
browser1 = webdriver.Chrome(options=op, executable_path="/usr/local/bin/chromedriver")
album = [] #album title list
author = [] #album author list
published = [] #album publish year list
genre = [] #genre list
rank= [] #album rank list
chartyr= [] #charting year list
albumID=[] #uniquely identifying 

#initializing empty variables
link = '' 
date = ''
style = ''
linkbum=''
the_ID= ''
#loops over the range to represent chart years 1970-2019
for year in range(1969, 2019, -1):
    #luckily the path to the charts only differs in the year, so parsing the url is easy
    url1= 'https://www.billboard.com/charts/year-end/' + str(year) + '/top-billboard-200-albums'
    browser1.get(url1)
    #saves
    top200 = browser1.find_elements_by_class_name('ye-chart-item__primary-row')
    #extract necessary data from class names in html file
    for albie in top200:
        position=albie.find_element_by_class_name('ye-chart-item__rank').text
        bum=albie.find_element_by_class_name('ye-chart-item__title').text
        art=albie.find_element_by_class_name('ye-chart-item__artist').text
        #query to run on google to return allmusic.com entry for that album
        query = bum +' by '+ art + ' album allmusic'
        for j in search(query, tld="com", lang='en', num=3, start=0, stop=3,pause=2):
            if 'allmusic.com/album/' in j:
                link = j
                break
        #opens second browser in headless mode to try to extract genre and release date from allmusic.com
        browser2 = webdriver.Chrome(options=op, executable_path="/usr/local/bin/chromedriver")
        if link==" " or 'allmusic.com/album/' not in link: 
            date="---"
        else:
            browser2.get(link)
            try:
                date=browser2.find_element_by_xpath("//div[@class='release-date']/span").text[-4:]
            except NoSuchElementException:
                date = 'N/A'
            try:
                style = browser2.find_element_by_xpath("//div[@class='genre']/div/a").text
            except NoSuchElementException:
                style = 'N/A'
        browser2.close()

        #append each value to the apporpriate list
        chartyr.append(year)
        album.append(bum)
        author.append(art)
        published.append(date)
        genre.append(style)
        rank.append(position)
        albumID.append(the_ID)

        #reassign to blanks so the previous positions information doesn't "leak" into next position 
        date = ' '
        linker = ' '
        link = ' '
        style = ' '
    
    #exporting to csv files
    df = pd.DataFrame(list(zip(rank,chartyr,album,author,albumID,published,genre)), columns=['RANK', 'CHARTYR','ALBUM', 'ARTIST', 'ALBUMID','DATE', 'GENRE'])
    csv_name = str(year)+'.csv' 
    df.to_csv(csv_name, index=False)

    #clear the arrays to avoid appending to them forever
    album.clear() 
    author.clear()
    published.clear()
    rank.clear()
    albumID.clear()

    #quit the browsers windows--your RAM will thank you!
    browser1.quit()
    browser2.quit()
