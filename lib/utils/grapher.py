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

from __future__ import division
import matplotlib as mpl
import matplotlib.pyplot as plt
from math import pow, sqrt
from lib import thelogger


mpl.rcParams["lines.linewidth"] = 1
mpl.rcParams["font.size"] = 30


def getResultDict(currSite, dbc, UseOrDebug, limit=None):
    """helper function for the other graphing functions"""
        
    resDict = ()
    newResDict = dict()

    newResDict['Xs'] = []
    newResDict['Counts'] = []
    newResDict['Classpos'] = []
    newResDict['Classneg'] = []
    newResDict['Classneu'] = []
        
    if UseOrDebug == "USE":        
        resDict = dbc.getResults(currSite.ProdObj.Name, limit)
    
    else:
        resDict = dbc.computePrecisionAndRecall(currSite.ProdObj.Name)

        newResDict['Correctclasspos'] = []
        newResDict['Correctclassneg'] = []
        newResDict['Correctclassneu'] = []
        newResDict['truthpos'] = []
        newResDict['truthneg'] = []
        newResDict['truthneu'] = []
        newResDict['Pos_Ps'] = []
        newResDict['Neg_Ps'] = []
        newResDict['Pos_Rs'] = []
        newResDict['Neg_Rs'] = []
        newResDict['Overall_Ps'] = []
        newResDict['Overall_Rs'] = []
        newResDict['Com_Hs'] = []
        #newResDict['Sep_Hs'] = []
        
    for k in sorted(resDict.keys()):
        
        #LAST MINUTE GRAPHING CHANGES (INSTEAD OF CHANGING THE FEATURES EVERYWHERE ELSE...)
        #note this is a hack..
        kk = k.replace("_","")
        if kk == "RA":
            kk = "RangeAnxiety"
        elif k == "LooksAndDesign":
            kk = "Design"
        elif kk == "ClimateControl":
            kk = "HVAC"
        elif kk == "MiscFeatures":
            kk = "MiscFeats"
        newResDict['Xs'].append(kk)
        
        newResDict['Classpos'].append(100*resDict[k]["class +"]/resDict[k]["Count"])
        newResDict['Classneg'].append(100*resDict[k]["class -"]/resDict[k]["Count"])
        newResDict['Classneu'].append(100*resDict[k]["class N"]/resDict[k]["Count"])
        newResDict['Counts'].append(resDict[k]["Count"])            
        
        if UseOrDebug == "DEBUG":        

            newResDict['Pos_Ps'].append(resDict[k]["Pos Precision"])
            newResDict['Neg_Ps'].append(resDict[k]["Neg Precision"])
            newResDict['Pos_Rs'].append(resDict[k]["Pos Recall"])
            newResDict['Neg_Rs'].append(resDict[k]["Neg Recall"])
            newResDict['Overall_Ps'].append(resDict[k]["Overall Precision"])
            newResDict['Overall_Rs'].append(resDict[k]["Overall Recall"])
            newResDict['Correctclasspos'].append(100*resDict[k]["*(class +)"]/resDict[k]["Count"])
            newResDict['Correctclassneg'].append(100*resDict[k]["*(class -)"]/resDict[k]["Count"])
            newResDict['Correctclassneu'].append(100*resDict[k]["*(class N)"]/resDict[k]["Count"])   
            newResDict['truthpos'].append(100*resDict[k]["count truth +"]/resDict[k]["Count"])
            newResDict['truthneg'].append(100*resDict[k]["count truth -"]/resDict[k]["Count"])
            newResDict['truthneu'].append(100*resDict[k]["count truth N"]/resDict[k]["Count"])        
            #newResDict['Sep_Hs'].append(max([resDict[k]["Pos Precision"],resDict[k]["Neg Precision"],resDict[k]["Pos Recall"],resDict[k]["Neg Recall"]]))
            newResDict['Com_Hs'].append(max([resDict[k]["Overall Precision"],resDict[k]["Overall Recall"]]))
        
    return newResDict


