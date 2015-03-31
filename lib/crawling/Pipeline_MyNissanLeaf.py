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

# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from unidecode import unidecode #used to convert strange unicode into ascii
from lib.utils.stringFunctions import ContractionsTagsWhitey
from lib.utils.databaseConnector import cralwerDBObject

#cleans the items before being entered into the database. 
class myNissanLeafClean(object):
   def process_item(self, item, spider):
       if 'myNissanLeafClean' not in getattr(spider, 'pipelines'):
          return item
       
       #fix contractions in title
       item['title'] = ContractionsTagsWhitey(item['title'])
       
       #infer numcomments
       item['numcomments'] = len(item['comments'])
       
       #make the comments into pairs {date|||comment} 3 pipes used because later i need to parse the date out and need a unique seperator. 
       comments = ""
       for c in range(0,len(item['comments'])):           
           #need to kill the quoted text, but cant do this in xpath.
           #in xpath if we select /div/text, then if there is a blank line in someones post:
           #<div class="postbody"> 
           #blag
           #<br>
           #blah
           #this gets parsed as two seperate comments. but we only want this to count as one post. 
           
           #instead well split the string (using pythoin) based on the div tag and take the shit before the last tag
           #KILL ALL OF THIS:
           #<div class="postbody"><div class="quotetitle">padamson1 wrote:</div><div class="quotecontent"
           #>I've been using the coil and twist method used by sailors (as shown here <a href="http://www.youtu
           ##be.com/watch?v=k2ChlCns4AU" onclick="window.open(this.href);return false;" class="postlink">http://www.you
           #tube.com/watch?v=k2ChlCns4AU</a>  but without the final tight wrap &amp; knot).  
           #This requires that a the far end is free to spin around because the twist turns the rope. </div>
           #START KEEPING FROM HERE
           #<br />I had modified this method so that when the wire gets twisted, I twist it the opposite way and 
           #put the loop on the other side of the coil.  This keeps the cable from getting twisted overall.  
           #I use this on the 20 feet of cable on the 120V brick EVSE.  But--it does nothing to help you get it unrolled.  
           #I have to unroll it the old fashioned way...
           #<br /><br />THEN, I watched the video!  No more of the old method!  I am going to learn this over/under method.  
           #As padamson1 said, I learned something new today.
           #</div>
           
           #note this wont work if there is a quote before and after a posters post, but hopefully the number of these si small
           thec = item['comments'][c].split("</div>")[-2]
           comments += "{" + item['commentdates'][c] + "|||" + (ContractionsTagsWhitey(thec) + "}\n")
       item['newCommentFormat'] = comments
       return item
 

#put the items in de db      
class myNissanLeafDB(cralwerDBObject):  
    def process_item(self, item, spider):
       if 'myNissanLeafDB' not in getattr(spider, 'pipelines'):
          return item
       q = 'insert into LeafReviews (BaseSite,Content,Title,Url,NumComments,Comments) values (\'{0}\', \'{1}\', \'{2}\', \'{3}\',\'{4}\', \'{5}\')'.format(item['site'],item['contenttype'],item['title'],item['url'],item['numcomments'],item['newCommentFormat'])
       self.insertItem(item, q)
       return item

