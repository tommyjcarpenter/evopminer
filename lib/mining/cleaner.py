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
from nltk.collocations import *
import re
from nltk.corpus import stopwords
import hashlib
from datetime import date, timedelta
from lib import misspellingsDict, contractionsDict, sentTableName, truthTableName, agoToDates, thelogger
from lib.utils import stringFunctions

def process_into_cleaned_sentences(currSite, dbc): 
    """takes the raw mined reviews, cleans them into sentences, and then puts them back into DB"""
    thelogger.info("Selecting/Cleaning Data..\n")
    tups = [] #expects (date, text) pairs, or in the case of ebikes, (date, text, questionNum, responderID) pairs
        
    if currSite.ProdObj.Name == "eBike":
        """ASSUMED FORMAT: date, comments, QuestionNumber, ResponseNumber"""
        #get the blob of uncleaned text and clean, insert it
        stmt = 'SELECT Date, '
        for f in range(0, len(currSite.FieldsToPull)):
            stmt += currSite.FieldsToPull[f]
            stmt += ', ' if (f < len(currSite.FieldsToPull) -1) else ' ' #add comma if not last field
            stmt += ', Question, responseNumber from ' + currSite.Table    
        
        #process each row which contains a date and a post, the post which may contain many sentences
        for d in dbc.SQLSelectGenerator(stmt):   
            tups.append((fixebikeDate(d[0]),d[1],d[2],d[3]))     #(date, text, questionNum, responderID)
    
    else:
        """ASSUMED FORMAT:{DATE|||COMMENT}{DATE|||COMMENT}{DATE|||COMMENT}..."""        
        #get the blob of uncleaned text and clean, insert it
        stmt = 'SELECT '
        for f in range(0, len(currSite.FieldsToPull)):
            stmt += currSite.FieldsToPull[f]
            stmt += ', ' if (f < len(currSite.FieldsToPull) -1) else ' ' #add comma if not last field
            stmt += 'from ' + currSite.Table    
        
        #process each row which contains a date and a post, the post which may contain many sentences
        for d in dbc.select_generator(stmt):
            #find all {DATE|||COMMENTS}
            for t in re.findall(r"{[^}]*}",d[0].lower()) :
                
                #first part date, second part sentence
                items = t.split("|||") 
                        
                if len(items) == 2: #this can fail if sentence somehow contained ||| which should never happen...
                    #get and fix date part
                    last_date = items[0].split("{")[1]
                    
                    if currSite.ProdObj.Name == "Leaf":
                       last_date = fixLeafDate(last_date )
                    elif currSite.ProdObj.Name == "Volt":
                       last_date = fixVoltDate(last_date )
                    elif currSite.ProdObj.Name == "Tesla":
                       last_date = fixTeslaDate(last_date.split(" ")[0]) #strip off time because this level is not needed for now. 
                   
                    text = items[1].split("}")[0]  #holds all the comments made at this date by this poster
                    tups.append((last_date, text)) #(date, text)         
    
    performSentenceInserts(currSite, dbc, tups)       


def performSentenceInserts(currSite, dbc, tups): #last two only for surveys
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
                
                if currSite.ProdObj.Name == "eBike":
                    dahash = hashlib.sha256(currSite.ProdObj.Name+str(i[2])+str(i[3])+date+s).hexdigest()            
                else:
                    dahash = hashlib.sha256(currSite.ProdObj.Name+date+s).hexdigest()      
                
                #add to insert_tups
                insert_tups.append((dahash, currSite.ProdObj.Name, s, date))      
    
    thelogger.info("Inserting cleaned data...")            
    dbc.bulk_insert("INSERT IGNORE INTO {senttable}".format(senttable=sentTableName), 
                    insert_tups,
                    "")                  

