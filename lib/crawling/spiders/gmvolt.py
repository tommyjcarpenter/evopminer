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
from lib.crawling.items import voltItem
from unidecode import unidecode #used to convert strange unicode into ascii

class VoltSpider(CrawlSpider):
   name = 'VoltSpider'
   allowed_domains = ['gm-volt.com']
   
   #this page is strange. there are no links to the next forum page for each page, only in groups of 10.
   #e.g., from page 1 there is a link to 11,21,... but to go right to 8 you have to type it in. 
   #so well build the list here
   start_urls=['http://gm-volt.com/forum/forumdisplay.php?16-Volt-Ownership-Forum']
   for p in range(2,3000):
       string = 'http://gm-volt.com/forum/forumdisplay.php?16-Volt-Ownership-Forum/page'
       string += '{0}'.format(p)
       string += '&order=desc'
       start_urls.append(string)
   
   pipelines = ['VoltCleaner','VoltDBC']
   
   rules = (       
   #******Since we manually build the list of URLs to follow above, we only have a rule for links which point to threads. 
   #hence unlike the leaf, here, we will NOT have a rule of links to follow.********** 
   
   # these are threads => http://gm-volt.com/forum/showthread.php?6939-40-Miles-Club   
   Rule(SgmlLinkExtractor(allow=('forum/showthread\.php\?[.]*'),deny=()),callback='parse_item',follow=False),
   )

   #parsing function 
   def parse_item(self, response):
       hxs = HtmlXPathSelector(response)
       item = voltItem()

       item['site'] = "http://gm-volt.com/forum/forumdisplay.php?16-Volt-Ownership-Forum"
      
       #these are all discussions
       item['contenttype'] = "Forum"

       item['title'] = unidecode(hxs.select('//title/text()').extract()[0])
      
       item['url'] = unidecode(response.url) 
            
       #<span class="date">
       item['commentdates'] = [unidecode(i).strip() for i in hxs.select('//span[@class="date"]/text()').extract()]        
      
       #comments may contain quoted text, but well deal with that in the pipeline
       # <blockquote class="postcontent restore">
       item['comments'] = [unidecode(i).strip() for i in hxs.select('//blockquote[@class="postcontent restore"]').extract()]
       return item









