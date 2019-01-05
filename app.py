from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
from imgurpython import ImgurClient
import time
import os  
import feedgenerator
from time import gmtime, strftime
import feedparser
import amazonscraper
from bs4 import BeautifulSoup
import json
import requests
from time import gmtime, strftime
from etsy_py.api import EtsyAPI
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload
import requests
import io
import sys
import logging


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
SCOPES = 'https://www.googleapis.com/auth/drive'
def contains_wanted(in_str, key_words):
    for wrd in key_words:
        if wrd.lower() in in_str:
            return True
    return False

def get_rss_redbubble(key_words):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    result = requests.get("https://www.redbubble.com/")
    c = result.content
    soup = BeautifulSoup(c, "html.parser")
    all_links = []
    samples = soup.find_all("a", "rb-dropdown-header")
    for i in  samples:
        all_links.append('https://www.redbubble.com' + i["href"])
    
    feed2 = feedgenerator.Rss201rev2Feed(
        title="events by keywords",
        link="https://redbubble.com/",
        description="New in redbubble by keywords",
        language="en")
    for j in all_links:
    
        list_title = []
        image = []
        price_description = []
        result2 = requests.get(j)
        c = result2.content
        soup = BeautifulSoup(c)
        mydivs = soup.findAll("div", {"class": "_3A6HF"})
        for i in mydivs:
            list_title.append(i['title'])
        mydivs2 = soup.findAll("img", {"class": "_2yCHr"})
        for i in mydivs2:
            image.append(i['src'])
    
        mydivs3 = soup.findAll("span", {"class": "_3FTU- _3LWZj EYMKU"})  

        for i in mydivs3:
            price_description.append(i.text)
    
        feed = feedgenerator.Rss201rev2Feed(title="all events",
                link="https://redbubble.com/",
                description="New in redbubble",
                language="en")

        res = zip(list_title, image, price_description)

        for info in res:
            feed.add_item(
                title=info[0],
                link=info[1],
                description='Price: {}'.format(info[2]),
                unique_id='none'
                    )
        feed = feed.writeString('utf-8')
        feed = feedparser.parse(feed)
        print(key_words)
        for key in feed["entries"]: 
            title = key['title']
            url = key['links'][0]['href']
            if contains_wanted(title.lower(), key_words):
                feed2.add_item(
                    title=title,
                    link=url,
                    description='by keywords',
                    unique_id='idposte'
                    )
    with open('rss_by_keywords_for_redbubble.rss', 'w') as fp:
        feed2.write(fp, 'utf-8')
    file_metadata = {'name': 'rss_by_keywords_for_redbubble.rss'}
    media = MediaFileUpload('rss_by_keywords_for_redbubble.rss', mimetype='text/plain',resumable=True)
    fili = service.files().create(body=file_metadata, media_body=media, fields='id').execute()  
def get_rss_amazon(key_words):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    title_list = []
    list_rating = []
    list_review = []
    list_url = [] 
    for i in key_words:
        print(i)
        results = amazonscraper.search(i)
        time.sleep(2)
        for result in results:
            print(result)
            title_list.append(result.title)
            list_rating.append(result.rating)
            list_review.append(result.review_nb)
            list_url.append(result.url)

    result = zip(title_list, list_rating, list_review, list_url)  
    print(list(result))
    feed = feedgenerator.Rss201rev2Feed(title="all events",
            link="https://www.amazon.com/",
            description="New in amazon",
            language="en")
    for info in result:
        feed.add_item(
                title=info[0],
                link=info[3],
                description=info[1],
                unique_id='no'
            )
    with open('rss_by_keywords_amazon.rss', 'w') as fp:
        feed.write(fp, 'utf-8')
    file_metadata = {'name': 'rss_by_keywords_amazon.rss'}
    media = MediaFileUpload('rss_by_keywords_amazon.rss', mimetype='text/plain',resumable=True)
    fili = service.files().create(body=file_metadata, media_body=media, fields='id').execute()    
def get_rss_etsy(key_words):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    title_list = []
    description_list = []
    url_list = []
    api = EtsyAPI(api_key='trq2ib58r0zqr51mmnlau3yn')
    url = '&'.join(key_words)
    url = '/listings/active?keywords=' + url
    r = api.get(url)
    data = r.json()
    for i in range(len(data['results'])):
        title_list.append(data['results'][i]['title'])
        description_list.append(data['results'][i]['description'])
        url_list.append(data['results'][i]['url'])
    result = zip(title_list, url_list, description_list)
    feed = feedgenerator.Rss201rev2Feed(title="all events",
        link="https://etsy.com/",
        description="New in etsy",
        language="en")
    for info in result:
        feed.add_item(
                title=info[0],
                link=info[1],
                description=info[2],
                unique_id='no'
                    )
    with open('rss_by_keywords_etsy.rss', 'w') as fp:
        feed.write(fp, 'utf-8')  
    file_metadata = {'name': 'rss_by_keywords_etsy.rss'}
    media = MediaFileUpload('rss_by_keywords_etsy.rss', mimetype='text/plain',resumable=True)
    fili = service.files().create(body=file_metadata, media_body=media, fields='id').execute() 
    
