# ner4soft
Repository for experiments and corpora for named entity recognition (NER) for software repositories, code  and readme files.

This repository contains a software-centric NER approach based (initially) in rules and gazetteers. The idea is to use this system from other applications to obtain better context of software documentation. 

Initial experiments:
- Dependencies (package, version, higher than/lower than qualifiers)
- Qualifiers on installation instructions (e.g., platform (Docker, Conda, etc.), OS (Unix, Windows, etc.), and others)
- Persons (citations)
- Conferences (citations)
- Frameworks (e.g., Keras, Tensorflow)
- Dataset formats

## Running ner4soft API
(THIS IS WORK IN PROGRESS)

```
cd src && python App.py
```

## Running ner4soft with Docker:

**Building the image:**

1. Clone this repository
2. `cd` into the main folder (ner4soft)
3. Build the image:
```
docker build -t ner4soft .
```

**Running the image:**
Once the image has been built, you can run it with the following command:

```
docker run --rm -p 8080:8080 ner4soft:latest
```
By default, ner4soft is exposed on port 8080.

Now you are ready to do requests. Sample request:

```
curl -X POST "http://localhost:8080/processText" -H "accept: application/json;charset=UTF-8" -H "Content-Type: application/json;charset=UTF-8" -d "{ \"text\": \"You need Python 3.6 or higher.\"}"
```

Note that changes to gazetteers or rules will require rebuilding the image.

