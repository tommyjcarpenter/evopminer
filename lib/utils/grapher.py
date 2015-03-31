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


def get_results_dict(site, dbc, UseOrDebug, limit=None):
    """helper function for the other graphing functions"""
        
    new_res_dict = dict()

    new_res_dict['Xs'] = []
    new_res_dict['Counts'] = []
    new_res_dict['Classpos'] = []
    new_res_dict['Classneg'] = []
    new_res_dict['Classneu'] = []
        
    if UseOrDebug == "USE":        
        old_res_dict = dbc.get_results(site.product.name, limit)
    
    else:
        old_res_dict = dbc.precision_recall(site.product.name)

        new_res_dict['Correctclasspos'] = []
        new_res_dict['Correctclassneg'] = []
        new_res_dict['Correctclassneu'] = []
        new_res_dict['truthpos'] = []
        new_res_dict['truthneg'] = []
        new_res_dict['truthneu'] = []
        new_res_dict['Pos_Ps'] = []
        new_res_dict['Neg_Ps'] = []
        new_res_dict['Pos_Rs'] = []
        new_res_dict['Neg_Rs'] = []
        new_res_dict['Overall_Ps'] = []
        new_res_dict['Overall_Rs'] = []
        new_res_dict['Com_Hs'] = []
        #new_res_dict['Sep_Hs'] = []
        
    for k in sorted(old_res_dict.keys()):
        
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
        new_res_dict['Xs'].append(kk)
        
        new_res_dict['Classpos'].append(100*old_res_dict[k]["class +"]/old_res_dict[k]["Count"])
        new_res_dict['Classneg'].append(100*old_res_dict[k]["class -"]/old_res_dict[k]["Count"])
        new_res_dict['Classneu'].append(100*old_res_dict[k]["class N"]/old_res_dict[k]["Count"])
        new_res_dict['Counts'].append(old_res_dict[k]["Count"])            
        
        if UseOrDebug == "DEBUG":        

            new_res_dict['Pos_Ps'].append(old_res_dict[k]["Pos Precision"])
            new_res_dict['Neg_Ps'].append(old_res_dict[k]["Neg Precision"])
            new_res_dict['Pos_Rs'].append(old_res_dict[k]["Pos Recall"])
            new_res_dict['Neg_Rs'].append(old_res_dict[k]["Neg Recall"])
            new_res_dict['Overall_Ps'].append(old_res_dict[k]["Overall Precision"])
            new_res_dict['Overall_Rs'].append(old_res_dict[k]["Overall Recall"])
            new_res_dict['Correctclasspos'].append(100*old_res_dict[k]["*(class +)"]/old_res_dict[k]["Count"])
            new_res_dict['Correctclassneg'].append(100*old_res_dict[k]["*(class -)"]/old_res_dict[k]["Count"])
            new_res_dict['Correctclassneu'].append(100*old_res_dict[k]["*(class N)"]/old_res_dict[k]["Count"])   
            new_res_dict['truthpos'].append(100*old_res_dict[k]["count truth +"]/old_res_dict[k]["Count"])
            new_res_dict['truthneg'].append(100*old_res_dict[k]["count truth -"]/old_res_dict[k]["Count"])
            new_res_dict['truthneu'].append(100*old_res_dict[k]["count truth N"]/old_res_dict[k]["Count"])        
            #new_res_dict['Sep_Hs'].append(max([old_res_dict[k]["Pos Precision"],old_res_dict[k]["Neg Precision"],old_res_dict[k]["Pos Recall"],old_res_dict[k]["Neg Recall"]]))
            new_res_dict['Com_Hs'].append(max([old_res_dict[k]["Overall Precision"],old_res_dict[k]["Overall Recall"]]))
        
    return new_res_dict


#produces the bar graph as seen in our paper
def graph(site, dbc, UseOrDebug, limit=None):
    """selector function for graphing. Chooses which graphing functions to call based on whether system being used or debuged"""
    if UseOrDebug == "DEBUG":
        new_res_dict = get_results_dict(site, dbc, "DEBUG")
        graph_precision_recall(site, new_res_dict) 
        graph_polarity_debug(site, new_res_dict)
    else:
        new_res_dict = get_results_dict(site, dbc, "USE", limit)
        graph_polarity_use(site, new_res_dict)
    
    
