# mellonhead

This repository contains the `research_query.py` script, which is used to slack snippets of yesterday's updated Generative AI and LLM related research posted to ArXiv.

## How does it work?

`research_query.py` does the following:
# Query ArXiv for research with "Generative AI" or "LLM" in any field (title, summary, etc.) return data in order of how recent the entry was updated
# Keep entries updated yesterday.  For each:
# # Get an easier to read (and shorter) summary of the abstract from OpenAI
# # Get a list of keywords from OpenAI based on the asbstract and ArXiv keywords
# # Send to slack a message that describes the research including title, link to the full paper, date published and last updated, keywords, summmary and original abstract.

This script is intended to run once a day.

I am in Slack and will read messages, bookmarking the papers that I want to print and read in full.

## Pre-requisites

This project requires `openai` and `requests` in order to make calls to ArXiv, OpenAI, and Slack.

```bash
pip install -r requirements.txt
```

Setup before you can run:
* config.ini should include your webhook url for Slack.

```bash
[Slack]
webhook_url = https://hooks.slack.com/services/xxxxx/yyyyyy
```

* an environment variable with your OpenAI key
```bash
export OPENAI_API_KEY=xxxxxxxxx
```

## How to Run

Execute the python script.  No config parameters needed


## Future Improvements

Here are some potential improvements that can be made to the `research_query.py` script and limitations:

- Improvements needed to move this script to be executed by a cloud function (serverless chron) like AWS lambda
- Implement error handling to gracefully handle invalid input or missing data.
- Make keywords configurable
- Get smarter about figuring out which papers are most likely to be interesting or relevant to read


