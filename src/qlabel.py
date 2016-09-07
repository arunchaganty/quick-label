#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The QuickLabel entry point
"""

from __future__ import division
import csv
from collections import namedtuple
from configparser import ConfigParser

from crf import CRF
from edit_shell import EditShell, QuitException
from data_store import DataStore
from util import get_longest_span
from pgutil import parse_psql_array, to_psql_array

def render_progress(data, accuracy):
    """
    Create a progress bar.
    """
    if len(accuracy) > 0:
        acc = sum(accuracy)/len(accuracy) * 100
        w_acc = sum(accuracy[:5])/len(accuracy[:5]) * 100
    else:
        acc, w_acc = 0, 0
    return "acc={:.1f} w_acc={:.1f} {}/{}".format(acc, w_acc, data.i(), len(data))

def score(guess, gold):
    """Compute just tag accuracy"""
    return sum(1 for tag, tag_ in zip(guess, gold) if tag == tag_)/len(guess)

def do_train(args):
    # Load configuration
    config = ConfigParser()
    config.read_file(args.config)

    data = DataStore(config)

    # Create the CRF model.
    model = CRF(config)

    retrain_epochs = config["training"].getint("retrain_every")

    accuracy = []

    with EditShell(config) as shell:
        while data.has_next():
            conll = data.next()
            i = data.i()

            # if the data doesn't have tags, try to smart-tag them.
            if len(conll[0]) == DataStore.TAG_LABEL+1:
                tags = [tok[DataStore.TAG_LABEL] for tok in conll]
            else:
                tags = model.infer(conll)

            try:
                #conll_display = ["{}/{}".format(token[0], token[2]) for token in conll]
                conll_display = ["{}".format(token[0]) for token in conll]

                # Create a copy of the list
                action = shell.run(conll_display, list(tags), metadata=render_progress(data, accuracy))

                if action.type == ":prev":
                    try:
                        data.rewind(2) # move 2 indices back
                    except AttributeError:
                        data.rewind(1)
                elif action.type == ":goto":
                    doc_idx, = action.args
                    assert doc_idx >= 0
                    data.goto(doc_idx)
                elif action.type == "save":
                    _, tags_ = action.args
                    accuracy.append(score(tags, tags_))

                    data.update(conll, tags_)

                    if i % retrain_epochs == 0:
                        model.retrain()

            except QuitException:
                break

def extract_quote_entries(sentence, tags):
    """
    Extract the quote entries from the sentence.
    """
    gloss = sentence.gloss
    doc_char_begin = list(map(int, parse_psql_array(sentence.doc_char_begin)))
    doc_char_end = list(map(int, parse_psql_array(sentence.doc_char_end)))

    # Parse the speaker tags.
    speaker_start, speaker_end = get_longest_span(tags, "SPKR")
    cue_start, cue_end = get_longest_span(tags, "CUE")
    content_tokens = [i for i, tag in enumerate(tags) if tag == "CTNT"]
    content_start, content_end = min(content_tokens), max(content_tokens)
    # Get character offsets.
    assert speaker_start is not None
    assert content_start is not None
    offset = doc_char_begin[0]
    speaker = gloss[doc_char_begin[speaker_start]-offset:doc_char_end[speaker_end-1]-offset+1]
    content = gloss[doc_char_begin[content_start]-offset:doc_char_end[content_end-1]-offset+1]
    if cue_start is not None:
        cue = gloss[doc_char_begin[cue_start]-offset:doc_char_end[cue_end-1]-offset+1]
    else:
        cue = None

    return (speaker_start, speaker_end,
            cue_start, cue_end,
            content_start, content_end, to_psql_array(map(str,content_tokens)),
            speaker, cue, content)

def do_infer(args):
    config = ConfigParser()
    config.read_file(args.config)
    model = CRF(config)

    writer = csv.writer(args.output, delimiter='\t')
    reader = csv.reader(args.input, delimiter='\t')
    header = next(reader)
    #if args.has_annotations:
    assert all(w in header for w in ["id", "words", "lemmas", "pos_tags", "doc_char_begin", "doc_char_end", "gloss"]), "Input doesn't have required annotations."
    #else:
    #    assert all(w in header for w in ["id", "text"]), "Input doesn't have ids."

    writer.writerow([
        'id',
        'speaker_start', 'speaker_end',
        'cue_start', 'cue_end',
        'content_start', 'content_end', 'content_tokens',
        'speaker', 'cue', 'content'])
    Sentence = namedtuple('Sentence', header)
    for row in reader:
        assert len(row) == len(header), "Row did not have enough fields: " + row
        sentence = Sentence(*row)
        words, lemmas, pos_tags = [parse_psql_array(arr) for arr in (sentence.words, sentence.lemmas, sentence.pos_tags)]
        conll = zip(words, lemmas, pos_tags)
        tags = model.infer(conll)
        if "SPKR" not in tags or "CTNT" not in tags: continue
        writer.writerow((sentence.id,) + extract_quote_entries(sentence, tags))

if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--config', type=argparse.FileType('r'),  help="Path to configuration file")

    subparsers = parser.add_subparsers()
    command_parser = subparsers.add_parser('train', help='Opens the training interface')
    command_parser.set_defaults(func=do_train)

    command_parser = subparsers.add_parser('infer', help='Uses the trained model to evaluate new sentences')
    command_parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin, help="Input")
    #command_parser.add_argument('--has_annotations', action='store_true', default=False, help="Does the input have annotations?")
    command_parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout, help="Output")
    command_parser.set_defaults(func=do_infer)

    ARGS = parser.parse_args()
    ARGS.func(ARGS)
