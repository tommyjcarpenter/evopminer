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

from lib import rootdir, debugging_logger, thelogger 
from lib import resultsTableName 


#container for one product, feature pair
class FeatureWiseResult(object): 
    def __init__(self):
        self.hashes = []
        self.sents = []
        self.parses = []

    
#holds containers for multiple products                    
class ResultContainerDict(object): 
    def __init__(self):
        self.ContainerDict = dict() #dict of dicts
        
    #add a sentence to "POS" or "NEG"    
    def addResult(self, product, feature, pOrN, hsh, sentence, parse):
        assert (pOrN == "POS" or pOrN == "NEG" or pOrN == "NEU"),  "pOrN Fail" 

        #if key doesn't exist add it
        try:
            self.ContainerDict[product] #O(1)
        except KeyError:
            self.ContainerDict[product] = dict() 
        try:
           self.ContainerDict[product][feature]
        except: 
            self.ContainerDict[product][feature] = dict()
            self.ContainerDict[product][feature]["POS"] = FeatureWiseResult() 
            self.ContainerDict[product][feature]["NEG"] = FeatureWiseResult() 
            self.ContainerDict[product][feature]["NEU"] = FeatureWiseResult() 

        #add the result
        self.ContainerDict[product][feature][pOrN].hashes.append(hsh)
        self.ContainerDict[product][feature][pOrN].sents.append(sentence)
        self.ContainerDict[product][feature][pOrN].parses.append(parse)

    
    #log debuggung info a file that can be used for debugging
    def log_debugging(self, currSite, dbc):
        debugging_logger.debug("logging debugging info for: {0}".format(currSite.ProdObj.Name))
        
        gtdict = dbc.pullAllHashesInGTForProduct(currSite.ProdObj.Name) #get all the IDs that are in GT for this product. 
        
        numpos = 0
        numneg = 0
        numneu = 0
        
        #write the files
        for prod in self.ContainerDict.keys():
            for feat in self.ContainerDict[prod].keys():
                for pol in self.ContainerDict[prod][feat].keys():
                    num = len(self.ContainerDict[prod][feat][pol].hashes)
                    if pol == "POS":
                        numpos += num
                    elif pol == "NEU":
                        numneu += num
                    else:
                        numneg += num

                    for p in range(0, num):
                        thishash = self.ContainerDict[prod][feat][pol].hashes[p]
                        debugging_logger.debug("Label: {polarity}, F: {ft}, Hash: {hsh}\n".format(polarity=pol,ft=feat,hsh=thishash))
                        try:
                            if gtdict[thishash][feat] != pol:
                                debugging_logger.debug('DOES NOT MATCH; GT IS {0}\n'.format(gtdict[thishash][feat]))
                        except KeyError:
                            debugging_logger.debug('\n NOT IN GROUND TRUTH FOR THIS FEAT\n')
                        debugging_logger.debug('("{hsh}","{polarity}","{ft}"),\n'.format(polarity=pol,hsh=thishash,ft=feat))
                        debugging_logger.debug('{sent} \n {parse} \n\n\n'.format(sent=str(self.ContainerDict[prod][feat][pol].sents[p]),parse=str(self.ContainerDict[prod][feat][pol].parses[p])))

        #log statistics
        tot = numpos + numneu + numneg
        debugging_logger.debug("Total Sentences With Features: {0}\n".format(tot))
        debugging_logger.debug("Pos Sentences: {0}\n".format(numpos))
        debugging_logger.debug("Neu Sentences: {0}\n".format(numneu))
        debugging_logger.debug("Neg Sentences: {0}\n\n\n".format(numneg))


     
    def insertResults(self, currSite, dbc):
        """produce prod, feature based summary"""
        insert_tups = []
        
        dbc.deleteResultsForProduct(currSite.ProdObj.Name)
        resultsQ = []
        for prod in self.ContainerDict.keys():
            for feat in self.ContainerDict[prod].keys():
                for pol in self.ContainerDict[prod][feat].keys():
                    num = len(self.ContainerDict[prod][feat][pol].hashes)
                    for p in range(0, num):
                        insert_tups.append((self.ContainerDict[prod][feat][pol].hashes[p], feat, pol, str(p+1), str(num)))
                                
        thelogger.info("Inserting result data...")            
        dbc.bulk_insert("INSERT IGNORE INTO {res}".format(res=resultsTableName), 
                        insert_tups,
                        "")    
    
    
    
    
    
    
    
    
    
        

        
                    
