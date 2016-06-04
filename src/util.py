#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
import ipdb
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
                yield current
            current = []
        else:
            current.append(row)
        # End logic
    if len(current) > 0:
        yield current

def read_conll_doc(blob):
    ret = []
    cur = []
    for toks in blob.split("\n"):
        if len(toks) == 0 and len(cur) > 0:
            ret.append(cur)
            cur = []
        elif len(toks) > 0:
            feats = toks.split("\t")
            assert len(feats)
            cur.append(feats)
    return ret

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

def write_conll(ostream, conll):
    """
    Output sentence to conll format
    """
    ostream.writelines(['\t'.join(fields) + "\n" for fields in conll] + ["\n"])

def __call_server(doc, props, uri=SERVER_URI):
    """
    Calls a remote server to annotate doc
    """
    # Save doc in a temporary file.
    if len(props) > 0:
        uri = "%s?%s"%(uri, urlencode({"outputFormat":"conll", "properties" : json.dumps(props)}))
    else:
        uri = uri
    return subprocess.check_output(["curl", uri, "--data", quote(doc)], stderr=subprocess.DEVNULL).decode()

def annotate_doc(doc):
    """
    Annotate
    """
    props = {"annotators":"tokenize,ssplit,lemma,pos"}
    ret = __call_server(doc, props)
    conll = read_conll_doc(ret)
    # Simplify conll; only take columns 2, 3, 4
    return [[tok[1:4] for tok in sentence] for sentence in conll]

def annotate_sentence(sentence):
    """
    Annotate a sentence (simpler return)
    """
    doc = annotate_doc(sentence)
    assert len(doc) == 1
    return doc[0]

def partition(lst, length):
    """
    Split lst into chunks of @length
    """

    i = 0
    for j in range(0, len(lst), length):
        yield i, lst[j:j+length]
        i += 1

