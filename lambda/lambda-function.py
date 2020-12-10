
import json
import boto3
import time


def send_email(email_data):
    client = boto3.client("ses")
    response = client.send_email(
    Destination={
        'BccAddresses': [
        ],
        'CcAddresses': [
        ],
        'ToAddresses': [
            'stefanstojanovicbusiness73@gmail.com',
        ],
    },
    Message={
        'Body': {
            'Text': {
                'Charset': 'UTF-8',
                'Data': f'Injected message ==> {email_data["message"]}' if email_data["message"] else "Error while injecting the message",
            },
        },
        'Subject': {
            'Charset': 'UTF-8',
            'Data': email_data["subject"],
        },
    },
    Source='stefanstojanovicbusiness73@gmail.com')


def process_dynamodb_response(response):
    #We can see the response from dynamoDB in test events
    message = None
    for record in response["Records"]:
        if "INSERT" in record["eventName"]:
            message = record["dynamodb"]["NewImage"]["message"]["S"]
    return message

def get_active_instance(describe):
    for reservation in describe["Reservations"]:
        for instance in reservation["Instances"]:
            if "running" in instance["State"]["Name"]:
                return instance["InstanceId"]
                


def lambda_handler(event, context):
    message = process_dynamodb_response(event)
    if message: 
        client = boto3.client('ec2')
        ssm = boto3.client('ssm')
        
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
        describe_instances = client.describe_instances()
        
        #getting the first running instance
        instance_id = get_active_instance(describe_instances)

        #we send argument => message in python execute command so it gets injected to an html file 
        #via python script on EC2 instance
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.send_command
        response = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': ['cd /home/ssm-user/bluegrid-html', 
                                        f"python3 inject.py '{message}'"]}  
                )
    
    
        
        command_id = response['Command']['CommandId']
        #waiting for command to finish on ssm, there is also waiter boto3 methods for this
        #so we can get the command invocation; we can use the output of the command to determine
        #if the injection was succesfull
        time.sleep(4)
        
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_command_invocation        
        output = ssm.get_command_invocation(
              CommandId=command_id,
              InstanceId=instance_id)
    
        #send the outcome of the script to the email using ses, 
        #it felt as it was the next logical step of automating this task
        returned_output = json.loads(output["StandardOutputContent"])
        send_email(returned_output)
        

