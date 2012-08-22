#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 20 Groups Loader
#   - load data at http://kdd.ics.uci.edu/databases/20newsgroups/20newsgroups.html
# This code is available under the MIT License.
# (c)2012 Nakatani Shuyo / Cybozu Labs Inc.

import os, codecs, re

STOPWORDS = """
the of in a and have to it was i or were this that with is some on for
how you if s would com be your my one not never then take for b an can
but aaa when as out t just from does they back up she those who their
her do by must u what there at very are am much way all any other e me
something someone doesn false
"""

def readTerms(target):
    with codecs.open(target, 'rb', 'latin1') as f:
        text = re.sub(r'^(.+\n)*\n', '', f.read())
    return [w.group(0).lower() for w in re.finditer(r'[A-Za-z]+', text)]

class Loader:
    def __init__(self, dirpath, freq_threshold=1, docs_threshold_each_label=100, includes_stopwords=False):
        if includes_stopwords:
            stopwords = re.split(r'\s', STOPWORDS)
        else:
            stopwords = []

        self.resourcenames = []
        self.labels = []
        self.label2id = dict()
        self.doclabelids = []
        vocacount = dict()
        tempdocs = []

        dirlist = os.listdir(dirpath)
        for label in dirlist:
            path = os.path.join(dirpath, label)
            if os.path.isdir(path):
                label_id = len(self.labels)
                self.label2id[label] = label_id
                self.labels.append(label)

                filelist = os.listdir(path)
                for i, s in enumerate(filelist):
                    if i >= docs_threshold_each_label: break

                    self.resourcenames.append(os.path.join(label, s))
                    self.doclabelids.append(label_id)

                    wordlist = readTerms(os.path.join(path, s))
                    tempdocs.append(wordlist)

                    for w in wordlist:
                        if w in vocacount:
                            vocacount[w] += 1
                        else:
                            vocacount[w] = 1

        self.vocabulary = []
        self.vocabulary2id = dict()
        for w in vocacount:
            if w not in stopwords and vocacount[w] >= freq_threshold:
                self.vocabulary2id[w] = len(self.vocabulary)
                self.vocabulary.append(w)

        self.docs = []
        for doc in tempdocs:
            self.docs.append([self.vocabulary2id[w] for w in doc if w in self.vocabulary2id])

def main():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("--alpha", dest="alpha", type="float", help="parameter alpha", default=0.1)
    parser.add_option("--beta", dest="beta", type="float", help="parameter beta", default=0.01)
    parser.add_option("-k", dest="K", type="int", help="number of topics", default=10)
    parser.add_option("-i", dest="iteration", type="int", help="iteration count", default=20)
    parser.add_option("--word_freq_threshold", dest="word_freq_threshold", type="int", default=3)
    parser.add_option("--docs_threshold_each_label", dest="docs_threshold_each_label", type="int", default=100)
    (options, args) = parser.parse_args()

    corpus = Loader("./20groups/mini_newsgroups/", options.word_freq_threshold, options.docs_threshold_each_label, True)
    V = len(corpus.vocabulary)

    import lda
    model = lda.LDA(options.K, options.alpha, options.beta, corpus.docs, V, True)
    print "corpus=%d, words=%d, K=%d, a=%f, b=%f" % (len(corpus.docs), V, options.K, options.alpha, options.beta)

    pre_perp = model.perplexity()
    print "initial perplexity=%f" % pre_perp
    for i in xrange(options.iteration):
        model.inference()
        perp = model.perplexity()
        print "-%d p=%f" % (i + 1, perp)
    lda.output_word_topic_dist(model, corpus.vocabulary)

if __name__ == "__main__":
    main()
