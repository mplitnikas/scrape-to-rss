import datetime
import boto3
import requests as req
from rfeed import *
from bs4 import BeautifulSoup

class Podcast:
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
            return unicode(self.content.h2.contents[0])
        except:
            pass

    def __init__(self, content):
        self.content = content
        self.url = self.get_media_url() # enclosure url, rename for clarity
        self.date = self.get_date()
        self.title = self.get_title()

def scrape_and_output():
    url = 'http://pftmedia.com/?s=the+major+scale'
    s3_bucket_name = 'wgot-rss-scrape'
    s3_bucket_path = 'the-major-scale'

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_bucket_name)

    search_page = req.get(url).content
    soup = BeautifulSoup(search_page, 'html.parser')

    title_links = soup.find_all('a', attrs={'class':'entry-title-link'})
    podcasts_content = [req.get(title_link['href']).content for title_link in title_links]
    podcasts_parsed = [BeautifulSoup(podcast, 'html.parser') for podcast in podcasts_content]

    shows = [Podcast(x) for x in podcasts_parsed]

    # future: get etag from headers, save to file, compare when making request

    feedItems = [Item(
                title=show.title,
                enclosure=Enclosure(
                    url=show.url,
                    type="audio/mpeg",
                    length=0),
                pubDate=show.date)
            for show in shows]

    feed = Feed(
            title="The Major Scale",
            link="https://pftmedia.com/category/pft-radio-network/major-scale/",
            description="The Major Scale by PFT Media",
            lastBuildDate=datetime.datetime.now(),
            items=feedItems)

    rss_feed = feed.rss()
    object_url = s3_bucket_path + '/' + 'feed.rss'
    bucket.put_object(Key=object_url, Body=rss_feed, ContentType='application/rss+xml')

if __name__ == "__main__":
    scrape_and_output()
