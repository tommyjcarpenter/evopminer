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
import pymysql as msql
import random
import re
import hashlib
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lib import truth_table, sent_table, results_table, sample_table
from lib.utils.config_reader import conf_reader
from lib import thelogger
from pymysql.converters import escape_string

        
class DBC(object):
    """Context manager mysql connection"""
    def __enter__(self):
        return self

    def __init__(self, database=None):
        if not database:
            database = conf_reader["mysql"]["database"] #default database
        user = conf_reader["mysql"]["user"]
        passwd = conf_reader["mysql"]["password"]
        host = conf_reader["mysql"]["host"]
        prt = int(conf_reader["mysql"]["port"])
        try:            
            self.myDB = msql.connect(host=host, port=prt, user=user, passwd=passwd.replace("\"",""), db=database)   
            self.conn = self.myDB.cursor() 
        except Exception, msg:
            thelogger.error("MYSQL ERROR: {0}".format(msg))
            exit(1)

    def __exit__(self, *args):
        """closes mysql connection"""
        self.conn.close() 
     
    def escape(self, stmt):
        """Escapes"""
        return escape_string(stmt).strip() if stmt else None

    def select_generator(self, stmt):
        """execute a select query and return results as a generator"""
        try:   
            data = []    
            self.conn.execute(stmt)
            data = self.conn.fetchall() #change if RAM not plentiful..currently defeats the purpose of a generator
            for row in data:
                yield row
        except mysql.Error as msg:
            thelogger.error("MYSQL QUERY ERROR!: {0}".format(msg))

    def exec_query_list(self, Q):
        """execute a bunch of sql queries, commits at end. An error on query i does not halt query i+1"""
        for q in Q:
            try: 
                self.conn.execute(q)
            except MySQLdb.Error as msg:
                thelogger.error("{1} MYSQL QUERY ERROR!: {0}".format(msg, q))
        self.myDB.commit()
            
    def bulk_insert(self, insert_clause, rows, update_clause):
        """rows: is a list of tuples with C elements where C is the number of columns
           insert_clause: the insert query with table name and columns. For example: INSERT INTO table (C1, C2)
           update_clause: a MySQL "ON DUPLICATE KEY" clause. For example: ON DUPLICATE KEY UPDATE c1 = VALUES(c2),
        """
        insert_queue = []  
        insert_vals = "" 
        count_this_run = 0 
        total_count = 0
        for i in range(0, len(rows)): 
            total_count += 1
            insert_vals += "(" + ",".join(["'{0}'".format(k) for k in [self.escape(j) if type(j) == str else j for j in rows[i]]]) + "),"                                                                                                                               
            if total_count % 10000 == 0 or total_count == len(rows): 
                insert_queue.append(insert_clause + " VALUES " + insert_vals[0:-1].replace("'None'","NULL") + " " + update_clause + ";") #REPLACE Python Nones with proper mysql NULLs
                insert_vals = "" #reset values
        self.exec_query_list(insert_queue) 
               
    #generates a list of all hashes in ground truth. Used to do a join against the ground truth table.    
    def get_truth_hashes_product(self,pr):
        stmt = 'SELECT {truth}.ProdDateSentHash,{truth}.feature,{truth}.label ' \
               'from {truth} INNER JOIN {sent} ' \
               'ON {truth}.ProdDateSentHash = {sent}.ProdDateSentHash ' \
               'WHERE {sent}.Product = "{prod}"'.format(truth=truth_table,sent=sent_table,prod=pr)
        
        gtdict = dict()
        
        for row in self.select_generator(stmt):
            hash = str(row[0]).strip()
            feat = str(row[1]).strip()
            label = str(row[2]).strip()
            gtdict[hash] = dict()
            gtdict[hash][feat] = label
            
        return gtdict
    
              
    #compute precision and recall
    def precision_recall(self,product):
        #first fetch the results        
        stmt = 'SELECT {res}.Feature, {res}.Label as class, {truth}.Label as truth \n' \
               'from {res} INNER JOIN {truth} \n '\
               'ON {res}.ProdDateSentHash = {truth}.ProdDateSentHash and {res}.Feature = {truth}.Feature \n' \
               'INNER JOIN {sent} \n' \
               'ON {res}.ProdDateSentHash = {sent}.ProdDateSentHash \n' \
               'WHERE {sent}.Product = "{prod}" \n'.format(truth=truth_table,sent=sent_table,prod=product,res=results_table)
               
               #must join featute becase the same sentence can be classified for multiple features. Also, there may be some rows in results where the PDShash is classified for a feature that it is not classified in GT and you may have rows in GT classifying some PDSh for results but the program did not classify that same PDSh for results. 
               #mysql> SELECT Results.Feature, Results.Label as class, GroundTruth.Label as truth  from Results INNER JOIN GroundTruth   ON Results.ProdDateSentHash = GroundTruth.ProdDateSentHash and Results.Feature = GroundTruth.Feature  INNER JOIN CleanedSentences  ON Results.ProdDateSentHash = CleanedSentences.ProdDateSentHash  WHERE CleanedSentences.Product = "Volt";
               #1605 rows in set (0.07 sec)

               #mysql> SELECT Results.Feature, Results.Label as class, GroundTruth.Label as truth  from Results INNER JOIN GroundTruth   ON Results.ProdDateSentHash = GroundTruth.ProdDateSentHash                                            INNER JOIN CleanedSentences  ON Results.ProdDateSentHash = CleanedSentences.ProdDateSentHash  WHERE CleanedSentences.Product = "Volt";
               #2113 rows in set (0.07 sec)"""

        results = dict()    
        for d in self.select_generator(stmt):
            f = str(d[0])
            clas = str(d[1])
            truth = str(d[2])
            
            try:
                results[f]["Count"] += 1 #membership testing in O(1) time
            except KeyError:
                results[f] = dict()
                results[f]["class +"] = 0
                results[f]["class -"] = 0
                results[f]["class N"] = 0
                results[f]["*(class +)"] = 0
                results[f]["*(class -)"] = 0
                results[f]["*(class N)"] = 0
                results[f]["count truth +"] = 0
                results[f]["count truth -"] = 0
                results[f]["count truth N"] = 0
                results[f]["Count"] = 1
                       
            if clas == "POS": 
                results[f]["class +"] += 1
                if truth == "POS":
                    results[f]["*(class +)"] += 1
            elif clas == "NEG":
                results[f]["class -"] += 1
                if truth == "NEG":
                    results[f]["*(class -)"] += 1
            elif clas == "NEU":
                results[f]["class N"] += 1
                if truth == "NEU":
                    results[f]["*(class N)"] += 1
                    
            else:
                thelogger.error("ERROR, UNKNOWN CLASSIFICATION: {0}".format(clas))
            
            if truth == "POS": 
                results[f]["count truth +"] += 1
            elif truth == "NEG": 
                results[f]["count truth -"] += 1
            elif truth == "NEU": 
                results[f]["count truth N"] += 1
                
        features = results.keys()
        
        for k in features:
            
            results[k]["Pos Precision"] = 100
            results[k]["Neg Precision"] = 100
            results[k]["Pos Recall"] = 100
            results[k]["Neg Recall"] = 100
            results[k]["Overall Precision"] = 100
            results[k]["Overall Recall"] = 100

            if results[k]["class +"] != 0:
                results[k]["Pos Precision"] = (results[k]["*(class +)"] / results[k]["class +"])*100
            if results[k]["class -"] != 0:
                results[k]["Neg Precision"] = (results[k]["*(class -)"] / results[k]["class -"])*100
            if (results[k]["class +"] + results[k]["class -"]) != 0: 
                results[k]["Overall Precision"] = ((results[k]["*(class +)"]+results[k]["*(class -)"]) / (results[k]["class +"]+results[k]["class -"]))*100
            if results[k]["count truth +"] != 0:
                results[k]["Pos Recall"] = (results[k]["*(class +)"] / results[k]["count truth +"])*100    
            if results[k]["count truth -"] != 0:
                results[k]["Neg Recall"] = (results[k]["*(class -)"] / results[k]["count truth -"])*100
            if (results[k]["count truth +"]+results[k]["count truth -"]) != 0:
                results[k]["Overall Recall"] = ((results[k]["*(class +)"]+results[k]["*(class -)"]) / (results[k]["count truth +"]+results[k]["count truth -"]))*100
        
        return results

    #get classification results
    def get_results(self,product, limit):
        #first fetch the results  
                     
        stmt = 'SELECT {res}.Feature, {res}.Label as class \n' \
               'from {res} INNER JOIN {sent} \n' \
               'ON {res}.ProdDateSentHash = {sent}.ProdDateSentHash \n' \
               'WHERE {sent}.Product = "{prod}" limit {lim}\n'.format(lim=limit,sent=sent_table,prod=product,res=results_table)
               
               #must join featute becase the same sentence can be classified for multiple features. Also, there may be some rows in results where the PDShash is classified for a feature that it is not classified in GT and you may have rows in GT classifying some PDSh for results but the program did not classify that same PDSh for results. 
               #mysql> SELECT Results.Feature, Results.Label as class, GroundTruth.Label as truth  from Results INNER JOIN GroundTruth   ON Results.ProdDateSentHash = GroundTruth.ProdDateSentHash and Results.Feature = GroundTruth.Feature  INNER JOIN CleanedSentences  ON Results.ProdDateSentHash = CleanedSentences.ProdDateSentHash  WHERE CleanedSentences.Product = "Volt";
               #1605 rows in set (0.07 sec)

        results = dict()    
        for d in self.select_generator(stmt):
            f = str(d[0])
            clas = str(d[1])
            
            try:
                results[f]["Count"] += 1 #membership testing in O(1) time
            except KeyError:
                results[f] = dict()
                results[f]["class +"] = 0
                results[f]["class N"] = 0
                results[f]["class -"] = 0
                results[f]["Count"] = 1
                       
            if clas == "POS": 
                results[f]["class +"] += 1
            elif clas == "NEG":
                results[f]["class -"] += 1
            elif clas == "NEU":
                results[f]["class N"] += 1
            else:
                thelogger.error("ERROR, UNKNOWN CLASSIFICATION: {0}".format(clas))
            
        return results
    
    
      
                    
    #sample a small section of results for reading for groundtruth        
    def sample_for_classification(self, class_percent, neu_percent, product):
        #first fetch the results table
        stmt = 'SELECT {res}.sentenceid, {res}.Feature, {sent}.sentence, {res}.Label' \
                           'FROM {res}, {sent} ' \
                           'WHERE {res}.sentenceid = {sent}.sentenceid and {res}.Product = "{prod}"'.format(res=results_table,sent=sent_table,prod=product)
     
        #first, add all the insert statements into one of two lists for each feature. The first list for each feature 
        # contains pos and neg inserts, and the second contains only neutrals. Both are then sampled from at different rates
        inserts = dict()
        for d in self.select_generator(stmt):
            sid = str(d[0])
            f = str(d[1])
            s = str(d[2])
            l = str(d[3]) #only used to see whether sampled or not
            
            #create an insert statement and add it to queue
            stmt = 'INSERT INTO {samp} VALUES("{prod}","{si}","{feat}","{sent}"'.format(samp=sample_table,prod=product,si=sid,feat=f,sent=s)

            try: #add neutrals to second list, add pos/neg to first
                inserts[f][l == "NEU"].append(stmt) #bombs in O(1) if not already in inserts, otherwise do nothing
            except KeyError:
                inserts[f] = [[],[stmt]] if l == "NEU" else [[stmt],[]]
            
        #build the actual insert list by sampling the classified, neutrals seperately and adding the sampled
        inserts = [] #final insert queue
        num_class_inserted = 0
        num_neu_inserted = 0
        
        #insert statements into the final insert queue
        for k in inserts.keys():
            num_class = len(inserts[k][0]) #number of those classified
            num_class_to_ins = int(class_percent*num_class) #number of classified to insert based on sampling percentage
            num_class_inserted += num_class_to_ins
            
            #sampling without replacement gives indices of those to insert
            indices = random.sample(range(num_class), num_class_to_ins) 
            for i in indices:
                inserts.append(inserts[k][0][i]) #add these to final inserts
                
            num_neu = len(inserts[k][1]) #number of those neutral
            num_neu_to_ins= int(neu_percent*num_neu) #number of neutral to inser based on sampling percentage
            num_neu_inserted += num_neu_to_ins
            
            #sampling without replacement gives indices of those to insert
            indices = random.sample(range(num_neu), num_neu_to_ins) 
            for i in indices:
                inserts.append(inserts[k][1][i]) #add these to final inserts
    
        #now insert everything
        self.exec_query_list(inserts)
        
    #deletes all results in results table before entering new results    
    def delete_product_results(self,pr):
        """deletes results table for a product in order to insert new results"""
        
        stmt = 'DELETE FROM {res} where ProdDateSentHash in '\
               '(select ProdDateSentHash from {sent} where Product="{prod}")'.format(res=results_table,sent=sent_table,prod=pr)
        self.exec_query_list([stmt])

    
    #generates sentences from the cleaned sentences table for processing. This is a database helper
    #function for process_sentences
    def gen_cleaned_sents(self, pr, UseOrDebug):
        if UseOrDebug == "DEBUG":
            stmt = "SELECT {sent}.ProdDateSentHash, {sent}.sentence FROM {sent} "\
                   "INNER JOIN {truth} ON {truth}.ProdDateSentHash = {sent}.ProdDateSentHash "\
                   "WHERE {sent}.Product = '{prod}'".format(sent=sent_table, prod=pr, truth=truth_table)   
        else:
            stmt = "SELECT ProdDateSentHash, sentence FROM {sent} WHERE  {sent}.Product='{prod}';".format(sent=sent_table, prod=pr)
    
        for d in self.select_generator(stmt):
            id = str(d[0]).strip()
            sent = str(d[1]).strip()
            yield (id, sent)                           

#base class which all spider pipelines for inserting the mined items into the DB will inherit from
class CrawlerDBC(DBC):    
    #exec an insert statement. The statement q will be passed by the inhertied class. 
    def insertItem(self, item, q):
       #sometimes 0 length items make it through
       if item['numcomments'] > 0:
           try:
              self.conn.execute(q)
              self.myDB.commit()
           except msql.Error, msg:
                thelogger.error("MYSQL ERROR: {0}".format(msg))  
       
       