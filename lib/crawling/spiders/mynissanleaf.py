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

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from lib.crawling.items import myNissanLeafItem
from unidecode import unidecode #used to convert strange unicode into ascii

class LeafSpider(CrawlSpider):
   name = 'myNissanLeafSpider'
   allowed_domains = ['www.mynissanleaf.com']
   start_urls=['http://www.mynissanleaf.com/viewforum.php?f=35']
   pipelines = ['myNissanLeafClean','myNissanLeafDB']

   rules = ( 
   # these are threads => http://www.mynissanleaf.com/viewtopic.php?f=34&t=9266   
                         #http://www.mynissanleaf.com/viewtopic.php?f=38&start=10&t=6671
                         #http://www.mynissanleaf.com/viewtopic.php?f=27&sid=de17525f21de4a13c246ea7da337a8e2&start=160&t=10257
     
   Rule(SgmlLinkExtractor(allow=('/viewtopic\.php[.]*'),deny=()),callback='parse_item',follow=False),
                          
   #follow forum links: http://www.mynissanleaf.com/viewforum.php?f=30
   Rule(SgmlLinkExtractor(allow=('/viewforum\.php[.]*')), follow=True),
   )

   #parsing function 
   def parse_item(self, response):
       hxs = HtmlXPathSelector(response)
       item = myNissanLeafItem()

       item['site'] = "http://www.mynissanleaf.com/viewforum.php?f=35"
      
       #these are all discussions
       item['contenttype'] = "Forum"

       #<title>My Nissan Leaf Forum &bull; View topic - The official &quot;I got my Leaf&quot; thread</title>
       item['title'] = unidecode(hxs.select('//title/text()').extract()[0]).split("View topic - ")[1]
      
       item['url'] = unidecode(response.url) 
            
       #<td class="gensmall" width="100%">//<div style="float: right;"><b>Posted:</b> Thu Dec 23, 2010 10:57 am&nbsp;</div></td>
       item['commentdates'] = [unidecode(i).strip() for i in hxs.select('//td[@class="gensmall"]//div[@style="float: right;"]/text()').extract()]        
      
       #comments are easy in this one
       # <div class="postbody"> 
       item['comments'] = [unidecode(i).strip() for i in hxs.select('//div[@class="postbody"]').extract()]
       return item









