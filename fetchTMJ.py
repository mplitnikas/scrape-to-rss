import requests as req
import datetime
from rfeed import *
from bs4 import BeautifulSoup

url = 'https://pftmedia.com/category/pft-radio-network/major-scale/'

page = req.get(url).content
soup = BeautifulSoup(page, 'html.parser')

class Post:
    def get_media_url(self):
        try:
            return unicode(self.content.find_all('a', download=True)[0]['href'])
        except:
            pass

    def get_date(self):
        try:
            datetime_text = self.content.find_all('time')[0]['datetime']
            date_text = datetime_text.split('T')[0] # discard time portion
            return datetime.datetime.strptime(date_text, '%Y-%m-%d');
        except:
            pass

    def get_title(self):
        try:
            return unicode(self.content.h2.a.contents[0])
        except:
            pass

    def get_desc(self):
        try:
            return ''.join([unicode(elem) for elem in self.content \
                .find_all(attrs={'class':'entry-content'})[0].contents])
        except:
            pass

    def __init__(self, content):
        self.content = content
        self.url = self.get_media_url() # enclosure url, rename for clarity
        self.date = self.get_date()
        self.title = self.get_title()
        self.desc = self.get_desc()

posts = [Post(x) for x in soup.find_all('article', attrs={'class': 'post'})]

# future: get etag from headers, save to file, compare when making request

feedItems = [Item(
            title=post.title,
            description=post.desc,
            enclosure=Enclosure(
                url=post.url,
                type="audio/mpeg",
                length=0),          # do we care about this property?
            pubDate=post.date)
        for post in posts]

feed = Feed(
        title="The Major Scale",
        link="https://pftmedia.com/category/pft-radio-network/major-scale/",
        description="The Major Scale by PFT Media",
        lastBuildDate=datetime.datetime.now(),
        items=feedItems)

print feed.rss()
