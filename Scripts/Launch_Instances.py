import ConfigParser
import boto.ec2


# Create a new EC2 T2.small Instance

def create_EC2(count):
    config = ConfigParser.ConfigParser()
    config.read('amazon.cfg')

    print 'Creating instances...'

    conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=config.get('amazon', 'AMAZON_ACCESS_KEY') \
                                      , aws_secret_access_key=config.get('amazon', 'AMAZON_SECRET_KEY'))
    for i in range(count):
        conn.run_instances(
            'ami-fce3c696',
            key_name='Hw3',
            instance_type='t2.small',
            security_groups=['launch-wizard-1']
        )

    print '\t{} Instances are launched successfully.\n'.format(count)

    return

if __name__ == '__main__':

    config = ConfigParser.ConfigParser()
    config.read('amazon.cfg')
    Create_EC2(8)
