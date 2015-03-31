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

from lib import DefSents

class Product(object):
    
    def __init__(self,name):
        self.Name = name                  #Name is an input but everything else is read from the config file with that same name
        self.Features = dict()            #dict of feature : list of syn mappings
        self.pentas = dict()
        self.quads = dict()               #stores string replacements for all double features
        self.trips = dict()               #stores string replacements for all double features
        self.dubs = dict()                #stores string replacements for all double features
        self.ImplicitFeatOps = []         #stores tag replacements for implict features
        self.NonAdjOps = []               #stores tag replacements of non adj opinion phrases
        self.AllFeatureSyns = []          #list of all synonyms for telling if a word in text is a feature word
        self.InvertedFeatures = dict()    #inverted dict to lookup a feature given a syn keyword. used later, built once for efficiency
        self.IgnoreKeywords = []
        
        configsToRead = ["conf/requiredFiles/AllConfig.txt","conf/requiredFiles/{0}Config.txt".format(self.Name)]
        for filee in configsToRead:
            with open(filee) as conf:
                for line in conf:
                    items = line.split(" ")
                    tag = items[0]
                    if tag  == "Feature" or  tag  == "POSFeature" or  tag  == "NEGFeature":
                        f = str(items[1].strip())  
                        try:
                            self.Features[f]
                        except KeyError:
                            self.Features[f] = dict()  
                            self.Features[f]["Sentiment Dictionary"] = dict()   #will be the feature specific dictionary; SentimentDictionary[feature] = dict() -> [word]: sentiment
                            self.Features[f]["Change Dict"] = dict() #stores keywords that change the feature
                        if tag  == "POSFeature":
                            self.Features[f]["Orientation"] = "POS"
                        elif tag  == "NEGFeature":
                            self.Features[f]["Orientation"] = "NEG"
                        else:
                            self.Features[f]["Orientation"] = "REG"
                        for word in items[2].split(","):
                            self.AllFeatureSyns.append(word.strip())
                            self.InvertedFeatures[word.strip()] = f    #build inverted dictionary at same time; will be useful later
                    elif tag  == "FeatureWordSentimentTriple":
                        self.Features[items[1].strip()]["Sentiment Dictionary"][items[2].strip()] = items[3].strip()
                    elif tag  == "PENTAPHRASE":
                        self.pentas["{0} {1} {2} {3} {4}".format(items[1].strip(), items[2].strip(), items[3].strip(), items[4].strip(),items[5].strip())] = items[6].strip()                 
                    elif tag  == "QUADPHRASE":
                        self.quads["{0} {1} {2} {3}".format(items[1].strip(), items[2].strip(), items[3].strip(), items[4].strip())] = items[5].strip()   
                    elif tag  == "TRIPLEPHRASE":
                        self.trips["{0} {1} {2}".format(items[1].strip(), items[2].strip(), items[3].strip())] = items[4].strip()     
                    elif tag  == "DOUBLEPHRASE":
                        self.dubs["{0} {1}".format(items[1].strip(), items[2].strip())] = items[3].strip()           
                    elif tag  ==  "NONADJOP":
                        self.NonAdjOps.append(items[1].strip())
                    elif tag  == "IMPLICITFEATOP":
                        self.ImplicitFeatOps.append(items[1].strip())
                    elif tag == "IGNOREKEYWORD":
                        self.IgnoreKeywords.append(items[1].strip())
                    elif tag == "FEATURECHANGER":
                        self.Features[items[1].strip()]["Change Dict"][items[2].strip()] = items[3].strip()
    
    
    
    def Query(self, opinion, f, valenceShifter, lowermod, highermod, presenceOf):
        """#Queries the sentiment of an opinion phrase for this feature"""
        #note highermod and lowermod wont both be on; this problem is solved in processor
        label = ""           
        
        invert = True if valenceShifter else False     
        if opinion in self.Features[f]["Sentiment Dictionary"].keys():
            label = self.Features[f]["Sentiment Dictionary"][opinion]
        elif self.Features[f]["Orientation"] == "POS":
            if highermod:#cant say (highermod or prescenseof) here because simply having a thing you want more of like "i have range" doesent mean much, but "having a bad thing" is bad so this is included in rules below
                label =  "POS"            #more/"have more" of a good thing = good
            elif lowermod: #true regardless of whether precense of;  "less of a good thing"/"have less of a good thing" both bad
                label =  "NEG"            #less of a good thing = bad
            elif valenceShifter and (presenceOf or opinion == ""):         
                label = "NEG"             #none of a good thing = bad  
                invert = False            #invert all other cases but not this   
            #return neutral for all other more complicated cases   
        elif self.Features[f]["Orientation"] == "NEG":
            if (highermod or presenceOf):
                label =  "NEG"            #more/"have more" of a bad thing = bad
            elif lowermod: #true regardless of whether precense of;  "less of a bad thing"/"have less of a bad thing" both good
                label =  "POS"            #less of a good thing = bad
            elif valenceShifter and (presenceOf or opinion == ""):         
                label = "POS"             #"i have none of a bad thing" = good  
                invert = False            #invert all other cases but not this    
        #cant use else here or if all of the inner elses fail, for example (posfeat,JJ) does not match any of the inner pos feat ifs, this wont be called. 
        if label == "":
            try:
                label =  DefSents[opinion]
            except KeyError:
                label = "NEU" #if all else fails return neutral
        
        #APPLY THE NEGATION IF APPLICABLE
        if invert and label == "POS":
            label = "NEG" 
        elif invert and label == "NEG":
            label = "POS"
             
        return label

