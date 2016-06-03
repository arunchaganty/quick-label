#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
from urllib.parse import urlencode
from urllib.request import quote
import subprocess
import csv
import json
from settings import SERVER_URI

def parse_conll(reader):
    """
    Parses a file in CONLL input, i.e.
    'TOKEN(<TAB>FEAT)+' for each token in a sentence, followed by a new line.
    """
    current = []
    for row in reader:
        # Handling.
        if len(row) == 0:
            if len(current)> 0:
                yield list(zip(*current))
            current = []
        else:
            current.append(row)
        # End logic
    if len(current) > 0:
        yield list(zip(*current))

def sentence_to_conll(ostream, sentence):
    """
    Output sentence to conll format
    """
    writer = csv.writer(ostream, delimiter='\t')

    for token in sentence["tokens"]:
        row = [token["word"], token["lemma"], token["pos"]]
        if "_tag" in token:
            row.append(token["_tag"])
        writer.writerow(row)

def __call_server(doc, props, uri=SERVER_URI):
    """
    Calls a remote server to annotate doc
    """
    # Save doc in a temporary file.
    if len(props) > 0:
        uri = "%s?%s"%(uri, urlencode({"properties" : json.dumps(props)}))
    else:
        uri = uri
    return subprocess.check_output(["curl", uri, "--data", quote(doc)], stderr=subprocess.DEVNULL).decode()

def annotate_doc(doc):
    """
    Annotate
    """
    props = {"annotators":"tokenize,ssplit,lemma,pos"}
    return json.loads(__call_server(doc, props))

def annotate_sentence(sentence):
    """
    Annotate a sentence (simpler return)
    """
    obj = annotate_doc(sentence)
    assert len(obj["sentences"]) == 1
    return obj["sentences"][0]

def partition(lst, length):
    """
    Split lst into chunks of @length
    """

    i = 0
    for j in range(0, len(lst), length):
        yield i, lst[j:j+length]
        i += 1