#Fixes known date data issues and raises an error on other issues
#Sometimes the dates will say "4 weeks ago, 3 weeks ago etc.
#These will be replaced with the dates specified here
def fixDates(currSite, dbc):

    updateQ = []
    
    stmt = 'select {sent}.ProdDateSentHash, {sent}.sentence, {sent}.Date '\
           'FROM {sent} '\
           'where {sent}.Product = "{prod}"'.format(prod=currSite.ProdObj.Name,sent=sentTableName)
    
    for d in dbc.SQLSelectGenerator(stmt):
        oldhash = str(d[0]).strip()
        sent = str(d[1]).strip()  
        olddate = str(d[2]).strip()               
        if currSite.ProdObj.Name == "Volt":
            newdate = fixVoltDate(olddate)           
        elif currSite.ProdObj.Name == "Leaf":
             newdate = fixLeafDate(olddate)
        elif currSite.ProdObj.Name == "Tesla":
             newdate = fixTeslaDate(olddate)
             
        if newdate != "ERR" and newdate != olddate:
            newhash = hashlib.sha256(currSite.ProdObj.Name+newdate+sent).hexdigest()    
            #we can use or replace because if it violates the hash then it must be the identical row including the date
            updateQ.append('UPDATE OR REPLACE {sent} set ProdDateSentHash="{nwshs}", date = "{nwdate}" where ProdDateSentHash="{oldhsh}"'.format(sent=sentTableName,nwshs = newhash,nwdate = newdate,oldhsh = oldhash))
            updateQ.append('UPDATE OR REPLACE {gt} set ProdDateSentHash="{nwshs}" where ProdDateSentHash="{oldhsh}"'.format(gt=truthTableName,nwshs = newhash,oldhsh = oldhash))
        
    dbc.exec_query_list(updateQ)
    


def fixTeslaDate(olddate):
    if olddate == "today":
        return date.today().strftime('%Y-%m-%d')
    elif olddate == "yesterday":
        return (date.today()-timedelta(days=1)).strftime('%Y-%m-%d')
    return olddate            
    
 
def fixebikeDate(olddate):
    items = olddate.split(" ")
    newdate = "{y}-{m}-{d}".format(m=stringFunctions.stringFunctions.monthToInt(items[0].lower()),d=items[1],y=items[2])
    return newdate
            
#fixes known issues with mynissanleaf dates
def fixLeafDate(olddate):
    """Fixes known possible Leaf date data errors"""
    
    #FIRST TRY TO FIND ERRORS THAT ARE CAUSED BY [STUFF]DATE
    tryToFindDate = re.findall(r"([a-z]{3} [0-9]{2}, [0-9]{4})",olddate)
    if len(tryToFindDate) == 1:
        newdate = tryToFindDate[0]
        newdate = "{y}-{m}-{d}".format(m=stringFunctions.monthToInt(newdate.split(" ")[0]),
                                       d=newdate.split(" ")[1].split(",")[0],
                                       y=newdate.split(", ")[1])
        return newdate
    
    #see if its in MM-DD-YYYY format
    tryToFindDate = re.findall(r"([0-9]{2}-[0-9]{2}-[0-9]{4})",olddate)
    if len(tryToFindDate) == 1:
        newdate = stringFunctions.stringFunctions.convertDateToYYYYMMDDFormat(tryToFindDate[0])
        return newdate
      
    #ERROR or nothing detected wrong
    return olddate
            
            
#fixes known issues with chevy volt dates
def fixVoltDate(olddate):
    """Fixes known possible Volt date data errors"""
    
    #FIRST TRY TO FIND ERRORS THAT ARE CAUSED BY [STUFF]DATE
    tryToFindDate = re.findall(r"([0-9]{2}-[0-9]{2}-[0-9]{4})",olddate)
    if len(tryToFindDate) == 1:
        newdate = stringFunctions.convertDateToYYYYMMDDFormat(tryToFindDate[0])
        return newdate
        
    #NEXT TRY TO FIND "X WEEKS AGO" ERRORS
    tryToFindWEEKSAgo = re.findall(r"[0-9] week[s]? ago$",olddate)
    if len(tryToFindWEEKSAgo) == 1:
        agosIndex = int(tryToFindWEEKSAgo[0].split(" ")[0])
        newdate = agoToDates[agosIndex]
        return newdate
            
    #NEXT TRY TO FIND "X DAYS/HOURS/MINUTES AGO" ERRORS WHICH ARE ALL IN LAST WEEK SO USE TODAYS DATE
    tryToFindDAYSAgo = re.findall(r"[0-9] day|hour|minute[s]? ago$",olddate)
    if len(tryToFindDAYSAgo) == 1:
        newdate = agoToDates[0]
        return newdate
    
    #ERROR or nothing detected wrong
    return olddate
