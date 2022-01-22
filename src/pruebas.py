import requests
from bs4 import BeautifulSoup
import json
import re
import os
from somef.cli import cli_get_data
import tempfile
from datetime import datetime

def cli_get_results(repo_data):
    results = {
    "description": [],
    "acknowledgement": [],
    "installation": [],
    "requirement": [],
    "usage": []
    }

    for i in repo_data.keys():
            if i in results.keys():
                # filter those which are header analysis
                section_result = repo_data[i]
                for j in section_result:
                    if j["technique"] == "Header extraction":
                        #print(i)
                        current_list = results[i]
                        text_with_no_code = re.sub(r"```.*?```", 'CODE_BLOCK', j["excerpt"], 0, re.DOTALL)
                        result = {
                            "id": len(current_list) + 1,
                            "title": dir_name,
                            "text": text_with_no_code
                        }
                        current_list.append(result)
                        results[i] = current_list
    return results

input_folder = "../corpus_creation/repos_to_process"


dir_name = os.listdir(input_folder)[0]
print("######## Processing: " + dir_name)
repo_data = cli_get_data(0.8, True, doc_src=os.path.join(input_folder, dir_name))
res_local = cli_get_results(repo_data)

# Get the repo html
r = requests.get("https://github.com/MarcoAS99/ner4soft/tree/main/corpus_creation/repos_to_process").text
soup = BeautifulSoup(r,'html.parser')

git_base_url = "https://github.com"
# Get all the urls of the various files to analize from the html of the repo
urls = [f"{git_base_url}{a['href']}" for a in soup.find_all('a', href=True) if 'blob' in a['href']]
# Get all the individual files html from the urls found
raw_r = [requests.get(url).text for url in urls]
# Get the raw url of each file (when requested it will return the markdown itself instead of the html)
raw_urls = [f"{git_base_url}{a['href']}" for a in [s.find(id="raw-url", href=True) for s in [BeautifulSoup(_r,'html.parser') for _r in raw_r]]]
url_doc = requests.get(raw_urls[0]).text
doc_names = [r.split('/')[-1] for r in raw_urls]
# Directory and file will auto-delete once out of with block
with tempfile.TemporaryDirectory() as td:
    tf_name = os.path.join(td,'temp.md')
    # Creating a file with the contents of the markdown for cli to read
    with open(tf_name, 'w', encoding='utf-8') as tf:
        tf.write(url_doc)
    repo_data = cli_get_data(0.8, True, doc_src=os.path.join(tf_name))


res_url = cli_get_results(repo_data)
print(f"---- res_local:\n{res_local}\n\n\n---- res_url:\n{res_url}\n\nEquals: {res_local == res_url}")

# Get current day formated yyyy-mm-dd --> datetime.now().strftime("%Y-%m-%d")