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

from lib import stop, valenceShifters, ignoresSentenceWide, lowerIntensityModifiers, higherIntensityModifiers, presenceOf, ignoresWithinChunk             
import nltk
import re
from lib import thelogger


def pretagging(stringSentence, productObject):
    """helper function to preprocess sents prior to POS tagging, like replacing multi word phrases"""
    
    #first replace multi word phrases because some contain otherwise-would-be stopwords
    for pf in productObject.pentas.keys():
        stringSentence = stringSentence.replace(pf, productObject.pentas[pf])           
    for qf in productObject.quads.keys():
        stringSentence = stringSentence.replace(qf, productObject.quads[qf])  
    for tf in productObject.trips.keys():
        stringSentence = stringSentence.replace(tf, productObject.trips[tf]) 
    for df in productObject.dubs.keys():
        stringSentence = stringSentence.replace(df, productObject.dubs[df])    
    
    #then remove stopwords
    newtokenized = [word for word in nltk.word_tokenize(stringSentence.rstrip(".").rstrip("?").rstrip("!")) if word not in stop]   
    stringSentence2 = ""
    for w in newtokenized:
       stringSentence2 += w + " " 
    stringSentence2.strip()
    
    #then replace again for phrases that were defined without stopwords, such as "loss-capacity" (was loss-of-capacity)
    for pf in productObject.pentas.keys():
        stringSentence2 = stringSentence2.replace(pf, productObject.pentas[pf])           
    for qf in productObject.quads.keys():
        stringSentence2 = stringSentence2.replace(qf, productObject.quads[qf])  
    for tf in productObject.trips.keys():
        stringSentence2 = stringSentence2.replace(tf, productObject.trips[tf]) 
    for df in productObject.dubs.keys():
        stringSentence2 = stringSentence2.replace(df, productObject.dubs[df])    
        
    #tokenize
    tokenized = nltk.word_tokenize(stringSentence2.strip())
    if tokenized == []:
        tokenized = ["NULL"] #SEE THE LONG COMMENT ON THE  assert STATEMENT BELOW FOR EXAPLANATION
    return tokenized





def posttagging(taggedSentence, productObject):
    """helper function to replace words with the tags used in the chunking grammar. This happens prior to chunking"""
    ignoreSENT = False #we will ignore the sentence if it does not meet certain criteria (like having no opinion etc)
    
    #NOW FIX THE TAGS
    newsent = [] 
    for t in taggedSentence:
        newtup = t
        w = t[0]
        #implicits would be caught in IMPLICITFEAT and AllFeatureSyns, so check Implicits first!!!
        if w in productObject.ImplicitFeatOps:
            newtup = ((w, "IMPLICITFEAT"))
        elif w in productObject.AllFeatureSyns:
            orientation = productObject.Features[productObject.InvertedFeatures[w]]["Orientation"] #use inverse dict to get feat, then get orientation
            newtup = ((w, orientation + "FEAT"))
        elif w in productObject.NonAdjOps:
            newtup = ((w, "NONADJOP"))
        elif w in valenceShifters:
            newtup = ((w, "VS"))
        elif w in lowerIntensityModifiers:
            newtup = ((w, "LINTM"))
        elif w in higherIntensityModifiers:
            newtup = ((w, "HINTM"))
        elif w in presenceOf:
            newtup = ((w, "PRESENCE"))
        elif w in ignoresWithinChunk:
            newtup = ((w, "IgnoreThisChunk"))
        elif w in ignoresSentenceWide or w in productObject.IgnoreKeywords:
            ignoreSENT = True
        newsent.append(newtup)
    
    #very long sentences are written poorly usually, so ignore long sentences. 
    #Note this 16 is after stopwrods removed so the original sent even longer
    return (ignoreSENT or len(newsent) > 16), newsent


