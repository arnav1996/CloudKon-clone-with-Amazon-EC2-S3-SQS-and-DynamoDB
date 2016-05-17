from time import sleep, time
import boto.sqs
import ConfigParser
from boto.sqs.message import RawMessage
import boto.dynamodb
import os
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Client: The Task Execution Framework.")
    parser.add_argument("-s", "--schedule", help="QNAME", required=True)
    parser.add_argument("-v", "--verbose", help="Verbose", default=True)
	parser.add_argument("-t", "--thread", help="Number of Threads", required=False)

    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read('amazon.cfg')
    # workloads = open(args.)

    conn = boto.sqs.connect_to_region("us-east-1", aws_access_key_id=config.get('amazon', 'AMAZON_ACCESS_KEY'), \					# Connection with SQS using boto
                                      aws_secret_access_key=config.get('amazon', 'AMAZON_SECRET_KEY'))

    dynamodbConn = boto.connect_dynamodb(aws_access_key_id=config.get('amazon', 'AMAZON_ACCESS_KEY') \
                                                   ,aws_secret_access_key=config.get('amazon', 'AMAZON_SECRET_KEY'))				# Connection with Amazon DynamoDB using Boto. 

    q = conn.get_queue(args.schedule)																								# To get queue from sqs
    rq = conn.create_queue("resQueue")

    myTable = dynamodbConn.get_table('MyTable')																						# To get the table from DynamoDB

    while True:																														# To poll every time to get queue from Client. 																										
        rs = q.get_messages(message_attributes=['Task'])
        starttime = time()
        #print len(rs)

        if len(rs) == 0:
            endtime = time()
            if (endtime - starttime) > 100:																			# Wait for 100 sec max for Client to send something then come out of program.
                break
            else:
                print "Waiting for Client...."

        else:
            m = rs[0]
            #print m
            arg = m.get_body().split()

            taskId = m.message_attributes['Task']['string_value']													# To fetch task id from message from queue
            #print taskId
            taskContent = m.get_body()																				# To get the message body

            if myTable.has_item(hash_key=taskId):																	# First Check the task id and if available then discard from queue. 
                q.delete_message(m)

            else:
                print 'Storing task {} into DynamoDB...' .format(taskId)
                item_data={'taskContent':taskContent}
                item = myTable.new_item(hash_key=taskId, attrs=item_data)											# To add new item in table. 
                item.put()
                # Execute task
                print 'Executing task {} ...' .format(taskId)
                arg1 = float(str(arg[1])) / 1000
                arg = arg[0] + " " + str(arg1)
                print arg
                os.system(arg)

                dm = RawMessage()
                dm.set_body(m.message_attributes['Task']['string_value'])											# to set the value in message body. 
                dm.message_attributes = {
                    "Result": {
                        "data_type": "Number",
                        "string_value": 0
                    }
                }
                rq.write(dm)
                print 'Sending result ({}) to resultQueue...\n\n' .format(arg)
                q.delete_message(m)

