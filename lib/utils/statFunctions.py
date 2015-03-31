"""
Copyright (c) 2013 Tommy Carpenter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import division # enables FPD
from operator import itemgetter
import nltk
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.collocations import *
from nltk.tokenize import RegexpTokenizer
from nltk.collocations import *
from nltk.corpus import wordnet
from grapher import plotFD
from databaseConnector import *

from lib import rootdir, stop, debugging_logger, ignoresWithinChunk, sentTableName, resultsTableName, truthTableName             


#this is only used for unigram and bigram graph coloring! This really needs to be renamed and reworked. 
def getPolarity(term):
    """tries to find the color of a term using sentiment dictionary. 
       if it is a bigram, it first sees if the first term is defined, then tries the second"""
    if not isinstance(term, tuple):
       try:
           s = DefSents[term]
       except KeyError:
           s = 'NEU'  
    else:
        try:
           s = DefSents[term[0]]
        except KeyError:
           try: 
               s = DefSents[term[1]]
           except KeyError:
               s = 'NEU'  
    return s


def frequencyDistributionComparison(currSite, smin,bmin,allowNeutrals):
    """analyzes the frequencies of words and bigrams found in all of the survey questions.
       four parameters are the min and max frequencies shown for single words and bigrams"""
    #words to not consider when doing frequency counts

    stop_single = set(("likely","much","many","cycling","bicycle","bicycles","cycle","dont","not","more","way","less","car","cars","bike","bikes","look","cant","arent","time","walk",
                       "walking","never","really","main","biking","kw","feel","quite","taking","trying","powered","compared",'vehicle','often','means','always',"potential",
                       'wonder','potentially','probably','ride','long','people',"possibly","drive","provide","daily","places","day","town","motorcycles","road","roads",
                       "ebike","ebikes","waterloo"))
    
    corpus = ""
    for i in currSite.dbc.SQLSelectGenerator("select {0} from {1} limit 10000".format(currSite.FieldsToPull[0], currSite.Table)):
        corpus += i[0] + " "

    #get list of all words as split by regex
    tokenizer = RegexpTokenizer('[a-z]+')
    words = tokenizer.tokenize(corpus.replace("\""," ").replace("\'","").lower())
    
    #take the original words and produce a list of filtered words
    filtered_words_single  = []
    filtered_words_bigrams  = []

    for w in words:
        word = w.strip()
        for r in sorted(eBikeReplacements.keys(),reverse=True):
            if word == r:
                word = eBikeReplacements[r]
                break
        if word not in stop and word != '' and word not in ignoresWithinChunk:
            filtered_words_bigrams.append(word)
            if word not in stop_single:
                filtered_words_single.append(word)
    fd = nltk.FreqDist(filtered_words_single)
    bigram_fd = nltk.FreqDist(nltk.bigrams(filtered_words_bigrams))   
    
    #SET UP THE PLOT
    cd = dict()
    cd["NEU"] = 'blue'
    cd["NEG"] = 'red'
    cd["POS"] = 'green'
    
    fds = [fd,bigram_fd]
    mins = [smin,bmin]
    
    for i in range(0,len(fds)):
        Xs = []
        Ys = []
        Xlabs = []
        Xcols = []
        count = 0                            
        for k,v in sorted(fds[i].items(), key=itemgetter(1), reverse=True):
           if v >= mins[i]:
               s = getPolarity(k)
               if s != "NEU" or allowNeutrals == True: 
                   Xs.append(count)
                   Ys.append(v)
                   Xcols.append(cd[s])
                   Xlabs.append(k)
                   count += 1
               
        plotFD(Xs,Ys,Xlabs,Xcols,count)
        
 
#returns length of text in words
def getTextLength(fdist):
    return fdist.N()
   
#returns the set of unique words of a entencereadertext and the count of this set for later use    
def getUniquesSetAndCount(fdist):    
    return fdist.keys(), fdist.B()

#top X used words. GENERATOR FUNCTION. 
def genTopXUsedWords(fdist, length, X):
    for tup in fdist.items()[:X]:
        yield (tup[0], 100*tup[1]/length)

def TopXUsedWords(fdist, length, X):
    return map(lambda tup: (tup[0], 100*tup[1]/length), fdist.items())[:X] #replace (char, count) with (char, freq)
       
#top X bigrams
def TopXBigrams(words, X, filt):
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    #trigram_measures = nltk.collocations.TrigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(words)
    finder.apply_freq_filter(filt)
    return finder.nbest(bigram_measures.pmi, X)

#top X trigrams
def TopXTrigrams(words, X, filt):
    trigram_measures = nltk.collocations.TrigramAssocMeasures()
    finder = TrigramCollocationFinder.from_words(words)
    finder.apply_freq_filter(filt)
    return finder.nbest(trigram_measures.pmi, X)

#concordance with some words
def printConcordance(words, target):
    text = nltk.Text(words)
    text.concordance(target, 30, 1000) #word, width of sentence, lines

#does some stuff with wordnet synsets
def syn(words):
    for r in range(0, 100):
        print(words[r])
        synsets = wordnet.synsets(words[r])
        if len(synsets) > 0:
            print(synsets[0].hyponyms())
     # for s in wordnet.synsets(words[r]):
        #    print(s.lemma_names)
        print("\n")



#NOTE: this function was for a fellow student and you will not need to use it (as is now)
#this is used to generate a time series of sentiments over time. 
def GenerateTimeSeries(curSite):
        
    file1 = open(rootdir + "/timeseries/" + curSite.ProdObj.Name + "_SentimentTimeSeries.txt","w")     
    file2 = open(rootdir + "/timeseries/" + curSite.ProdObj.Name + "_GeneralTimeSeries.txt","w")     
    file1.write("start,end(inclusive),feature,num pos, num neu, num neg, total\n")
    file2.write("start,end(inclusive),SentenceCount,SentimentCount\n")

    begin= datetime.fromtimestamp(1259643600) #first ever comment as of now is dec 2009
    end = begin+relativedelta(months=1)-relativedelta(days=1)  #end is inclusive

    while begin < datetime.now():
        #MAKE FILE 2    
        stmt = 'SELECT count(*) '\
                'from {sent} '\
                'WHERE Product = "{prod}" and Date BETWEEN "{st}" and "{en}"'.format(sent=sentTableName, prod=curSite.ProdObj.Name, st=begin.strftime('%Y-%m-%d'),en=end.strftime('%Y-%m-%d'))
        
        for d in curSite.dbc.SQLSelectGenerator(stmt):
            totsentences = d[0]
                    
        stmt = 'SELECT count(*) ' \
               'from {res} INNER JOIN {sent} \n '\
               'ON {res}.ProdDateSentHash = {sent}.ProdDateSentHash ' \
               'WHERE {sent}.Product = "{prod}" and {sent}.Date BETWEEN "{b}" and "{e}" \n'.format(sent=sentTableName,prod=curSite.ProdObj.Name,res=resultsTableName,b=begin.strftime('%Y-%m-%d'),e=end.strftime('%Y-%m-%d'))

        for d in curSite.dbc.SQLSelectGenerator(stmt):
            sentsWithFeatures = d[0]
        
        #WRITE FILE 2
        file2.write(begin.strftime('%Y-%m-%d') + "," + end.strftime('%Y-%m-%d') + "," + str(totsentences) + "," + str(sentsWithFeatures) + "\n")
        
        #MAKE FILE 1
        stmt = 'SELECT {res}.Feature, {res}.Label ' \
               'from {res} INNER JOIN {sent} \n '\
               'ON {res}.ProdDateSentHash = {sent}.ProdDateSentHash ' \
               'WHERE {sent}.Product = "{prod}" and {sent}.Date BETWEEN "{b}" and "{e}"'.format(sent=sentTableName,prod=curSite.ProdObj.Name,res=resultsTableName,b=begin.strftime('%Y-%m-%d'),e=end.strftime('%Y-%m-%d'))
            
        #WRITE FILE 1
        res = dict()
        for feat in curSite.ProdObj.Features.keys():
            res[feat] = dict()
            res[feat]["POS"] = 0
            res[feat]["NEU"] = 0
            res[feat]["NEG"] = 0     
            res[feat]["TOT"] = 0          

        for d in curSite.dbc.SQLSelectGenerator(stmt):
            f = str(d[0])
            c = str(d[1])
            res[f][c] += 1
            res[f]["TOT"] += 1
        
        for f in res.keys():
            file1.write(begin.strftime('%Y-%m-%d') + "," + end.strftime('%Y-%m-%d') + "," + f + "," + str(res[f]["POS"]) + "," + str(res[f]["NEU"]) + "," + str(res[f]["NEG"]) + "," + str(res[f]["TOT"]) + "\n") 
        begin=begin+relativedelta(months=1)
        end = begin+relativedelta(months=1)-relativedelta(days=1)  #end is inclujsive

    file1.close()
    file2.close()

#prints a query to show sentences that were incorrectly classified w.r.t. ground truth
def showWrongSentences(currSite):
    debugging_logger.debug("Computing Wrong Sentences...\n\n")     
    stmt = 'SELECT {truth}.* \n'\
            'FROM {truth} \n'\
            'INNER JOIN {res} ON {truth}.sentenceid = {res}.sentenceid and {truth}.Product = {res}.Product and {truth}.Feature = {res}.Feature \n'\
            'WHERE {truth}.Label is not {res}.Label and {res}.Product = "{prod}" and {truth}.Product = "{prod}"'.format(res=resultsTableName,truth=truthTableName,prod=currSite.ProdObj.Name)
    #TODO: something useful...
    debugging_logger.debug(stmt)
    raise NotImplemented("showWrongSentences not implemented!")
        

        