def get_rss_teepublic(key_words):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }
    all_links = ['https://society6.com/wall-art', 'https://society6.com/home-decor', 'https://society6.com/furniture', 'https://society6.com/bedding', 'https://society6.com/bath', 'https://society6.com/tech', 'https://society6.com/stationery', 'https://society6.com/apparel', 'https://society6.com/tabletop', 'https://society6.com/baggage']


    list_id = []
    title_list = []
    href_list = []
    for i in all_links:
        result = requests.get(i, headers=headers)
        c = result.content
        soup = BeautifulSoup(c, "html.parser")
        data = soup.find_all('script')[8]
        data = str(data)
        data = json.loads(data[33:-9])
        for i in range(len(data['feed']['cards'])):
            list_id.append(data['feed']['cards'][i]['id'])
            title_list.append(data['feed']['cards'][i]['card']['title'])
            href_list.append('https://society6.com' + data['feed']['cards'][i]['card']['link']['href'])
        feed = feedgenerator.Rss201rev2Feed(title="all events",
            link="https://society6.com/",
            description="New in society",
            language="en")
        result2 = zip(list_id, title_list, href_list)
        
        for info in result2:
            feed.add_item(
                    title=info[1],
                    link=info[2],
                    description='none',
                    unique_id=info[0]
                )
        feed = feed.writeString('utf-8')        
        feed = feedparser.parse(feed)
        feed2 = feedgenerator.Rss201rev2Feed(
            title="events by keywords",
            link="https://teepublic.com/",
            description="New in teepublic by keywords",
            language="en")
        for key in feed["entries"]: 
            title = key['title']
            url = key['links'][0]['href']
            if contains_wanted(title.lower(), key_words):
                #print('{} - {}'.format(title, url))
                feed2.add_item(
                    title=title,
                    link=url,
                    description='by keywords',
                    unique_id='idposte'
                )
    with open('rss_by_keywords_teepublic.rss', 'w') as fp:
        feed2.write(fp, 'utf-8')
    file_metadata = {'name': 'rss_by_keywords_teepublic.rss'}
    media = MediaFileUpload('rss_by_keywords_teepublic.rss', mimetype='text/plain',resumable=True)
    fili = service.files().create(body=file_metadata, media_body=media, fields='id').execute() 
  
def get_rss_imgur(key_words):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    client_id = '9ad3b6263c1b1b3'
    client_secret = '175417178f1c53525c187429412c2b54d2fc52f8'
    descr = []
    links = []
    id_list = []
    title_list = []

    client = ImgurClient(client_id, client_secret)

    items = client.gallery(section='hot', sort='time', page=0, window='day', show_viral=False)
    for item in items:
        links.append(item.link)
        title_list.append(item.title)
        id_list.append(item.id)
        descr.append(item.description)
    feed = feedgenerator.Rss201rev2Feed(title="all events",
            link="https://imgur.com/",
            description="New in imgur",
            language="en")
    result = zip(id_list, title_list, links, descr)
    for info in result:
        feed.add_item(
                title=info[1],
                link=info[2],
                description=info[3],
                unique_id=info[0]
            )
    now_time = strftime("%H:%M:%S", gmtime())
    feed = feed.writeString('utf-8')
    feed = feedparser.parse(feed)
    feed2 = feedgenerator.Rss201rev2Feed(
        title="events by keywords",
        link="https://imgur.com/",
        description="New in imgur by keywords",
        language="en")
    for key in feed["entries"]: 
        title = key['title']
        url = key['links'][0]['href']
        if contains_wanted(title.lower(), key_words):
            #print('{} - {}'.format(title, url))
            feed2.add_item(
                title=title,
                link=url,
                description='by keywords',
                unique_id='idposte'
            )
    with open('rss_by_keywords_imgur.rss', 'w') as fp:
        feed2.write(fp, 'utf-8')    
    file_metadata = {'name': 'rss_by_keywords_imgur.rss'}
    media = MediaFileUpload('rss_by_keywords_imgur.rss', mimetype='text/plain',resumable=True)
    fili = service.files().create(body=file_metadata, media_body=media, fields='id').execute() 
def get_rss_9gag(key_words):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    feed2 = feedgenerator.Rss201rev2Feed(
            title="events by keywords",
            link="https://9gag.com/",
            description="New in 9gag by keywords",
            language="en")
    list_rss = ['https://9gag-rss.com/api/rss/get?code=9GAGFresh&format=2', 'https://9gag-rss.com/api/rss/get?code=9GAGFunny&format=2', 'https://9gag-rss.com/api/rss/get?code=9GAGHot&format=2']
    for i in  list_rss:
        feed = feedparser.parse(i)
        for key in feed["entries"]: 
            title = key['title']
            url = key['links'][0]['href']
            if contains_wanted(title.lower(), key_words):
                feed2.add_item(
                    title=title,
                    link=url,
                    description=key['description'],
                    unique_id='idposte'
                )
            
    with open('rss_by_keywords_for_9gag.rss', 'w') as fp:
        feed2.write(fp, 'utf-8')
    
    file_metadata = {'name': 'rss_by_keywords_for_9gag.rss'}
    media = MediaFileUpload('rss_by_keywords_for_9gag.rss', mimetype='text/plain',resumable=True)
    fili = service.files().create(body=file_metadata, media_body=media, fields='id').execute()  
    
@app.route('/')
def index():
    return render_template(
        'index.html',
        site_data = [{'site':'imgur'}, {'site':'amazon'}, {'site':'teepublic'}, {'site':'etsy'}, {'site':'9gag'}, {'site':'redbubble'}]
    )
@app.route("/test" , methods=['GET', 'POST'])
def test():
    select = request.form.get('comp_select')
    print(select)
    text = request.form.get('key')
    processed_text = text.upper()
    key_words = text.split()
    if select == '9gag':
        get_rss_9gag(key_words)
    elif select == 'redbubble':
        get_rss_redbubble(key_words)
    elif select == 'etsy':
        get_rss_etsy(key_words)
    elif select == 'teepublic':
        get_rss_teepublic(key_words)
    elif select == 'amazon':
        get_rss_amazon(key_words)
    elif select == 'imgur':
        get_rss_imgur(key_words)
    return 'You get rss for site: {0} by such keywords as: {1}'.format(select, text)
if __name__=='__main__':
    app.run(debug=True)

