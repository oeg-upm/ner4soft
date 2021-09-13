# This is a script to create an annotation corpus from SOMEF outputs.
# As input, this script expects a folder with readme files.
# As output, this script generates a series of JSONL files, each with an annotation corpus.
# Files are generated for description, ack, installation, requirements and run sections
# A special treatment is done to all the elements under the first header
import json
import os
import re

from somef.cli import cli_get_data

input_folder = "repos_to_process"

results = {
    "description": [],
    "acknowledgement": [],
    "installation": [],
    "requirement": [],
    "usage": []
}

# Read repos apply somef to each of them.
for dir_name in os.listdir(input_folder):
    #try:
        print("######## Processing: " + dir_name)
        repo_data = cli_get_data(0.8, True, doc_src=os.path.join(input_folder, dir_name))
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
        # print (results)
    #except:
    #    print("Error when processing" + dir_name)

# transform each of the categories to a JSONL corpus.
for category in results.keys():
    with open(category+".jsonl", "w") as outfile:
        for i in results[category]:
            json.dump(i,outfile)
            outfile.write("\n")
           # json.dump(, outfile)