def processChunk(currSite,ch,sent):
    """process a chunk; get its feature and classify the sentiment of the opinion referring to the feature"""
       
    opinions = []
    opspos = []
    closestOp = ""
    valenceShifter = False
    lowermod = False
    highermod = False
    presenceOf = False
    lowermodPos = -1
    highermodPos = -1
    count = 0
    ignoreThisChunk = False
    theFeat = ""
    featpos = ""
    the_words = []
    for tup in ch.rhs(): 
        theword = tup[0]
        the_words.append(theword)
        thepos = tup[1]
        optags = ["JJ","JJR","JJS","NONADJOP","IMPLICITFEAT"]
        feats = ["REGFEAT", "NEGFEAT", "POSFEAT","IMPLICITFEAT"]
         
        if (thepos in feats):
            theFeat = currSite.ProdObj.InvertedFeatures[theword] #need to reverse lookup the synonym to get the actual feature
            featpos = count
        elif (thepos in optags):
            opinions.append(theword)
            opspos.append(count)
        elif(thepos == "LINTM"):
            lowermod = True
            lowermodPos = count
        elif(thepos == "HINTM"):
            highermod = True
            highermodPos = count
        elif (thepos == "VS"): #need to deal with double negatives
            valenceShifter = False if valenceShifter else True
        elif (thepos == "PRESENCE"): #need to deal with double negatives
            presenceOf = True
        elif (thepos == "IgnoreThisChunk"):
            ignoreThisChunk = True
        count += 1
          
    #Tried making a POS tag for feature changers, but this does not work: sometimes feature changers
    #are also the opinion phrase, like "the tesla is EXPENSIVE(featurechanger)", but sometimes it is near the opinion phrase, 
    #like "the Tesla LOOKS(featurechanger) great". So what we will do is enumerate all feature changers for the feature found,
    #and if a feature changer for that feature exists in the chunk, regardless of whether its the opinion or elsewhere, change the feat.
    for k in currSite.ProdObj.Features[theFeat]["Change Dict"].keys():
        if k in the_words:
            theFeat = currSite.ProdObj.Features[theFeat]["Change Dict"][k]
            break
                        
    #fix inconsistencies with both lower and upper mods
    if lowermod and highermod:
        if highermodPos+1 == lowermodPos or lowermodPos+1 == highermodPos:
            highermod = False #very little... -> little. (op-feat needing/VBG very/HINTM little/LINTM maintenance/NEGFEAT)
        #elif l:
         #   lowermod = False #down/LINTM quite/HINTM
            
            
            
                    
    #QUERY THE SENTIMENT     
    if sent.endswith(("?","?.","?..","?...")) or ignoreThisChunk:
        label = "NEU"    # IGNORE QUESTIONS, sentences containing subjects we wish to ignore
    elif len(opinions) > 0:
        score = 0
        for i in range (0,len(opinions)):
            dist = abs(opspos[i]-featpos)
            
            thishighermod = highermod
            thislowermod = lowermod
            thisvalenceShifter = valenceShifter
            
            # (feat-op makes/VBZ car/REGFEAT very/HINTM affordable/JJ))  was classified as NEG
            if highermod and (highermodPos+1 == opspos[i]):
                thishighermod = False #really great -> great , really bad -> bad 
            elif lowermod and (lowermodPos+1 == opspos[i]):
                thislowermod = False #less bad = good, less good = bad   
                thisvalenceShifter = True
            
            thislabel = currSite.ProdObj.Query(opinions[i], theFeat, thisvalenceShifter, thislowermod, thishighermod, presenceOf)
            if dist == 0: #happens for implict feats
                dist = 1   
            if thislabel == "POS":
                score += 1.0/dist
            elif thislabel == "NEG":
                score += -1.0/dist
        if score == 0:
            label = "NEU"
        elif score < 0:
            label = "NEG"
        else:
            label = "POS"
    elif len(opinions) == 0:
        label = currSite.ProdObj.Query("", theFeat, valenceShifter, lowermod, highermod, presenceOf)     
    return theFeat, label   
    

