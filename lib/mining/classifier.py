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

from lib import stop, valence_shifts, ignoresSentenceWide, lowerIntensityModifiers, higherIntensityModifiers, presence, chunk_ignores             
import nltk
import re
from lib import thelogger


def pre_tag_operations(sent_str, product_object):
    """helper function to preprocess sents prior to POS tagging, like replacing multi word phrases"""
    
    #first replace multi word phrases because some contain otherwise-would-be stopwords
    for pf in product_object.pentas.keys():
        sent_str = sent_str.replace(pf, product_object.pentas[pf])           
    for qf in product_object.quads.keys():
        sent_str = sent_str.replace(qf, product_object.quads[qf])  
    for tf in product_object.trips.keys():
        sent_str = sent_str.replace(tf, product_object.trips[tf]) 
    for df in product_object.dubs.keys():
        sent_str = sent_str.replace(df, product_object.dubs[df])    
    
    #then remove stopwords
    newtokenized = [word for word in nltk.word_tokenize(sent_str.rstrip(".").rstrip("?").rstrip("!")) if word not in stop]   
    sent_str2 = ""
    for w in newtokenized:
       sent_str2 += w + " " 
    sent_str2.strip()
    
    #then replace again for phrases that were defined without stopwords, such as "loss-capacity" (was loss-of-capacity)
    for pf in product_object.pentas.keys():
        sent_str2 = sent_str2.replace(pf, product_object.pentas[pf])           
    for qf in product_object.quads.keys():
        sent_str2 = sent_str2.replace(qf, product_object.quads[qf])  
    for tf in product_object.trips.keys():
        sent_str2 = sent_str2.replace(tf, product_object.trips[tf]) 
    for df in product_object.dubs.keys():
        sent_str2 = sent_str2.replace(df, product_object.dubs[df])    
        
    #tokenize
    tokenized = nltk.word_tokenize(sent_str2.strip())
    if tokenized == []:
        tokenized = ["NULL"] #SEE THE LONG COMMENT ON THE  assert STATEMENT BELOW FOR EXAPLANATION
    return tokenized


def post_tag_operations(sent_tagged, product_object):
    """helper function to replace words with the tags used in the chunking grammar. This happens prior to chunking"""
    ignore_sent = False #we will ignore the sentence if it does not meet certain criteria (like having no opinion etc)
    
    #NOW FIX THE TAGS
    newsent = [] 
    for t in sent_tagged:
        newtup = t
        w = t[0]
        #implicits would be caught in IMPLICITFEAT and AllFeatureSyns, so check Implicits first!!!
        if w in product_object.implicit_ops:
            newtup = ((w, "IMPLICITFEAT"))
        elif w in product_object.feature_syns:
            orientation = product_object.features[product_object.inverted_feats[w]]["Orientation"] #use inverse dict to get feat, then get orientation
            newtup = ((w, orientation + "FEAT"))
        elif w in product_object.non_adj_ops:
            newtup = ((w, "NONADJOP"))
        elif w in valence_shifts:
            newtup = ((w, "VS"))
        elif w in lowerIntensityModifiers:
            newtup = ((w, "LINTM"))
        elif w in higherIntensityModifiers:
            newtup = ((w, "HINTM"))
        elif w in presence:
            newtup = ((w, "PRESENCE"))
        elif w in chunk_ignores:
            newtup = ((w, "ignore_chunk"))
        elif w in ignoresSentenceWide or w in product_object.ignores:
            ignore_sent = True
        newsent.append(newtup)
    
    #very long sentences are written poorly usually, so ignore long sentences. 
    #Note this 16 is after stopwrods removed so the original sent even longer
    return (ignore_sent or len(newsent) > 16), newsent


def process_chunk(site,ch,sent):
    """process a chunk; get its feature and classify the sentiment of the opinion referring to the feature"""
       
    opinions = []
    opspos = []
    closestOp = ""
    valence_shifter = False
    lowermod = False
    highermod = False
    presence = False
    lowermodPos = -1
    highermodPos = -1
    count = 0
    ignore_chunk = False
    the_feat = ""
    featpos = ""
    the_words = []
    for tup in ch.rhs(): 
        theword = tup[0]
        the_words.append(theword)
        thepos = tup[1]
        optags = ["JJ","JJR","JJS","NONADJOP","IMPLICITFEAT"]
        feats = ["REGFEAT", "NEGFEAT", "POSFEAT","IMPLICITFEAT"]
         
        if (thepos in feats):
            the_feat = site.product.inverted_feats[theword] #need to reverse lookup the synonym to get the actual feature
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
            valence_shifter = False if valence_shifter else True
        elif (thepos == "PRESENCE"): #need to deal with double negatives
            presence = True
        elif (thepos == "ignore_chunk"):
            ignore_chunk = True
        count += 1
          
    #Tried making a POS tag for feature changers, but this does not work: sometimes feature changers
    #are also the opinion phrase, like "the tesla is EXPENSIVE(featurechanger)", but sometimes it is near the opinion phrase, 
    #like "the Tesla LOOKS(featurechanger) great". So what we will do is enumerate all feature changers for the feature found,
    #and if a feature changer for that feature exists in the chunk, regardless of whether its the opinion or elsewhere, change the feat.
    for k in site.product.features[the_feat]["Change Dict"].keys():
        if k in the_words:
            the_feat = site.product.features[the_feat]["Change Dict"][k]
            break
                        
    #fix inconsistencies with both lower and upper mods
    if lowermod and highermod:
        if highermodPos+1 == lowermodPos or lowermodPos+1 == highermodPos:
            highermod = False #very little... -> little. (op-feat needing/VBG very/HINTM little/LINTM maintenance/NEGFEAT)
           
    #QUERY THE SENTIMENT     
    if sent.endswith(("?","?.","?..","?...")) or ignore_chunk:
        label = "NEU"    # IGNORE QUESTIONS, sentences containing subjects we wish to ignore
    elif len(opinions) > 0:
        score = 0
        for i in range (0,len(opinions)):
            dist = abs(opspos[i]-featpos)
            
            thishighermod = highermod
            thislowermod = lowermod
            thisvalence_shifter = valence_shifter
            
            # (feat-op makes/VBZ car/REGFEAT very/HINTM affordable/JJ))  was classified as NEG
            if highermod and (highermodPos+1 == opspos[i]):
                thishighermod = False #really great -> great , really bad -> bad 
            elif lowermod and (lowermodPos+1 == opspos[i]):
                thislowermod = False #less bad = good, less good = bad   
                thisvalence_shifter = True
            
            thislabel = site.product.Query(opinions[i], the_feat, thisvalence_shifter, thislowermod, thishighermod, presence)
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
        label = site.product.Query("", the_feat, valence_shifter, lowermod, highermod, presence)     
    return the_feat, label   
    