#produces the bar graph as seen in our paper
def graph(currSite, dbc, UseOrDebug, limit=None):
    """selector function for graphing. Chooses which graphing functions to call based on whether system being used or debuged"""
    if UseOrDebug == "DEBUG":
        newResDict = getResultDict(currSite, dbc, "DEBUG")
        graphPandR(currSite, newResDict) 
        graphPolarityStacksDebug(currSite, newResDict)
    else:
        newResDict = getResultDict(currSite, dbc, "USE", limit)
        graphPolarityStacksUse(currSite, newResDict)
    
    
def graphPandR(currSite, newResDict):
    """graphs precision and recall"""
    LEN = len(newResDict['Xs'])
    width = 0.5       # the width of the bars
    mpl.rcParams["font.size"] = 30
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects1 = ax.bar([0*width + 3*x*width for x in range(0, LEN)], newResDict['Overall_Ps'], width, color='.3')
    rects2 = ax.bar([1*width + 3*x*width for x in range(0, LEN)], newResDict['Overall_Rs'], width, color='.7') 
    ax.set_ylabel('%')
    ax.set_title('{0} Performance Metrics'.format(currSite.ProdObj.Name))
    ax.set_xticks([width+ 3*x*width for x in range(0,LEN)])
    ax.set_yticks([x*10 for x in range(0,11)])
    ax.set_xticklabels(newResDict['Xs'],rotation=-90 )
    ax.set_xlim(0,3*width*LEN-1 + .9*width)
    ax.set_ylim(0,110)
    leg = ax.legend((rects1, rects2), ('Precision', 'Recall'), loc=8,ncol=2,  fancybox=True)
    leg.get_frame().set_alpha(0.7)
    
    def autolabel(rects, whicharr):
        for x in range (0, len(rects)):
            height = newResDict['Com_Hs'][x]
            ax.text(rects[x].get_x()+rects[x].get_width()/1., 100, "{0}".format(whicharr[x]), ha='center', va='bottom', rotation=0)
    
    autolabel(rects1,newResDict['Counts'])
     #make grid go behind bars
    ax.set_axisbelow(True) 
    ax.yaxis.grid(color='0', linestyle='solid')
    plt.tight_layout()
    plt.show()     


#produces the graph of sentiment polarities seen in the paper
def graphPolarityStacksDebug(currSite, newResDict):
    """graphs poliarity of sentiments. Three bars each column: classified, correctly classified, and ground truth"""
    LEN = len(newResDict['Xs'])
    width = 0.5       # the width of the bars
    mpl.rcParams["font.size"] = 30
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects1 = ax.bar([0*width + 4*x*width for x in range(0, LEN)], newResDict['Classpos'], width, color='.0')
    rects2 = ax.bar([0*width + 4*x*width for x in range(0, LEN)], newResDict['Classneg'], width, color='.4',bottom=newResDict['Classpos']) 
    rects3 = ax.bar([0*width + 4*x*width for x in range(0, LEN)], newResDict['Classneu'], width, color='.8',bottom=[a+b for a,b in zip(newResDict['Classpos'],newResDict['Classneg'])]) 

    rects4 = ax.bar([1*width + 4*x*width for x in range(0, LEN)], newResDict['Correctclasspos'], width, color='.0')
    rects5 = ax.bar([1*width + 4*x*width for x in range(0, LEN)], newResDict['Correctclassneg'], width, color='.4',bottom=newResDict['Correctclasspos']) 
    rects6 = ax.bar([1*width + 4*x*width for x in range(0, LEN)], newResDict['Correctclassneu'], width, color='.8',bottom=[a+b for a,b in zip(newResDict['Correctclasspos'],newResDict['Correctclassneg'])]) 
    
    rects7 = ax.bar([2*width + 4*x*width for x in range(0, LEN)], newResDict['truthpos'], width, color='.0')
    rects8 = ax.bar([2*width + 4*x*width for x in range(0, LEN)], newResDict['truthneg'], width, color='.4',bottom=newResDict['truthpos']) 
    rects9 = ax.bar([2*width + 4*x*width for x in range(0, LEN)], newResDict['truthneu'], width, color='.8',bottom=[a+b for a,b in zip(newResDict['truthpos'],newResDict['truthneg'])]) 
        
    def autolabel(rects, whicharr):
        for x in range (0, len(rects)):
            height = 100
            ax.text(rects[x].get_x()+rects[x].get_width()/1., 100, "{0}".format(whicharr[x]), ha='center', va='bottom', rotation=0)
    autolabel(rects1,newResDict['Counts'])
    
    ax.set_ylabel('%')
    ax.set_title('{0} Polarity Breakdown'.format(currSite.ProdObj.Name))
    ax.set_xticks([width*1.5+ 4*x*width for x in range(0,LEN)])
    ax.set_yticks([x*10 for x in range(0,11)])
    ax.set_xticklabels(newResDict['Xs'],rotation=-90 )
    ax.set_ylim(0,110)
    ax.set_xlim(0,4*width*LEN-1 + .9*width)
    leg = ax.legend((rects1, rects2,rects3), ('Pos', 'Neg','Neu'), loc=9,bbox_to_anchor=(0.5, 0.9),ncol=3,  fancybox=True)
    leg.get_frame().set_alpha(0.7)

    #make grid go behind bars
    ax.set_axisbelow(True) 
    ax.yaxis.grid(color='0', linestyle='solid')
    plt.tight_layout()
    plt.show() 
    
    
