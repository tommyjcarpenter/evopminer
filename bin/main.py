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

import nltk
from nltk.tag.stanford import POSTagger
import sys
import subprocess
import pickle

from lib.mining.product import Product
from lib.mining.results_container import ResultContainerDict
from lib.utils.mysql import DBC
from lib.utils.grapher import graph, graph_polarity_use
from lib.mining.website import Website
from lib.mining.classifier import classify_sentences
from lib.utils.text_stats import compare_freq_dists, sentiment_time_series, wrong_sentences
from lib.mining.cleaner import process_into_cleaned_sentences, fix_dates
from lib.utils.gui import RunGUI
from lib.utils.config_reader import conf_reader
from lib import rootdir, thelogger

#  ___         _ _          
# | _ \_ _ ___| (_)_ __  ___
# |  _/ '_/ -_) | | '  \(_-<
# |_| |_| \___|_|_|_|_|_/__/


#Initilize globals and results container object
results = ResultContainerDict() #init results container


#   ___                               
#  / __|_ _ __ _ _ __  _ __  __ _ _ _ 
# | (_ | '_/ _` | '  \| '  \/ _` | '_|
#  \___|_| \__,_|_|_|_|_|_|_\__,_|_|   
#Chunking grammar. See our paper for details about how this is used.                                    
stuff = "<IgnoreThisChunk|PRESENCE|VS|VB.*|DT|RB.*|PRP.*|CD|PDT|POS>*" #REMOVED IN, PDT
opphrase = "<LINTM|HINTM|NONADJOP|IMPLICITFEAT|JJ.*>+"
feat = "<POSFEAT|NEGFEAT|REGFEAT|IMPLICITFEAT>"
implicitfeat = ""
grammar = """vs-feat:    {{<VS><NEGFEAT>}}                          #no maintenence, no range anxiety
             op-feat-op  {{{3}{2}{3}}}                              #onces with an op before and after. For example, "the car is pretty much [HINTM] maintenance free.[JJ]" 
             op-feat:    {{{0}{3}{0}{2}}}                           #stuff op stuff feat, also stuff op feat, or op stuff feat
             feat-op:    {{{0}{2}{0}{3}}}                           #stuff feat stuff op: the volt sucks (lol),range drop
          """.format(stuff, implicitfeat, feat, opphrase)
myChunks = ["implicfeat","vs-feat", "op-feat-op","op-feat","feat-op"]

#this rule was deprecated after injunctions and words like the are now removed as stopwords
#op-w-feat:  {{<VS>*<NONADJOP>+<IN>+<PRP.*>*<IGN>*{2}}} #no) issues with the X, (no) issues with X, (no) issues with my voltZzs battery (ignore)


#  ___             ___                        
# | _ \_  _ _ _   | _ \__ _ _ _ __ _ _ __  ___
# |   / || | ' \  |  _/ _` | '_/ _` | '  \(_-<
# |_|_\\_,_|_||_| |_| \__,_|_| \__,_|_|_|_/__/
#THIS IS THE SECTION TO EDIT TO START A NEW RUN!

params = RunGUI()
params.root.mainloop()
UseOrDebug = params.UseOrDebug
HOTSTART = params.HOTSTART
stages = params.stages 
prod = params.product
site = ""
if prod == "Leaf":
    site = Website(Product("Leaf"),  "LeafReviews", ['Comments'], "myNissanLeafSpider", rootdir + "/" + "LeafLog.txt")
elif prod == "Volt":
    site = Website(Product("Volt"),  "VoltReviews", ["Comments"], "VoltSpider", rootdir + "/" + "voltLog.txt")
elif prod == "Tesla":
    site = Website(Product("Tesla"),  "TeslaReviews", ['Comments'], "teslaMotorsClubSpider", rootdir + "/" + "TeslaLog.txt")
elif prod == "eBike":
    site = Website(Product("eBike"),  "Survey1Preliminary", ['Comments'], None, rootdir + "/" + "ebikeLog.txt")
params.destroy()

#we initialize the tagger here because it takes awhile to load
#http://nlp.stanford.edu/software/pos-tagger-faq.shtml#h
StanfordTagger = POSTagger('lib/stanford-postagger-2014-06-16/models/english-left3words-distsim.tagger',
                           'lib/stanford-postagger-2014-06-16/stanford-postagger.jar') 

#  ___ _            _     ___                       _           
# / __| |_ __ _ _ _| |_  | _ \_ _ ___  __ ___ _____(_)_ _  __ _ 
# \__ \  _/ _` | '_|  _| |  _/ '_/ _ \/ _/ -_|_-<_-< | ' \/ _` |
# |___/\__\__,_|_|  \__| |_| |_| \___/\__\___/__/__/_|_||_\__, |
#                                                         |___/ 
    
with DBC("eBike" if prod == "eBike" else None) as dbc:     
    if 'Stage0: DataIntegrity' in stages:
        print("Stage 0: Fixing DirtyData' Issues Stuff...\n\n")
        fix_dates(site, dbc)
    
    if 'Stage1: Crawl' in stages:
        thelogger.info("Stage 1: Crawling Reviews...\n\n")   
        with open(site.log, "w") as crawlog: 
            subprocess.call([conf_reader["scrapy"]["exec_path"], 'crawl', site.spider], universal_newlines=True, stdout=crawlog, stderr=crawlog, cwd=".")  
    
    if 'Stage2: Clean' in stages:    
        thelogger.info("Stage 2: Converting Raw Reviews Into Clean Sentences...\n\n")
        process_into_cleaned_sentences(site, dbc)
    
    if 'Stage3: ProcessAndClassify' in stages:
        if HOTSTART == 1:
            thelogger.info("HOTSTARTING..")
            results = pickle.load(open(rootdir + "/" + site.product.name + "_resultsPickle.pkl","rb"))
        else:
            thelogger.info("Stage 3: Processing And Classifying Sentences...\n\n")
            cp = nltk.RegexpParser(grammar) 
            classify_sentences(site, dbc, cp,  myChunks, results, UseOrDebug, StanfordTagger)
            pickle.dump(results, open(rootdir + "/" + site.product.name + "_resultsPickle.pkl","wb")) #Dump results object for later hotstart    
            
            thelogger.info("Printing Debugging Files...\n\n")
            results.log_debugging(site, dbc)
            
            thelogger.info("Inserting Results...\n\n")
            results.insertResults(site, dbc)
            
    if 'Stage4: Graphage' in stages:
        thelogger.info("Stage 4: Graphing Results")
        graph(site, dbc, UseOrDebug, 10000000000) #second parameter only used in "use" case because without a limit the sql query takes forever
    
    if 'Stage: sentiment_time_series' in stages:
        thelogger.info("Making time series....")
        sentiment_time_series(site)
    
    if 'Stage: FrequencyDistributions' in stages: #NEW STAGE: Classifies and Graphs Frequency Distributions of phrases found in the text
        compare_freq_dists(site, 10,4,True)
        #compare_freq_dists(site, 2000,100,False)
        
    thelogger.info("Done!")
