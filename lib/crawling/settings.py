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

# Scrapy settings for GreenCarScraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'crawler'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['lib.crawling.spiders']
NEWSPIDER_MODULE = 'lib.crawling.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

#CREATING PIPELINES
"""
http://doc.scrapy.org/en/latest/topics/item-pipeline.html
Writing your own item pipeline
Writing your own item pipeline is easy. Each item pipeline component is a single Python class that must implement the following method:
process_item(item, spider)
"""

#http://doc.scrapy.org/en/latest/topics/settings.html#std:setting-ITEM_PIPELINES
#Lists are supported in ITEM_PIPELINES for backwards compatibility, but they are deprecated.
ITEM_PIPELINES = {
				  'lib.crawling.leaf_pipeline.myNissanLeafClean':1,
				  'lib.crawling.leaf_pipeline.myNissanLeafDB':2,
				  'lib.crawling.volt_pipeline.VoltCleaner':3,
				  'lib.crawling.volt_pipeline.VoltDBC':4,
				  'lib.crawling.tesla_pipeline.TeslaCleaner':5, 
				  'lib.crawling.tesla_pipeline.TeslaDBC':6 
                 }