#produces the graph of sentiment polarities seen in the paper
def graphPolarityStacksUse(currSite, newResDict):
    
    LEN = len(newResDict['Xs'])
    
    width = 4       # the width of the bars
    
    XLocs = [1.5*x*width for x in range(0, LEN)]
    
    mpl.rcParams["font.size"] = 30
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects1 = ax.bar(XLocs, newResDict['Classpos'], width, color='.0')
    rects2 = ax.bar(XLocs, newResDict['Classneg'], width, color='.4',bottom=newResDict['Classpos']) 
    rects3 = ax.bar(XLocs, newResDict['Classneu'], width, color='.8',bottom=[a+b for a,b in zip(newResDict['Classpos'],newResDict['Classneg'])]) 
        
    def autolabel(rects, whicharr):
        for x in range (0, len(rects)):
            height = 100
            ax.text(rects[x].get_x()+rects[x].get_width()/2, 100, "{0}".format(whicharr[x]), ha='center', va='bottom', rotation=0)
    autolabel(rects1,newResDict['Counts'])
    
    ax.set_ylabel('%')
    ax.set_title('{0} Polarity Breakdown'.format(currSite.ProdObj.Name))
    ax.set_xticks([i+width/2 for i in XLocs])
    ax.set_yticks([x*10 for x in range(0,11)])
    ax.set_xticklabels(newResDict['Xs'],rotation=-90 )
    ax.set_ylim(0,110)
    ax.set_xlim(0,XLocs[-1]+width)
    leg = ax.legend((rects1, rects2,rects3), ('Pos', 'Neg','Neu'), loc=9,bbox_to_anchor=(0.5, 0.9),ncol=3,  fancybox=True)
    leg.get_frame().set_alpha(0.7)

    #make grid go behind bars
    ax.set_axisbelow(True) 
    ax.yaxis.grid(color='0', linestyle='solid')
    #plt.tight_layout()
    plt.show() 
    
    
       
#plots a frequency distribution of words and word counts
def plotFD(Xs,Ys,Xlabs,Xcols,count):
   #DO THE PLOT
   plt.figure(1) 
    
   #plt.xlabel("Term")
   plt.ylabel("Frequency")
   plt.title("Word vs. Frequency")
    
   ax = plt.subplot(111)
    
   #plot the two bars
   ax.bar(Xs, Ys, color="grey",width=1)
    
   #set axis
   ax.set_xticks([i+.5 for i in range(0,count)])
   ax.set_xticklabels(Xlabs, rotation=270)
   ax.set_yticks([i for i in range(0,max(Ys)+5,5)])
   ax.set_yticklabels([i for i in range(0,max(Ys)+5,5)])
         
   for xtick, color in zip(ax.get_xticklabels(), Xcols):
       xtick.set_color(color)
   
   plt.xlim(0,count)
   plt.ylim(1,max(Ys))

   #ax.set_yticklabels([0.05*x*100 for x in range(0,21)])
   #make grid go behind bars
   ax.set_axisbelow(True) 
   ax.yaxis.grid(color='0', linestyle='solid')    
   #2plt.tight_layout()
   plt.show() 
      