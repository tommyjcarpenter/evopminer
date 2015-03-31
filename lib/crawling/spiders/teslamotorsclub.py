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
from lib.crawling.items import teslaMotorsClubItem
from unidecode import unidecode #used to convert strange unicode into ascii

class TeslaSpider(CrawlSpider):
   name = 'teslaMotorsClubSpider'
   allowed_domains = ['www.teslamotorsclub.com']
   
   #****main forum has 5 subforums. First one in list below is the main forum *****  
   start_urls=['http://www.teslamotorsclub.com/forumdisplay.php/73-Model-S',
               'http://www.teslamotorsclub.com/forumdisplay.php/112-Model-S-Ordering-Production-Delivery',
               'http://www.teslamotorsclub.com/forumdisplay.php/110-Model-S-Driving-Dynamics',
               'http://www.teslamotorsclub.com/forumdisplay.php/109-Model-S-Battery-Charging',
               'http://www.teslamotorsclub.com/forumdisplay.php/113-Model-S-User-Interface',
               'http://www.teslamotorsclub.com/forumdisplay.php/111-Model-S-Interior-Exterior']

   pipelines = ['TeslaCleaner','TeslaDBC']

   rules = ( 
   #the format of all forum pages which link to threads it the same as the above with "/pageX" appended
   Rule(SgmlLinkExtractor(allow=('/forumdisplay\.php/73-Model-S/page[0-9]+')), follow=True),
   Rule(SgmlLinkExtractor(allow=('/forumdisplay\.php/112-Model-S-Ordering-Production-Delivery/page[0-9]+')), follow=True),
   Rule(SgmlLinkExtractor(allow=('/forumdisplay\.php/110-Model-S-Driving-Dynamics/page[0-9]+')), follow=True),
   Rule(SgmlLinkExtractor(allow=('/forumdisplay\.php/109-Model-S-Battery-Charging/page[0-9]+')), follow=True),
   Rule(SgmlLinkExtractor(allow=('/forumdisplay\.php/113-Model-S-User-Interface/page[0-9]+')), follow=True),
   Rule(SgmlLinkExtractor(allow=('/forumdisplay\.php/111-Model-S-Interior-Exterior/page[0-9]+')), follow=True),

   # these are threads => http://www.teslamotorsclub.com/showthread.php/19584-Glove-box-latch-failure
   #                      http://www.teslamotorsclub.com/showthread.php/19584-Glove-box-latch-failure/page2
   Rule(SgmlLinkExtractor(allow=('/showthread\.php/[.]*'),deny=()),callback='parse_item',follow=False),
   )

   #parsing function 
   def parse_item(self, response):
       hxs = HtmlXPathSelector(response)
       item = teslaMotorsClubItem()

       #base site. This column probably not that useful because there is another field for URL
       item['site'] = "http://www.teslamotorsclub.com/forumdisplay.php/73-Model-S"
       
       #this field is also not useful but ill leave this as is to be consistent with leaf and volt
       item['contenttype'] = "Forum"
       
       #<title> Model S Technical / Mechanical Issues</title>
       item['title'] = unidecode(hxs.select('//title/text()').extract()[0]).strip()#.split("- Page")[0].strip() 
       #<- think having the page in title is good. not used nywhere anyway other than visually looking at it
       
       #url
       item['url'] = unidecode(response.url).split("?")[0] 

       #comments easy here. Even though there is lots of quoted text, all comments are at the end of:
       #<blockquote class="postcontent restore ">....</blockquote>
       #blocks, so using /text() works like a charm. 
       item['comments'] = [unidecode(i).strip() for i in hxs.select('//blockquote[@class="postcontent restore "]').extract()]
       
       #<span class="date">2012-07-27,&nbsp;<span class="time">04:21 PM</span></span>
       #YOU LIKE THAT??-->
       item['commentdates']  = map(lambda x,y: x+y, 
                                   [unidecode(i.split(",")[0]).strip() + " " for i in hxs.select('//span[@class="postdate old"]//span[@class="date"]/text()').extract()],
                                   [unidecode(j).strip() for j in hxs.select('//span[@class="postdate old"]//span[@class="time"]/text()').extract()])    
       return item









