# Create NER corpus

The script `create_corpus_for_NER.py` requires having [SOMEF](https://github.com/KnowledgeCaptureAndDiscovery/somef/) installed (and setting the right path to the `repos_to_process` folder, which is used as input).

The script also removes code blocks (i.e., text in between three ` ` ` chacarters)

The corpus in in JSONL format, which is the one accepting by [Doccano](https://github.com/doccano/doccano), the tool we are using to annotate everything.

