import requests
import json
import xml.etree.ElementTree as ET
import configparser
import datetime
import os
from openai import OpenAI


def search_arxiv(keywords):
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = f'search_query=' + '+OR+'.join([f'all:%22{keyword.replace(" ", "+")}%22' if " " in keyword else f'all:{keyword}' for keyword in keywords])
    start = 0
    max_results = 10
    papers = []

    #print("API Key:", os.getenv("OPENAI_API_KEY"))

    while True:
        query_url = f'{base_url}{search_query}&sortBy=lastUpdatedDate&sortOrder=descending&start={start}&max_results={max_results}'
        response = requests.get(query_url)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            opensearch_metadata = root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults')
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            for entry in entries:
                updated_date = datetime.datetime.strptime(entry.find('{http://www.w3.org/2005/Atom}updated').text, '%Y-%m-%dT%H:%M:%SZ').date()
                yesterday = datetime.date.today() - datetime.timedelta(days=1)
                
                if updated_date >= yesterday:
                    papers.append({
                        'title': entry.find('{http://www.w3.org/2005/Atom}title').text,
                        'summary': entry.find('{http://www.w3.org/2005/Atom}summary').text,
                        'link': entry.find('{http://www.w3.org/2005/Atom}link').attrib['href'],
                        'updated': updated_date.strftime('%Y-%m-%d'),
                        'published': datetime.datetime.strptime(entry.find('{http://www.w3.org/2005/Atom}published').text, '%Y-%m-%dT%H:%M:%SZ').date().strftime('%Y-%m-%d'),
                        'arxiv_keywords': [category.attrib['term'] for category in entry.findall('{http://www.w3.org/2005/Atom}category')]
                    })
                else: break
                    
            total_results = int(opensearch_metadata.text)
            start += max_results
            if start >= total_results:
                break
            break
        else:
            return None
    
    return papers


def summarize(summary):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": "Provide a brief summary content you are provided with for a non-technical college student."
            },
            {
                "role": "user",
                "content": f"{summary}"
            }
        ],
        temperature=0.7,
        max_tokens=64,
        top_p=1
    )
    #print(response.choices[0].message.content)
    return response.choices[0].message.content

def keywords(title, summary, arxiv_keywords):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": "Provide a list of the top 5 keywords that describe the content you are provided with and which would interest an AI researcher. Expand arXiv keywords. Format as a comma-separated list. Keywords only. No sentences or explanations"
            },
            {
                "role": "user",
                "content": 
                   # f"Title: {title}\n"
                    f"Abstract: {summary}\n"
                    f"arXiv Keywords: {', '.join(arxiv_keywords)}\n"
            }
        ],
        temperature=0.7,
        max_tokens=64,
        top_p=1
    )
    #print(response.choices[0].message.content)
    return response.choices[0].message.content

def post_to_slack(entry):
    config = configparser.ConfigParser()
    config.read('config.ini')
    webhook_url = config['Slack']['webhook_url']
 
    headers = {'Content-Type': 'application/json'}
    line_break = "-" * (len(entry['title']) + 4)
    clean_title = ":collision: " + entry['title'].replace('\n', '') + " :collision:"
    clean_summary = entry['summary'].replace('\n', ' ') 
    data = {
        'text': f"{line_break}\n"
                f"*{clean_title}*\n"
                f"{line_break}\n"
                f"<{entry['link']}|View full paper>\n\n"
                f"*Published*: {entry['published']}\t*Updated*: {entry['updated']}\n\n"
                f"*Keywords* {entry['keywords_expanded']}\n\n"
                f"*Summary:* {entry['summary_simplified']}\n\n"
                f"*Abstract:* {clean_summary}\n\n",
        'mrkdwn': True
    }

    #print(webhook_url)
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return True
    else:
        return False
    

papers = search_arxiv(["llm","generative ai"])
for paper in papers:
    # print(f"{papers.index(paper)}: {paper['title']} \t {paper['updated']} \t {paper['published']}\n")
    paper['summary_simplified'] = summarize(paper['summary']) 
    paper['keywords_expanded'] = keywords(paper['title'],paper['summary'],paper['arxiv_keywords']) 
    post_to_slack(paper)