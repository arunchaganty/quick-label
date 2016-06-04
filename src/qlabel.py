#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The QuickLabel entry point
"""

from __future__ import division
from crf import CRF
from edit_shell import EditShell, QuitException
from data_store import DataStore
from configparser import ConfigParser

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

def do_command(args):
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('config', type=argparse.FileType('r'),  help="Path to configuration file")
    parser.set_defaults(func=do_command)

    ARGS = parser.parse_args()
    ARGS.func(ARGS)
