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
from lib.utils.string_functions import cleanse_tags_contractions_whitespace
from lib.utils.mysql import CrawlerDBC


#cleans the volt items before being entered into the database. 
class VoltCleaner(object):
   def process_item(self, item, spider):
       if 'VoltCleaner' not in getattr(spider, 'pipelines'):
          return item
       
       #fix contractions in title
       item['title'] = cleanse_tags_contractions_whitespace(item['title'])
       
       #infer numcomments
       item['numcomments'] = len(item['comments'])
       
       #make the comments into pairs {date|||comment}  pipes used because later i need to parse the date out and need a unique seperator. 
       comments = ""
       for c in range(0,len(item['comments'])): 
           #need to kill the quoted text, but cant do this in xpath becasue the post will contain divs seperating
           #the quoted text and the actual reply of the user. So, we extract the part of the message containing the actual reply here.  
           #see myNIssanLeaf spider for more details
           #note this wont work if there is a quote before and after a posters post, but hopefully the number of these si small
           thec = item['comments'][c].split("</div>")[-1]
           comments += "{" + item['commentdates'][c] + "|||" + (cleanse_tags_contractions_whitespace(thec) + "}\n")
       item['newCommentFormat'] = comments
       return item
 
#put the items in de db      
class VoltDBC(CrawlerDBC):    
    def process_item(self, item, spider):
       if 'VoltDBC' not in getattr(spider, 'pipelines'):
          return item
       q = 'insert into VoltReviews (BaseSite,Content,Title,Url,NumComments,Comments) values (\'{0}\', \'{1}\', \'{2}\', \'{3}\',\'{4}\', \'{5}\')'.format(item['site'],item['contenttype'],item['title'],item['url'],item['numcomments'],item['newCommentFormat'])       
       self.insertItem(item, q)
       return item

