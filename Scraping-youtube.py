
import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import ssl
import ast
import os
from urllib.request import Request, urlopen
import pandas as pd
import xlrd
import time


def scrape_data(soup, video_details):

    for span in soup.findAll('span',attrs={'class': 'watch-title'}):
        if 'TITLE' not in video_details: # Create the key if the key is not in the dictionary
            video_details['TITLE']= [span.text.strip()] # insert value in the key as a list

        else: # If the key exist append the new value to the lst of values for the key
            video_details['TITLE'].append(span.text.strip())

    for script in soup.findAll('script',attrs={'type': 'application/ld+json'}):
        channelDesctiption = json.loads(script.text.strip())
        if 'CHANNEL_NAME' not in video_details:
            video_details['CHANNEL_NAME'] = [channelDesctiption['itemListElement'][0]['item']['name']]
        else:
            video_details['CHANNEL_NAME'].append(channelDesctiption['itemListElement'][0]['item']['name'])

    for strong in soup.findAll('strong', attrs={'class': 'watch-time-text'}):
        if 'PUBLISHED_DATE' not in video_details:
            video_details['PUBLISHED_DATE'] = [strong.text.strip()]
        else:
            video_details['PUBLISHED_DATE'].append(strong.text.strip())

    for div in soup.findAll('div',attrs={'class': 'watch-view-count'}):
        if 'NUMBER_OF_VIEWS' not in video_details:
            video_details['NUMBER_OF_VIEWS'] = [div.text.strip()]
        else:
            video_details['NUMBER_OF_VIEWS'].append(div.text.strip())

    for button in soup.findAll('button',attrs={'title': 'I like this'}):
        if 'LIKES' not in video_details:
            video_details['LIKES'] = [button.text.strip()]
        else:
            video_details['LIKES'].append(button.text.strip())

    for c, button in enumerate(soup.findAll('button',attrs={'title': 'I dislike this'})):
        if 'DISLIKES' not in video_details:
            video_details['DISLIKES'] = [button.text.strip()]
        else:
            if c < 1:
                video_details['DISLIKES'].append(button.text.strip())
            else:
                break
    '''
    for span in soup.findAll('span',attrs={'class': 'yt-subscription-button-subscriber-count-branded-horizontal yt-subscriber-count'}):
        if 'NUMBER_OF_SUBSCRIPTIONS' not in video_details:
            video_details['NUMBER_OF_SUBSCRIPTIONS'] = [span.text.strip()]
        else:
            video_details['NUMBER_OF_SUBSCRIPTIONS'].append(span.text.strip())

    hashtags = []
    for span in soup.findAll('span',attrs={'class': 'standalone-collection-badge-renderer-text'}):
        for a in span.findAll('a',attrs={'class': 'yt-uix-sessionlink'}):
            hashtags.append(a.text.strip())

    if 'HASH_TAGS' not in video_details:
        video_details['HASH_TAGS'] = [hashtags]
    else:
        video_details['HASH_TAGS'].append(hashtags)
    '''

    return video_details




def scrape_all(url_list):
    video_details = {}

    for url in url_list:
        req = Request(url, headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser') # Creating a BeautifulSoup object of the html page
        video_details = scrape_data(soup, video_details) # Scraping the data
        #time.sleep(3)# making the for loop execute every 3 sec


    print ('----------Extraction of data is complete----------')

    return video_details



def clean_data_(video_details):

    df = pd.DataFrame(video_details) # Convert dictionary to DataFrame

    df['PUBLISHED_DATE'] = df['PUBLISHED_DATE'].map(lambda x: str(x.replace('Published on','').strip()))
    df['NUMBER_OF_VIEWS'] = df['NUMBER_OF_VIEWS'].map(lambda x: x.replace((' views'), '').replace(',','').strip())
    df['LIKES'] = df['LIKES'].map(lambda x: x.replace(',',''))
    df['DISLIKES'] = df['DISLIKES'].map(lambda x: x.replace(',',''))

    return df



if __name__ == '__main__':

    # For ignoring SSL certificate errors

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Load your list of url
    # List of url I have is in excel format
    # You can change the code to load the suitable format file
    df_url = pd.read_excel('listurl.xlsx') # Type your youtube URL here
    df_url.url.apply(lambda x: str(x))
    url_list = list(df_url.url)

    # Start scraping
    videos = scrape_all(url_list)
    df = clean_data(videos)

    # Convert the DataFrame to a CSV file and save it on disk
    df.to_csv('Yotube_Data_1.csv')

    print("-------------Check CSV file-------------")
