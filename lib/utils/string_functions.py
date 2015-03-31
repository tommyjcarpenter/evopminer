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
This module includes some string cleaning functions
"""


import re
from lib import agoToDates

def cleanse_tags_contractions_whitespace(thestring):
    """replaces tags and whitespace
    also, the splitting function expects the format: 
    ASSUMED FORMAT:{DATE|||COMMENT}{DATE|||COMMENT}{DATE|||COMMENT}...
    so we cannot have braces elsewhere. Get rid of them. 
    this { } replacement happens before the comment is aggregated into the {date|||comments} format"""
    #escape contractions
    thestring = thestring.replace("\'","\'\'") 
    # kills all things of the form <stuff>
    thestring = re.sub('<[^>]*>','',thestring)
    #kill various whitespace 
    thestring =  thestring.replace("\n","").replace("\t","").replace("\r","").strip() 
    #kill final braces
    return thestring.replace("{","").replace("}","")

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

def fix_tesla_date(olddate):
    if olddate == "today":
        return date.today().strftime('%Y-%m-%d')
    elif olddate == "yesterday":
        return (date.today()-timedelta(days=1)).strftime('%Y-%m-%d')
    return olddate            
    
 
def fix_ebike_date(olddate):
    items = olddate.split(" ")
    newdate = "{y}-{m}-{d}".format(m=monthToInt(items[0].lower()),d=items[1],y=items[2])
    return newdate
            
#fixes known issues with mynissanleaf dates
def fix_leaf_date(olddate):
    """Fixes known possible Leaf date data errors"""
    
    #FIRST TRY TO FIND ERRORS THAT ARE CAUSED BY [STUFF]DATE
    try_date= re.findall(r"([a-z]{3} [0-9]{2}, [0-9]{4})",olddate)
    if len(try_date) == 1:
        newdate = try_date[0]
        newdate = "{y}-{m}-{d}".format(m=monthToInt(newdate.split(" ")[0]),
                                       d=newdate.split(" ")[1].split(",")[0],
                                       y=newdate.split(", ")[1])
        return newdate
    
    #see if its in MM-DD-YYYY format
    try_date= re.findall(r"([0-9]{2}-[0-9]{2}-[0-9]{4})",olddate)
    if len(try_date) == 1:
        newdate = convertDateToYYYYMMDDFormat(try_date[0])
        return newdate
      
    #ERROR or nothing detected wrong
    return olddate
               
#fixes known issues with chevy volt dates
def fix_volt_date(olddate):
    """Fixes known possible Volt date data errors"""
    
    #FIRST TRY TO FIND ERRORS THAT ARE CAUSED BY [STUFF]DATE
    try_date= re.findall(r"([0-9]{2}-[0-9]{2}-[0-9]{4})",olddate)
    if len(try_date) == 1:
        newdate = convertDateToYYYYMMDDFormat(try_date[0])
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


"""     No Longer Used        
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
"""

