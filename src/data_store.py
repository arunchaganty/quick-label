"""
Stores data, allowing for quick iteration.
"""

import csv
from util import annotate_sentence, parse_conll, write_conll

class DataStore(object):
    """
    Stores data, allowing for quick iteration.
    """
    TAG_LABEL = 3

    def __init__(self, config):
        """
        Keeps track of training data.
        """
        train_path = config["paths"]["train"]
        source_path = config["paths"]["txt"]
        self.train_path = train_path

        # Load all the labelled data.
        with open(train_path) as f:
            reader = csv.reader(f, delimiter='\t')
            self.labelled_data = list(parse_conll(reader))
        # Load all the unlabelled data.
        self.unlabelled_data = list(open(source_path))
        # The assumption that the labelled data is a subset of the
        # unlabelled data is an assumption
        assert len(self.unlabelled_data) >= len(self.labelled_data)
        # Current index
        self.cur_index = len(self.labelled_data)

        # Open a appendable handle to the labelled data file
        self.labelled_data_file = open(train_path, 'a')

    def update(self, conll, tags):
        """
        Updates labels for the current example.
        """
        # Create labelled data
        conll_labelled = [feats[:self.TAG_LABEL] + [t] for feats, t in zip(conll, tags)]

        # If we've move previous, rewrite the whole labelled set.
        if self.cur_index <= len(self.labelled_data):
            self.labelled_data[self.cur_index-1] = conll_labelled
            self.labelled_data_file.close()
            self.labelled_data_file = open(self.train_path,'w')
            for conll in self.labelled_data:
                write_conll(self.labelled_data_file, conll)
            self.labelled_data_file.close()
            self.labelled_data_file = open(self.train_path,'a')
        else:
            self.labelled_data.append(conll_labelled)
            write_conll(self.labelled_data_file, conll_labelled)

    def __iter__(self):
        """
        Iterator interface.
        """
        # Current index
        self.cur_index = len(self.labelled_data)
        return self

    def __getitem__(self, i):
        """
        Return the element at index i
        """
        if i < len(self.labelled_data):
            return self.labelled_data[i]
        else:
            # First call annotate on the unlabelled sentence
            sentence = self.unlabelled_data[i]
            return annotate_sentence(sentence)

    def __next__(self):
        return self.next()

    def next(self):
        """
        Returns next element
        """
        if self.cur_index > len(self):
            raise StopIteration()
        else:
            elem = self[self.cur_index]
            self.cur_index += 1
            return elem

    def rewind(self, i):
        """
        Return previous example by rewinding index by @i.
        """
        self.goto(self.cur_index-i)

    def has_next(self):
        """Returns if there are still unlabelled data left"""
        return self.cur_index < len(self)

    def i(self):
        """Returns current index"""
        return self.cur_index

    def goto(self, i):
        """
        Go to a particular index
        """
        if i < 0:
            raise AttributeError()
        self.cur_index = i

    def __len__(self):
        return len(self.unlabelled_data)

def test_data_store():
    """
    Test for the datastore
    """
    from configparser import ConfigParser
    config = ConfigParser()
    config.read_file(open('quotes.config'))

    data = DataStore(config)

    data.cur_index = 0
    for _ in range(10):
        print(" ".join([t[0] for t in data.next()]))
    data.rewind(2)
    print(" ".join([t[0] for t in data.next()]))

if __name__ == "__main__":
    test_data_store()

