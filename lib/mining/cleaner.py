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

"""
This module is meant to clean text/sentences prior to classification.
"""


import nltk
from nltk.collocations import *
import re
from nltk.corpus import stopwords
import hashlib
from datetime import date, timedelta
from lib import misspellingsDict, contractionsDict, sent_table, truth_table, agoToDates, thelogger
from lib.utils import string_functions

def process_into_cleaned_sentences(site, dbc): 
    """takes the raw mined reviews, cleans them into sentences, and then puts them back into DB"""
    thelogger.info("Selecting/Cleaning Data..\n")
    tups = [] #expects (date, text) pairs, or in the case of ebikes, (date, text, questionNum, responderID) pairs
        
    if site.product.name == "eBike":
        """ASSUMED FORMAT: date, comments, QuestionNumber, ResponseNumber"""
        #get the blob of uncleaned text and clean, insert it
        stmt = 'SELECT Date, '
        for f in range(0, len(site.fields)):
            stmt += site.fields[f]
            stmt += ', ' if (f < len(site.fields) -1) else ' ' #add comma if not last field
            stmt += ', Question, responseNumber from ' + site.table    
        
        #process each row which contains a date and a post, the post which may contain many sentences
        for d in dbc.select_generator(stmt):   
            tups.append((fix_ebike_date(d[0]),d[1],d[2],d[3]))     #(date, text, questionNum, responderID)
    
    else:
        """ASSUMED FORMAT:{DATE|||COMMENT}{DATE|||COMMENT}{DATE|||COMMENT}..."""        
        #get the blob of uncleaned text and clean, insert it
        stmt = 'SELECT '
        for f in range(0, len(site.fields)):
            stmt += site.fields[f]
            stmt += ', ' if (f < len(site.fields) -1) else ' ' #add comma if not last field
            stmt += 'from ' + site.table    
        
        #process each row which contains a date and a post, the post which may contain many sentences
        for d in dbc.select_generator(stmt):
            #find all {DATE|||COMMENTS}
            for t in re.findall(r"{[^}]*}",d[0].lower()) :
                
                #first part date, second part sentence
                items = t.split("|||") 
                        
                if len(items) == 2: #this can fail if sentence somehow contained ||| which should never happen...
                    #get and fix date part
                    last_date = items[0].split("{")[1]
                    
                    if site.product.name == "Leaf":
                       last_date = string_functions.fix_leaf_date(last_date )
                    elif site.product.name == "Volt":
                       last_date = string_functions.fix_volt_date(last_date )
                    elif site.product.name == "Tesla":
                       last_date = string_functions.fix_tesla_date(last_date.split(" ")[0]) #strip off time because this level is not needed for now. 
                   
                    text = items[1].split("}")[0]  #holds all the comments made at this date by this poster
                    tups.append((last_date, text)) #(date, text)         
    
    insert_sents(site, dbc, tups)       


def insert_sents(site, dbc, tups): #last two only for surveys
    """takes a block of (date, bunch_of_comments) pairs, seperates the bunch_of_comments into sentences,
       cleans them, then inserts each as a sentence under that date"""
    thelogger.info("Cleaning data...")   
    insert_tups = []
    
    for i in tups:
        
        date = i[0]
        text = i[1]
        
        text = text.lower() #just in case
        text = re.sub("[\n\t\r\ ]+"," ", text)            #whitespace
        text = re.sub(r"http[:][/][/][^ ]* ","",text)     #kill hyperlinks 
        text = re.sub(r"[:;][ ]*[-]*[ ]*[)(]","", text)   #get rid of emotionicons
        text = re.sub("\"","", text)#replace("\"","")     #remove all quotes 
        text = re.sub(r"u[.]s[.]","united states", text)
        text = re.sub(r"part no[.]", "part number", text)
        text = re.sub(r"[ ][.](?P<int>[0-9]+)",r"0.\g<int>", text) #converts .4 into 0.4 not to confuse number with period. 
        text = re.sub(r"(?P<int1>[0-9]+)[.](?P<int2>[0-9]+)",r"\g<int1>DECIMALPOINT\g<int2>", text) #converts x.y to xDECIMALPOINTy: will be changed back after
                
        for s in re.findall(r"[^.?!]*[.!?]+", text): #find all sentences posted at that date. 
            #POSTPROCESSING. PUT BACK x.y, braces, etc.
            s = re.sub(r"(?P<int1>[0-9]+)DECIMALPOINT(?P<int2>[0-9]+)",r"\g<int1>.\g<int2>", s)
            #replace contractions, misspellings
            for word in s.split(" "):
                try:
                    s = re.sub(" {0} ".format(word), " {0} ".format(misspellingsDict[word]),s)#if this bombs the word is not in misspellings dict
                except KeyError: 
                    pass
                try:
                    s = re.sub(" {0} ".format(word), " {0} ".format(contractionsDict[word]),s)#if this bombs the word is not in contractions dict
                except KeyError:
                    pass
            if (len(s.split(" ")) > 2): #ignore sentences that are under 2 words
                #The same comment like "I love my Volt" might appear multiple times throughout a long period of time. We do not want 
                # each sentence in the reviews table to be enforced as unique then, because then there could only be one "I love my volt"
                # for all time. Instead, we will hash (prod+date+sentence) and enforce THAT to be unique. 
                
                if site.product.name == "eBike":
                    dahash = hashlib.sha256(site.product.name+str(i[2])+str(i[3])+date+s).hexdigest()            
                else:
                    dahash = hashlib.sha256(site.product.name+date+s).hexdigest()      
                
                #add to insert_tups
                insert_tups.append((dahash, site.product.name, s, date))      
    
    thelogger.info("Inserting cleaned data...")            
    dbc.bulk_insert("INSERT IGNORE INTO {senttable}".format(senttable=sent_table), 
                    insert_tups,
                    "")                  

#Fixes known date data issues and raises an error on other issues
#Sometimes the dates will say "4 weeks ago, 3 weeks ago etc.
#These will be replaced with the dates specified here
def fix_dates(site, dbc):

    updateQ = []
    
    stmt = 'select {sent}.ProdDateSentHash, {sent}.sentence, {sent}.Date '\
           'FROM {sent} '\
           'where {sent}.Product = "{prod}"'.format(prod=site.product.name,sent=sent_table)
    
    for d in dbc.select_generator(stmt):
        oldhash = str(d[0]).strip()
        sent = str(d[1]).strip()  
        olddate = str(d[2]).strip()               
        if site.product.name == "Volt":
            newdate = string_functions.fix_volt_date(olddate)           
        elif site.product.name == "Leaf":
             newdate = string_functions.fix_leaf_date(olddate)
        elif site.product.name == "Tesla":
             newdate = string_functions.fix_tesla_date(olddate)
             
        if newdate != "ERR" and newdate != olddate:
            newhash = hashlib.sha256(site.product.name+newdate+sent).hexdigest()    
            #we can use or replace because if it violates the hash then it must be the identical row including the date
            updateQ.append('UPDATE OR REPLACE {sent} set ProdDateSentHash="{nwshs}", date = "{nwdate}" where ProdDateSentHash="{oldhsh}"'.format(sent=sent_table,nwshs = newhash,nwdate = newdate,oldhsh = oldhash))
            updateQ.append('UPDATE OR REPLACE {gt} set ProdDateSentHash="{nwshs}" where ProdDateSentHash="{oldhsh}"'.format(gt=truth_table,nwshs = newhash,oldhsh = oldhash))
        
    dbc.exec_query_list(updateQ)
    


