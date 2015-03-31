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

import re

#kills whitespace
#By the way, that's a Chris Farley reference: http://www.youtube.com/watch?v=KKN6JJYIWWY
def KILL_WHITEY(thestring):
    return thestring.replace("\n","").replace("\t","").replace("\r","").strip()

def ContractionsTagsWhitey(thestring):
    """replaces tags and whitespace
    also, the splitting function expects the format: 
    ASSUMED FORMAT:{DATE|||COMMENT}{DATE|||COMMENT}{DATE|||COMMENT}...
    so we cannot have braces elsewhere. Get rid of them. 
    this { } replacement happens before the comment is aggregated into the {date|||comments} format"""
    thestring =  KILL_WHITEY(killTagsLeaveText(fixSqliteContractions(thestring)))
    return thestring.replace("{","").replace("}","")

#kill word endings leave just stems
def stem(words):
    assert isinstance(words, list), 'stem takes a list of words that have been tokenized already'
    porter = nltk.PorterStemmer()
    lancaster = nltk.LancasterStemmer()
    return [porter.stem(w) for w in words]
    #return [lancaster.stem(w) for w in words]

#returns a text without stopwords for use with statistical functions
def filterStopwords(words):
    assert isinstance(words, list), 'filterStopwords takes a list of words that have been tokenized already'
    return [w for w in words if w not in stopwords.words('english')]


#convert date from "jan" to 01 so all dates are in the same format     
def monthToInt(m):
    """Converts months in 3 letter abbrev form to XX integer form, e.g., jan -> 01"""
    
    if m == "jan":
        return "01"
    elif  m == "feb":
        return "02"
    elif  m == "mar":
        return "03"
    elif  m == "apr":
        return "04"
    elif  m == "may":
        return "05"
    elif  m == "jun":
        return "06"
    elif  m == "jul":
        return "07"
    elif  m == "aug":
        return "08"
    elif  m == "sep":
        return "09"
    elif  m == "oct":
        return "10"
    elif  m == "nov":
        return "11"
    elif  m == "dec":
        return "12"

#make all dates consistent        
def convertDateToYYYYMMDDFormat(olddate):
    #IF NOT NONE, DATE ALREADY IN CORRECT FORMAT
    if re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}$", olddate) is not None:        
        return olddate
    
    if re.match(r"[0-9]{2}-[0-9]{2}-[0-9]{4}$", olddate) is not None:        
        parts = olddate.split("-")
        m = parts[0]
        d = parts[1]
        y = parts[2]
        return "{year}-{month}-{day}".format(year=y,month=m,day=d)
    
    #THIS WAS GIVEN AN INCORrECT FORMAT IF GETS TO HERE
    return "ERR"
        
#makes ' into '' because sqlite requires this
def fixSqliteContractions(thestring):
    return thestring.replace("\'","\'\'") 

def killTagsLeaveText(thestring):
    # kills all things of the form <stuff>
    return re.sub('<[^>]*>','',thestring)