def graph_precision_recall(site, new_res_dict):
    """graphs precision and recall"""
    LEN = len(new_res_dict['Xs'])
    width = 0.5       # the width of the bars
    mpl.rcParams["font.size"] = 30
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects1 = ax.bar([0*width + 3*x*width for x in range(0, LEN)], new_res_dict['Overall_Ps'], width, color='.3')
    rects2 = ax.bar([1*width + 3*x*width for x in range(0, LEN)], new_res_dict['Overall_Rs'], width, color='.7') 
    ax.set_ylabel('%')
    ax.set_title('{0} Performance Metrics'.format(site.product.name))
    ax.set_xticks([width+ 3*x*width for x in range(0,LEN)])
    ax.set_yticks([x*10 for x in range(0,11)])
    ax.set_xticklabels(new_res_dict['Xs'],rotation=-90 )
    ax.set_xlim(0,3*width*LEN-1 + .9*width)
    ax.set_ylim(0,110)
    leg = ax.legend((rects1, rects2), ('Precision', 'Recall'), loc=8,ncol=2,  fancybox=True)
    leg.get_frame().set_alpha(0.7)
    
    def autolabel(rects, whicharr):
        for x in range (0, len(rects)):
            height = new_res_dict['Com_Hs'][x]
            ax.text(rects[x].get_x()+rects[x].get_width()/1., 100, "{0}".format(whicharr[x]), ha='center', va='bottom', rotation=0)
    
    autolabel(rects1,new_res_dict['Counts'])
     #make grid go behind bars
    ax.set_axisbelow(True) 
    ax.yaxis.grid(color='0', linestyle='solid')
    plt.tight_layout()
    plt.show()     


#produces the graph of sentiment polarities seen in the paper
def graph_polarity_debug(site, new_res_dict):
    """graphs poliarity of sentiments. Three bars each column: classified, correctly classified, and ground truth"""
    LEN = len(new_res_dict['Xs'])
    width = 0.5       # the width of the bars
    mpl.rcParams["font.size"] = 30
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects1 = ax.bar([0*width + 4*x*width for x in range(0, LEN)], new_res_dict['Classpos'], width, color='.0')
    rects2 = ax.bar([0*width + 4*x*width for x in range(0, LEN)], new_res_dict['Classneg'], width, color='.4',bottom=new_res_dict['Classpos']) 
    rects3 = ax.bar([0*width + 4*x*width for x in range(0, LEN)], new_res_dict['Classneu'], width, color='.8',bottom=[a+b for a,b in zip(new_res_dict['Classpos'],new_res_dict['Classneg'])]) 

    rects4 = ax.bar([1*width + 4*x*width for x in range(0, LEN)], new_res_dict['Correctclasspos'], width, color='.0')
    rects5 = ax.bar([1*width + 4*x*width for x in range(0, LEN)], new_res_dict['Correctclassneg'], width, color='.4',bottom=new_res_dict['Correctclasspos']) 
    rects6 = ax.bar([1*width + 4*x*width for x in range(0, LEN)], new_res_dict['Correctclassneu'], width, color='.8',bottom=[a+b for a,b in zip(new_res_dict['Correctclasspos'],new_res_dict['Correctclassneg'])]) 
    
    rects7 = ax.bar([2*width + 4*x*width for x in range(0, LEN)], new_res_dict['truthpos'], width, color='.0')
    rects8 = ax.bar([2*width + 4*x*width for x in range(0, LEN)], new_res_dict['truthneg'], width, color='.4',bottom=new_res_dict['truthpos']) 
    rects9 = ax.bar([2*width + 4*x*width for x in range(0, LEN)], new_res_dict['truthneu'], width, color='.8',bottom=[a+b for a,b in zip(new_res_dict['truthpos'],new_res_dict['truthneg'])]) 
        
    def autolabel(rects, whicharr):
        for x in range (0, len(rects)):
            height = 100
            ax.text(rects[x].get_x()+rects[x].get_width()/1., 100, "{0}".format(whicharr[x]), ha='center', va='bottom', rotation=0)
    autolabel(rects1,new_res_dict['Counts'])
    
    ax.set_ylabel('%')
    ax.set_title('{0} Polarity Breakdown'.format(site.product.name))
    ax.set_xticks([width*1.5+ 4*x*width for x in range(0,LEN)])
    ax.set_yticks([x*10 for x in range(0,11)])
    ax.set_xticklabels(new_res_dict['Xs'],rotation=-90 )
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
def graph_polarity_use(site, new_res_dict):
    
    LEN = len(new_res_dict['Xs'])
    
    width = 4       # the width of the bars
    
    XLocs = [1.5*x*width for x in range(0, LEN)]
    
    mpl.rcParams["font.size"] = 30
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects1 = ax.bar(XLocs, new_res_dict['Classpos'], width, color='.0')
    rects2 = ax.bar(XLocs, new_res_dict['Classneg'], width, color='.4',bottom=new_res_dict['Classpos']) 
    rects3 = ax.bar(XLocs, new_res_dict['Classneu'], width, color='.8',bottom=[a+b for a,b in zip(new_res_dict['Classpos'],new_res_dict['Classneg'])]) 
        
    def autolabel(rects, whicharr):
        for x in range (0, len(rects)):
            height = 100
            ax.text(rects[x].get_x()+rects[x].get_width()/2, 100, "{0}".format(whicharr[x]), ha='center', va='bottom', rotation=0)
    autolabel(rects1,new_res_dict['Counts'])
    
    ax.set_ylabel('%')
    ax.set_title('{0} Polarity Breakdown'.format(site.product.name))
    ax.set_xticks([i+width/2 for i in XLocs])
    ax.set_yticks([x*10 for x in range(0,11)])
    ax.set_xticklabels(new_res_dict['Xs'],rotation=-90 )
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
def graph_freq_dist(Xs,Ys,Xlabs,Xcols,count):
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
      