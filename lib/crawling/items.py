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

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class baseItem(Item):
   site = Field()
   contenttype = Field()
   title = Field()
   url = Field()
   numcomments = Field()
   commentdates = Field()
   comments = Field()
   newCommentFormat = Field()
   
class myNissanLeafItem(baseItem):
    pass
    
class voltItem(baseItem):
    pass

class teslaMotorsClubItem(baseItem):
    pass

#class GCRItem(baseItem):
#   author = Field()
#   postDate = Field()
#   views = Field()
#   body = Field()
#
#class HybridCarsItem(baseItem):
#    body = Field()
#
#   
#class pluginCarsItem(baseItem):
#   postDate = Field()
#   author = Field()
#   body = Field()
#