def processSentences(currSite, dbc, parser, myChunks, resultsContainer, UseOrDebug, tagger):
    """get each sentence, get features, find adjectives, classify, add to results, repeat"""

    queueCounter = 0 
    totCounter = 0
    sentQ = dict()
    sentQ['hsh'] = []
    sentQ['sents'] = []
    sentQ['tokenizedsents'] = []
    sentQ['taggedsents'] = []
              
    for hsh, sent in dbc.getCleanSentencesGenerator(currSite.ProdObj.Name, UseOrDebug):
        sentQ['hsh'].append(hsh)
        sentQ['sents'].append(sent)
        sentQ['tokenizedsents'].append(pretagging(sent, currSite.ProdObj))
        
        #had to move these here so that the size of sentQ['tokenizedsents'] does not grow to 501 before the queue check of 500 is performed
        queueCounter+=1
        totCounter +=1
        
        #tag 500 at a time because calling a java instance wrapper each time is SLOW
        if queueCounter == 500 or hsh==None:  
            thelogger.info("Sents Processed So Far: {0}".format(totCounter))
            sentQ['taggedsents'] = tagger.tag_sents(sentQ['tokenizedsents'])
            
            """the following assertion ensures batch_tag returned a tagged output for every input in sentQ['tokenizedsents']. 
            if this fails the size of sentQ['taggedsents'] < (sentQ['tokenizedsents'] == size of sentQ['hsh']), so then we have no idea what taggedSents 
            match up with what hashes. The problem is we dont know what input number to batch tag did not return a value so we cant skip that hash. 
            after much debugging, I believe the only times batch_tag does not return a value for every input is if one of the inputs are blank (== [])
            which can happen if the sentence was short and contained only stop words due to punctuation errors or other reasons, which is why the 
            pretagging function now returns ["NULL"] if it would return []. Hence, with that change made in pretagging, if this assertion fails, somethings really wrong.
            IMO, the stanfordTagger is bugged and should return an empty return [] instead of not returning anyhting on empty input"""
            assert len(sentQ['taggedsents']) == len(sentQ['tokenizedsents']) 
            
            for K in range(0,queueCounter):
                ignore, taggedSentence = posttagging(sentQ['taggedsents'][K],currSite.ProdObj)
                    
                #parse the sentence into its chunks. then analysize the chunks
                parse = parser.parse(taggedSentence)
                chunks = parse.productions()
                
                #sentences with multiple labels for the same feature should be fixed as specified in detailed comments below. Need this dict
                chunkFeatLabels = dict()
                
                #process each chunk seperately      
                for ch in chunks:  
                    #parse the chunks LHS to determine if its a chunk we need to worry about.
                    #only consider the tups that are our chunks
                    LHS = ch.lhs().__repr__().split("->")[0].strip()
                    if LHS in myChunks:  
                       theFeat, label = processChunk(currSite,ch,sentQ['sents'][K])
                       if ignore:
                           label = "NEU" #set label to neutral for all questions, hugely long setnences, etc. see ignore in posttagging function
                       try:
                           chunkFeatLabels[theFeat].append(label)
                       except KeyError:
                           chunkFeatLabels[theFeat] = [label]
                    
                #sentences with multiple labels for the same feature are added as follows:
                # multiple pos -> just one pos, multiple neg -> just one neg,  pos and neutral -> pos, neg and neutral -> neg, pos and a neg -> neu 
                #NOTE you could also implement some kind of averaging or weighting here for this case
                for f in chunkFeatLabels.keys():
                    if "POS" in chunkFeatLabels[f] and "NEG" not in chunkFeatLabels[f]:  
                        resultsContainer.addResult(currSite.ProdObj.Name, f, "POS", sentQ['hsh'][K], sentQ['sents'][K], parse)
                    elif "POS" not in chunkFeatLabels[f] and "NEG" in chunkFeatLabels[f]:          
                        resultsContainer.addResult(currSite.ProdObj.Name, f, "NEG", sentQ['hsh'][K], sentQ['sents'][K], parse)
                    else:                                                                           
                        resultsContainer.addResult(currSite.ProdObj.Name, f, "NEU", sentQ['hsh'][K], sentQ['sents'][K], parse)

            sentQ['hsh'] = []
            sentQ['sents'] = []
            sentQ['tokenizedsents'] = []
            sentQ['taggedsents'] = []
            queueCounter = 0

