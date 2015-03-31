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

from datetime import date, timedelta
from lib.utils.config_reader import conf_reader
from nltk.corpus import stopwords
import logging


def Logger(name, path):
    logger=logging.getLogger('evopminer-{0}'.format(name))
    logger.setLevel(logging.DEBUG)
    handler=logging.FileHandler(path,'w')
    logger.addHandler(handler)
    return logger


thelogger = Logger("main", conf_reader["core"]["main_logpath"])
debugging_logger = Logger("debugging", conf_reader["core"]["debugging_logpath"])


#  ________________  _____ 
#  / __/ __/_  __/ / / / _ \
# _\ \/ _/  / / / /_/ / ___/
#/___/___/ /_/  \____/_/    
                                                      
rootdir = conf_reader["core"]["rootdir"]


contractionsDict = dict()
misspellingsDict = dict()
DefSents = dict()
eBikeReplacements = dict() 

        
with open("conf/requiredFiles/contractions.txt") as contractions:
    for c in contractions:
        if not c.startswith("#"):
            s = c.split(",")
            contractionsDict[s[0].strip()] = s[1].strip()
with open("conf/requiredFiles/misspellings.txt") as misspellings:
    for m in misspellings:
        if not m.startswith("#"):
            s = m.split(",")
            misspellingsDict[s[0].strip()] = s[1].strip()
with open("conf/requiredFiles/defaultSentiments.txt") as defsents: 
    for line in defsents:
        s = line.split(",")
        DefSents[s[0].strip()] = s[1].strip()


#   ___             _            _      
#  / __|___ _ _  __| |_ __ _ _ _| |_ ___
# | (__/ _ \ ' \(_-<  _/ _` | ' \  _(_-<
#  \___\___/_||_/__/\__\__,_|_||_\__/__/ 
#These define some constants used in the database                                   
sampleTableName = "Sample"
truthTableName = "GroundTruth"
sentTableName = "CleanedSentences"
resultsTableName = "Results"
tod = date.today()
agoToDates = [tod.strftime('%Y-%m-%d'),
              (tod-timedelta(weeks=1)).strftime('%Y-%m-%d'),
              (tod-timedelta(weeks=2)).strftime('%Y-%m-%d'),
              (tod-timedelta(weeks=3)).strftime('%Y-%m-%d'),
              (tod-timedelta(weeks=4)).strftime('%Y-%m-%d')]

#various important lists
lowerIntensityModifiers = ["diminished","plummeted","relief","relieved","reduced",
                           "negligible","minimal","minor","barely", "little",  "down", "infrequent", "infrequently", "fall", "fell", "dropped", "drop", 
                           "tiny", "small", "smaller", "smallest", "low", "lower","lowered", "lowest", "decrease", "decreased", "reduce", 
                           "reduced", "reduction","less", "limited", "short", "shortest", "less"]
higherIntensityModifiers = ["accelerated","far","farther","really","especially","greater","majorly","major", "awfully", "super","epic","epicly","fairly","substantial",
                            "significant","significantly", "steep","ridiculously", "quite", "incredibly", "extremely","considerable",  
                            "considerably", "pretty", "much", "very", "24/7", "often", "frequent", "frequently", "huge", "gain", "gains", 
                            "big", "bigger", "biggest", "high", "higher", "highest", "highly", "large", "larger", "largest", "increasingly", 
                            "increase", "increased", "long", "longer", "further", "more"]
valenceShifters = ["no-longer","free","myth","wish","overly","never","moot", "dont","ain't","without","w/o", "not", "rarely", "never", "zero", "no", "none","nothing", "lack", "lacks"]
#used in combination with pos and neg feature, e.g., "i have a good thing"
presenceOf = ["due-to","evidence","occurring","inevitably","felt","only","appreciable","discernible","have","had","sign","experience","expirienced","expiriencing"] 
#ignore sentences contining these phrases becuase these often indicate the user is asking a question
ignoresSentenceWide = ["say-that","how-much","do-not-know","question","wondering","is-there","are-there","are-you","does-anyone","do-you","curious","hopefully","might","may","wonder","as-long-as","if","should"] #tested
#ignore chunkscontining these phrases becuase these often indicate the user is talking about a hypethtical scario or making relative statements
ignoresWithinChunk = ["for-the","need","claims","thought",'might',"idea","could","can","may","your","helps","help","possibly",'curious','maybe','want']
#"than","you",'',"will",


#these words are filtered out of sentences
stop = set(stopwords.words('english')) | set(("the","that","are","am",'about','on','a','to','is','it','like',"much-like","there","which","not-only","any",'be'))
stop = stop - set(lowerIntensityModifiers) - set(higherIntensityModifiers)  - set(valenceShifters)  - set(presenceOf) - set(ignoresSentenceWide) - set(ignoresWithinChunk)
