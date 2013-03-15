# -*- coding: utf-8 -*- 

import tweepy, re
from datetime import date
import sqlite3 as sql
import os, signal, sys, base64
import urllib, urllib2
import mimetypes, types
from bs4 import BeautifulSoup

username = ""
password = ""
database = ""

conn = sql.connect(database)
c = conn.cursor()

auth = tweepy.auth.BasicAuthHandler(username, base64.b64decode(password))
api = tweepy.API(auth)

search_query = "data filter:links"
toolbar_width = 15

def urlInDatabase(url):
  c.execute('SELECT url FROM urls WHERE url = "%s" ' % url)
  return len(c.fetchall()) > 0
 

def titleInDatabase(title):
  c.execute('SELECT title FROM urls WHERE title  = "%s" ' % title)
  return len(c.fetchall()) > 0

# Fetch titles from url
def fetchTitle(url):
  """
Returns <title> of page in given url
If url contains images, documents or applications ('image' or 'application' content-type) prints corresponding text
"""
  global title
  def timeout_handler(signum, frame):
    pass
  
  old_handler = signal.signal(signal.SIGALRM, timeout_handler)
  signal.alarm(6)

  try:

    mime = mimetypes.guess_type(url)
    if type(mime[0]) == types.NoneType:
      mimetype = "None"
      fileExt = "None"
    else:
      mimetype, fileExt = mime[0].split("/")

    if mimetype.lower() == 'image':
      title = "Image"
      signal.alarm(0)
    elif mimetype.lower() == 'application':
      title = "App. Doc. Something."
      signal.alarm(0)
    else:
      # Avataan url
      opener = urllib2.build_opener()
      opener.addheaders = [('User-agent', 'Mozilla/5.0')]
      resource = opener.open(url)
      data = resource.read()
      resource.close()
      # Luetaan data BeutifulSoup-olioon
      soup = BeautifulSoup(data)
      # Haetaan sivun <title>-tagin sisältö
      raw_title = soup.find("title")
      # Poistetaan mahdolliset rivinvaihdot
      title = raw_title.renderContents().replace('\n','')
      title = " ".join(title.split())
      signal.alarm(0)

    return title

  except:
    title = "Not found"
    signal.alarm(0)
    return title


results = api.search(search_query, include_entities=True)

for result in results:
  url = result.entities['urls'][0]['expanded_url']
  title = fetchTitle(url).decode('latin-1')
  if title == "Not found" or title == "Image":
    continue
  if urlInDatabase(url) or titleInDatabase(title):
    continue
  user = result.from_user
  day = date.today()
  try:
    insertables = (url.decode('latin-1'), title.decode('latin-1'), user.decode('latin-1'), day, "true")
    c.execute("INSERT INTO urls VALUES (?, ?, ?, ?, ?)", insertables)
    conn.commit()
  except:
    pass

c.close()
sys.stdout.write("\n")