def classify_sentences(site, dbc, parser, myChunks, results, UseOrDebug, tagger):
    """get each sentence, get features, find adjectives, classify, add to results, repeat"""

    queue_counter = 0 
    total_counter  = 0
    sent_queue = dict()
    sent_queue['hsh'] = []
    sent_queue['sents'] = []
    sent_queue['tokenizedsents'] = []
    sent_queue['taggedsents'] = []
              
    for hsh, sent in dbc.gen_cleaned_sents(site.product.name, UseOrDebug):
        sent_queue['hsh'].append(hsh)
        sent_queue['sents'].append(sent)
        sent_queue['tokenizedsents'].append(pre_tag_operations(sent, site.product))
        
        #had to move these here so that the size of sent_queue['tokenizedsents'] does not grow to 501 before the queue check of 500 is performed
        queue_counter+=1
        total_counter  +=1
        
        #tag 500 at a time because calling a java instance wrapper each time is SLOW
        if queue_counter == 500 or hsh==None:  
            thelogger.info("Sents Processed So Far: {0}".format(total_counter ))
            sent_queue['taggedsents'] = tagger.tag_sents(sent_queue['tokenizedsents'])
            
            """the following assertion ensures batch_tag returned a tagged output for every input in sent_queue['tokenizedsents']. 
            if this fails the size of sent_queue['taggedsents'] < (sent_queue['tokenizedsents'] == size of sent_queue['hsh']), so then we have no idea what taggedSents 
            match up with what hashes. The problem is we dont know what input number to batch tag did not return a value so we cant skip that hash. 
            after much debugging, I believe the only times batch_tag does not return a value for every input is if one of the inputs are blank (== [])
            which can happen if the sentence was short and contained only stop words due to punctuation errors or other reasons, which is why the 
            pre_tag_operations function now returns ["NULL"] if it would return []. Hence, with that change made in pre_tag_operations, if this assertion fails, somethings really wrong.
            IMO, the stanfordTagger is bugged and should return an empty return [] instead of not returning anyhting on empty input"""
            assert len(sent_queue['taggedsents']) == len(sent_queue['tokenizedsents']) 
            
            for K in range(0,queue_counter):
                ignore, sent_tagged = post_tag_operations(sent_queue['taggedsents'][K],site.product)
                    
                #parse the sentence into its chunks. then analysize the chunks
                parse = parser.parse(sent_tagged)
                chunks = parse.productions()
                
                #sentences with multiple labels for the same feature should be fixed as specified in detailed comments below. Need this dict
                chunk_feat_labels = dict()
                
                #process each chunk seperately      
                for ch in chunks:  
                    #parse the chunks LHS to determine if its a chunk we need to worry about.
                    #only consider the tups that are our chunks
                    LHS = ch.lhs().__repr__().split("->")[0].strip()
                    if LHS in myChunks:  
                       the_feat, label = process_chunk(site,ch,sent_queue['sents'][K])
                       if ignore:
                           label = "NEU" #set label to neutral for all questions, hugely long setnences, etc. see ignore in post_tag_operations function
                       if the_feat in chunk_feat_labels:
                           chunk_feat_labels[the_feat].append(label)
                       else:
                           chunk_feat_labels[the_feat] = [label]
                    
                #sentences with multiple labels for the same feature are added as follows:
                # multiple pos -> just one pos, multiple neg -> just one neg,  pos and neutral -> pos, neg and neutral -> neg, pos and a neg -> neu 
                #NOTE you could also implement some kind of averaging or weighting here for this case
                for f in chunk_feat_labels.keys():
                    if "POS" in chunk_feat_labels[f] and "NEG" not in chunk_feat_labels[f]:  
                        results.add_result(site.product.name, f, "POS", sent_queue['hsh'][K], sent_queue['sents'][K], parse)
                    elif "POS" not in chunk_feat_labels[f] and "NEG" in chunk_feat_labels[f]:          
                        results.add_result(site.product.name, f, "NEG", sent_queue['hsh'][K], sent_queue['sents'][K], parse)
                    else:                                                                           
                        results.add_result(site.product.name, f, "NEU", sent_queue['hsh'][K], sent_queue['sents'][K], parse)

            sent_queue['hsh'] = []
            sent_queue['sents'] = []
            sent_queue['tokenizedsents'] = []
            sent_queue['taggedsents'] = []
            queue_counter = 0

