from os import popen as cli
from time import sleep
from re import search


stack_1 = 'pystack'
file_1 = 'cf_template_bucket4py.json'
stack_2 = 'lambdastack'
file_2 = 'cf_template_lambda4ec2.json'


def spawn(stackname, file, options):
    line = 'aws cloudformation create-stack --template-body file://' + file + ' --stack-name ' + stackname + ' --region eu-central-1 --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM ' + options
    cli(line)


def checker(stackname):
    line = 'aws cloudformation describe-stacks --stack-name ' + stackname
    describe = cli(line)
    status = search('\"StackStatus\":.*(?=,)',describe.read())
    try:
        return status.group(0)
    except Exception as e:
        print(e)
        return stackname


def creator (stackname, file, loops, options=''):
    spawn(stackname, file, options)
    sleep(10)
    n = 0
    while True:
        if 'CREATE_COMPLETE' in checker(stackname):
            break
        elif n == loops:
            print('---------U ARE MISERABLE-------')
            break
        #print(n)
        n += 1
        sleep(10)
    print('---------SUCCESS CREATING STACK ' + stackname +'------------')


def main():
    creator(stack_1, file_1, 10)
    bucket_check = cli('aws cloudformation describe-stacks --stack-name ' + stack_1)
    bucket = search('bucket-python-(\w)*',bucket_check.read())
    cp_line = 'aws s3 cp lambda.zip s3://' + bucket.group(0) + '/lambda.zip'
    #print(cp_line)
    cli(cp_line)
    option = '--parameters ParameterKey=pybucket,ParameterValue=' +  bucket.group(0)
    creator(stack_2, file_2, 60, option)
    lambda_check = cli('aws cloudformation describe-stacks --stack-name ' + stack_2)
    http = search('https.*(?=")',lambda_check.read())
    print('\nlambda http triger: ' + http.group(0))


if __name__ == '__main__':
    main()
