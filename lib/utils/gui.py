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

from Tkinter import *


#The constructor (the __init__ method) is called with a parent widget (the master), to which it adds a number of child widgets.
class RunGUI:
    
    def __init__(self):

        self.root = Tk()
        self.root.wm_title("Runtime Parameter Selection")

        self.frame = Frame(self.root)
        self.frame.pack()
        
        #for why exportselection=0 see: http://stackoverflow.com/questions/756662/using-multiple-listboxes-in-python-tkinter
        prodgroup = LabelFrame(self.frame, text="Product?", padx=5, pady=5)
        prodgroup .pack(padx=10, pady=10,side=LEFT)
        self.prod_list = Listbox(prodgroup,selectmode=SINGLE,exportselection=0)
        self.prod_list.insert(END,"Leaf")
        self.prod_list.insert(END,"Volt")
        self.prod_list.insert(END,"Tesla")
        self.prod_list.insert(END,"eBike")
        self.prod_list.select_set(3) #defaults to ebike for now
        self.prod_list.pack()
        self.prodbutton = Button(prodgroup, text="Explain this", fg="red", command=lambda: self.create_window(prodtext))
        self.prodbutton.pack()
        
        rdgroup = LabelFrame(self.frame, text="Run or Debug?", padx=5, pady=5)
        rdgroup .pack(padx=10, pady=10,side=LEFT)
        self.rundebug = Listbox(rdgroup,selectmode=SINGLE,exportselection=0)
        self.rundebug.insert(END,"DEBUG")
        self.rundebug.insert(END,"RUN")
        self.rundebug.select_set(1) #defaults to r for now
        self.rundebug.pack()
        self.runbutton = Button(rdgroup, text="Explain this", fg="red", command=lambda: self.create_window(rdtext))
        self.runbutton.pack()
        
        
        hotgroup = LabelFrame(self.frame, text="Hotstart?", padx=5, pady=5)
        hotgroup.pack(padx=10, pady=10,side=LEFT)
        self.hotstart = Listbox(hotgroup,selectmode=SINGLE,exportselection=0)
        self.hotstart.insert(END,"FALSE")
        self.hotstart.insert(END,"TRUE")
        self.hotstart.select_set(0) #defaults to false for now
        self.hotstart.pack()
        self.hotbutton = Button(hotgroup, text="Explain this", fg="red", command=lambda: self.create_window(hottext))
        self.hotbutton.pack()
        
        stagesgroup = LabelFrame(self.frame, text="Stages To Run?", padx=5, pady=5)
        stagesgroup.pack(padx=10, pady=10,side=LEFT)      
        self.stages = Listbox(stagesgroup,selectmode=MULTIPLE,exportselection=0)
        self.stages.insert(END,"Stage0: DataIntegrity")
        self.stages.insert(END,"Stage1: Crawl")
        self.stages.insert(END,"Stage2: Clean")
        self.stages.insert(END,"Stage3: ProcessAndClassify")
        self.stages.insert(END,"Stage4: Graphage")
        self.stages.insert(END,"Stage: sentiment_time_series")
        self.stages.insert(END,"Stage: FrequencyDistributions")
        self.stages.pack()
        self.stagesbutton = Button(stagesgroup, text="Explain this", fg="red", command=lambda: self.create_window(stagestext))
        self.stagesbutton.pack()
        
        
        #The constructor starts by creating a Frame widget. A frame is a simple container, and is in this case only used to hold the other two widgets.
        self.runbutton = Button(self.frame, text="RUN!", command=self.getParamsAndClose)
        self.runbutton.pack(side=LEFT)

    def getParamsAndClose(self):
        self.poll()
        self.root.quit()
        
    def destroy(self):
        self.root.destroy()
             
    def poll(self):
        self.UseOrDebug = self.rundebug.get(self.rundebug.curselection()[0])
        self.HOTSTART = self.hotstart.curselection()[0]
        self.stages = [self.stages.get(i) for i in self.stages.curselection()]
        self.product = self.prod_list.get(self.prod_list.curselection()[0])
    
    def create_window(self,mestext):
        top = Toplevel()
        #top.geometry("%dx%d%+d%+d" % (600, 600, 50, 50))
        top.title("Help")
        msg = Label(top, text=mestext,justify=LEFT,wraplength=500)
        msg.pack()
        button = Button(top, text="OK", command=top.destroy)
        button.pack()


#DOCUMENTATION
 
prodtext = "Defines what product you want to run this system for\n"
 
 
 
       
rdtext = """When the system is in USE mode, all sentiments are classified and graphed, but the user does not know what percentage of these are correct.\n
When the system is in DEBUG mode, only sentiments that are in the ground truth table are classified and graphed, and precision and recall is computed and graphed. This gives the user a sense of how well the system is working in terms of accuracy and classification power.\n
DEBUG mode is helpful because it classifies far fewer sentences, which is really fast thus useful when you want to make changes to the system to fix classification errors.
"""




hottext = """Hotstart was created so that features after the processing of sentences can be debugged.\n
Once you run the system once, the results will be pickled (storage of Python object). This pickled object can then be loaded if you wish to test features and do not want to recompute results, which takes a few hours sometimes.\n
Hotstart cannot be turned on until the system has been run once.
"""




stagestext = """Define what stages to do. You may select multiple stages.\n 
Stage0: DataIntegrity---This should only be run if an error was caused in the database somehow. Normally, sentences are cleaned as they are parsed and split in stage 2, so the data is already run through the same set of filders as they are here\n 
Stage1: Crawl---Crawls the forums. This is done rarely; only when the review database is out of date. NOTE: The primary key on the raw review tables is URL. For this reason, its better to purge those raw review tables completely before re building the table using this crawling method because the same comments could be moved to different urls over time\n
Stage2: Clean---Converts raw mined reviews into split and cleaned sentences. Precursor to sentence processing.\n
Stage3: ProcessAndClassify---HOTSTART or Classify all sents in `cleaned sentences` for this product\n
Stage4: Graphage---Graphs results\n
Stage: sentiment_time_series---For a colleague of mine. You can probably ignore.\n
Stage: FrequencyDistributions---for graphing the sentiments of unigrams and bigrams in the corpus 
"""
