import requests
import json
import xml.etree.ElementTree as ET
import configparser
import datetime


def search_arxiv(query):
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = f'search_query=all:{query}'
    start = 0
    max_results = 10

    query_url = f'{base_url}{search_query}&sortBy=lastUpdatedDate&sortOrder=descending'

    response = requests.get(query_url)

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        papers = [{'title': entry.find('{http://www.w3.org/2005/Atom}title').text,
                   'summary': entry.find('{http://www.w3.org/2005/Atom}summary').text,
                   'link': entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']}
                  for entry in entries]
                 # if datetime.datetime.strptime(entry.find('{http://www.w3.org/2005/Atom}updated').text, '%Y-%m-%dT%H:%M:%SZ').date() == datetime.date.today() - datetime.timedelta(days=1)]
        return papers
    else:
        return None

def post_to_slack(entry):
    config = configparser.ConfigParser()
    config.read('config.ini')
    webhook_url = config['Slack']['webhook_url']
 
    headers = {'Content-Type': 'application/json'}
    clean_title = ":collision: " + entry['title'].replace('\n', '') + " :collision:"
    clean_summary = entry['summary'].replace('\n', ' ') 
    data = {
        'text': f"*{clean_title}*\n"
                f"<{entry['link']}|View full paper>\n\n"
                #f"*Abstract*\n"
                f"{clean_summary}",
        'mrkdwn': True
    }

    print(webhook_url)
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return True
    else:
        return False
    

papers = search_arxiv("llm")
for paper in papers:
    #print(paper)
    post_to_slack(paper)