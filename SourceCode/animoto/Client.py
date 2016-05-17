# import modules

import ConfigParser
import argparse
import os
import random
from Queue import Queue
from multiprocessing import Process
from time import time, sleep
import boto.dynamodb
import boto.sqs
from boto.sqs.message import RawMessage
from Localworker import Localworker


# For Creating DynamoDB table
 
def createDynamoDB():

    # http://programminggenin.blogspot.com/2012/10/getting-started-with-amazons-dynamodb.html

    print 'Creating a table with DynamoDB...'

    dynamodbConn = boto.connect_dynamodb(aws_access_key_id=config.get('amazon', 'AMAZON_ACCESS_KEY') \
                                                   ,aws_secret_access_key=config.get('amazon', 'AMAZON_SECRET_KEY'))    # Connection with Amazon DynamoDB using Boto. 

    myschema=dynamodbConn.create_schema(hash_key_name='task_id',hash_key_proto_value='S')                               # Create Schema in DynamoDB

    try:

        myTable = dynamodbConn.create_table(name='MyTable',schema=myschema,read_units=100,write_units=100)              # Create Table in DynamoDB with read and write capacity
        print '\tTable created successfully!\n'

    except:

        print '\tMyTable already exists.\n'

    return


# def worker(i):
#     while not lq.empty():
#         print "worker {} is executing task..".format(i)
#         item = lq.get()
#         do_work(item)
#         lq.task_done()
#
#
#
# def do_work(item):
#     arg = item.split()
#     arg1 = float(str(arg[1]))/1000
#     arg = arg[0] + " " + str(arg1)
#     print item
#     os.system(arg)




if __name__ == '__main__':

    # createDynamoDB()
    parser = argparse.ArgumentParser(description="Client")
    parser.add_argument("-s", "--schedule", help="QNAME", required=True)
    parser.add_argument("-w", "--workload", help="<WORKLOAD_FILE>", required=True)
    parser.add_argument("-t", "--thread", help="Number of Threads", required=False)
    

    args = parser.parse_args()

    # tasks =  open("workload.txt")
    tasks = open(args.workload)

    config = ConfigParser.ConfigParser()
    config.read('amazon.cfg')

    # http://boto.cloudhackers.com/en/latest/sqs_tut.html


    conn = boto.sqs.connect_to_region("us-east-1", aws_access_key_id=config.get('amazon', 'AMAZON_ACCESS_KEY') \		# Connection with SQS using boto
                                      , aws_secret_access_key=config.get('amazon', 'AMAZON_SECRET_KEY'))

    if args.schedule == 'Local':																						# Local Queue module calls

        q = Queue()
        result = []
        task = open(args.workload)
        tasks = []
        for item in task.readlines():
            q.put(item)
            tasks.append(item)

        nworker = int(args.thread)
        worker = []
        starttime = time()
        for i in range(nworker):
            t = Localworker(tasks[(i * len(tasks) / nworker):((i + 1) * len(tasks) / nworker)])							# Localworker class has called from here where threads are implemented.  
            t.daemon = True
            t.start()																									# Thread starts. 
            worker.append(t)

        for i in worker:
            i.join()

        for wk in worker:
            result += wk.results

        print "Total Time taken by Local Worker is {} sec".format(time() - starttime)

        if sum(result) == 0:																							# To check the response from Worker 
																														# If all response 0 then only task completed. 

            print "\n\nTask Completed Successfully... :)"
        else:

            print "\n\nOhh Sorry, Task is Not Completed.. :("

    elif args.schedule == 'QNAME:																												# Remote Queue aka SQS Module

        taskQueue = conn.create_queue(args.schedule)
        dynamodb = createDynamoDB()

        rand = random.sample(range(1, 18000), len(tasks.readlines()))													# Generating Unique numbers.. 
        #print rand
        tasks.seek(0)
        start = time()
        for i, data in enumerate(tasks.readlines()):
            m = RawMessage()
            print data
            m.set_body(data)																							# Set the message in queue as a body. 
            # q.write(m)

            m.message_attributes = {
                "Task": {
                    "data_type": "String",
                    "string_value": str(rand[i])
                }

            }
            taskQueue.write(m)																							# to write the message in queue

        print 'All tasks have been sent to SQS successfully.\n'

        tasks.seek(0)
        resQueue = conn.get_queue("resQueue")																			# Result queue to get data from Worker. 		

        #tasks.seek(0)
        i = 0
        rs = resQueue.get_messages()
        #print len(rs)
        #print len(tasks.readlines())
        #tasks.seek(0)
        while i < len(tasks.readlines()):																				# To poll until all values come from worker. 
            #print i
            if len(rs):
                i+=1
                m = rs[0]
                print "Task Completed: " + m.get_body()
                resQueue.delete_message(m)

            rs = resQueue.get_messages()
            tasks.seek(0)

        endtime = time()

        print "Total Time taken by Remote Worker is {} sec".format(endtime-start)										# For finding the time.

        print 'All results have been retreived from SQS.\n'
		
	else:
		