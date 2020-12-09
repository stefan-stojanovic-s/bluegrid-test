# BlueGrid Test

Using a combination of AWS services we are importing request payload from an API to DynamoDB after which Dynamo triggers a lambda function that, using AWS Session Manager, connects to an EC2 instance and appends a message to index.html file .

## Branches

For the sake of better structuring, there are 2 branches. 
EC2 branch is used on EC2 instance and it only includes index.html file and a helper inject.py script.
Master branch includes all data

## inject.py

Script uses system arguments to get a hold of the message entered in DynamoDB, which is passed from the lambda function.
Afterwards, it parses the existing index.html file and injects a new message in a form of a li tag inside an unordered list .

## lambda/lambda-function.py

This lambda function is triggered from DynamoDB after changes happen to the data inside the table.<br/>
Once the message from the request has been INSERT-ed, lambda grabs the inserted message and passes it <br/>
on to the script on the EC2 instance using SSM . 