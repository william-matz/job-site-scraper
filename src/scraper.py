from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def make_soup(link, connect=3, backoff_factor=0.5):
    """Pulls the full page with BeautifulSoup & Requests
    Args:
        link (str): A full URL of the page to scrape
    Returns:
        soup (bs4 object): A BeautifulSoup Object containing the full contents of the [link]'s page
    """
    session = requests.Session()
    retry = Retry(connect, backoff_factor) #Back off in case of request failure
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    get_page = session.get(link)
    html = get_page.content
    soup = bs(html, 'html.parser') #Use the built-in html parser
    return  soup


def scrape_job_urls(full_home_page, url_base):
    """Scrapes every URL with the structure [url_base] + '/job/'
    Returns an array with all urls that link to jobs
    """

    urls = []
    for a_tag in full_home_page.findAll('a'):  #Find all links
        link_extension = str(a_tag.get('href'))
        if link_extension[0:5]=="/job/": #If it's a job link, store it
            urls.append(url_base + link_extension)

    return urls


def perks_scrape(job_page):
    """
    """
    perks = []
    #All perks are defined within the class 'perk-title'
    perk_classes = job_page.find_all(class_='perk-title')

    if perk_classes is not None:
        for perk in perk_classes:
            #The categories of the perks are a few parents up, with class 'category-title'
            data = {"name":perk.get_text('span'),"cat":perk.parent.parent.parent.parent.find(class_="category-title").get_text()}
            perks.append(data)

    return perks


def tools_scrape(job_page):
    """
    """
    tools = []

    #All tools are defined within the class 'full-stack-item'
    tool_classes = job_page.find_all(class_='full-stack-item')

    if tool_classes is not None:
        for tool in tool_classes:
            data = {"name":tool.get_text(),"cat":tool.next_sibling.get_text()}
            tools.append(data)

    return tools


def job_page_scrape(link, verbose=False):
    """
    Scrapes a specific job page
    """
    print('-------------' + link) #Print in every case, to show progress

    job_page = make_soup(link)  #Requests the full job page



    perks = perks_scrape(job_page)
    tools = tools_scrape(job_page)
    
    return [perks, tools]


# ---------------------------------------------------------------
# ---------------------------------------------------------------


url_base = 'https://www.builtinla.com'
url_home = 'https://builtinla.com/jobs'

perks=[]
technologies=[]

page = 0
num_urls = 1
while num_urls > 0: #Loop through pages on the job site, stop if there's no more
    full_home_page = make_soup(url_home + str(page))
    print("Page "+str(page))
    page += 1
    
    job_urls = scrape_job_urls(full_home_page, url_base)
    num_urls = len(job_urls)
    print("Num "+str(num_urls))
    
    for link in job_urls:
        list = job_page_scrape(link)
        perks.append(list[0])
        technologies.append(list[1])