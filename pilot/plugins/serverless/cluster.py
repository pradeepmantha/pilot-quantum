"""
Lambda Manager
"""

import os
import logging
import time
import boto3 
import json
import stat
import inspect
import zipfile

class Manager():

    def __init__(self, jobid, working_directory):
        self.jobid = jobid
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')            
        self.role_arn=""
        self.configuration={}
        
        
    # Lambda - submit pilot job
    def submit_job(self,
                   resource_url="lambda://localhost",
                   number_of_nodes=None, # ignored
                   number_cores=1, # will be mapped to concurrency
                   cores_per_node=None, # ignored
                   spmd_variation=None, # ignored
                   queue=None, # ignored
                   walltime=None, # ignored
                   project=None, # ignored
                   config_name=None,
                   extend_job_id=None,
                   pilotcompute_description=None
    ):
        try:
            if "lambda_function" not in pilotcompute_description and "lambda_input_data" not in pilotcompute_description:
                raise Exception("Please specify lambda_function and lambda_input_data in you Pilot-Job Description!") 
           
            self.role_arn = self.create_lambda_iam_role(self.jobid)
            print("created role: " + self.role_arn)
            zipped_code=self.prepare_function(pilotcompute_description["lambda_function"], self.jobid)
            time.sleep(10)
            response = self.lambda_client.create_function(
                                    FunctionName=self.jobid,
                                    Runtime='python3.7',
                                    Role=self.role_arn,
                                    Handler=self.jobid+'.' + pilotcompute_description["lambda_function"].__name__,
                                    Code={
                                        'ZipFile': zipped_code
                                    },
                                    Description='Managed Lambda Function'
                                    )
            
            response=self.lambda_client.get_function(FunctionName=self.jobid)
            self.configuration=response[ 'Configuration']
            
            print("Create mapping from %s to %s"%(pilotcompute_description["lambda_input_data"], self.jobid))
            response = self.lambda_client.create_event_source_mapping(
                EventSourceArn=pilotcompute_description["lambda_input_data"],
                FunctionName=self.jobid,
                Enabled=True,
                BatchSize=1,
                StartingPosition='LATEST'
                )
            
            response=self.lambda_client.get_function(FunctionName=self.jobid)
            self.configuration=response[ 'Configuration']
            print("Created lambda: %s"%self.jobid)
        except Exception as ex:
            print("An error occurred: %s" % (str(ex)))
            

    def wait(self):
        return 
    
            
    def submit_compute_unit(self, function_ref):
        # update lambda code
        response=self.lambda_client.get_function(FunctionName=self.jobid)
        self.configuration=response[ 'Configuration']
        zipped_code=self.prepare_function(function_ref, self.jobid)
        response = self.lambda_client.update_function_code(
                                        FunctionName=self.jobid,
                                        ZipFile=zipped_code,
                                        RevisionId=self.configuration['RevisionId']
                                        )
        
    def get_jobid(self):
        return self.stream_arn
    
    
    def get_context(self, configuration):
        return None
    
    
    def cancel(self):
        self.lambda_client.delete_function(FunctionName=self.jobid)
        iam_client = boto3.client('iam')
        iam_client.detach_role_policy(RoleName=iam_role_name, PolicyArn='arn:aws:iam::aws:policy/AmazonKinesisFullAccess')
        iam_client.detach_role_policy(RoleName=iam_role_name, PolicyArn='arn:aws:iam::aws:policy/CloudWatchLogsFullAccess')
        iam_client.delete_role(RoleName=self.jobid)
            
    
    def get_config_data(self):
        return self.configuration
    
    
    def print_config_data(self):
        print("Lambda: %s"%self.stream_arn)

        
    def prepare_function(self, function_ref, file_basename):
        print("Prepare code for function: %s"%file_basename)
        lines = inspect.getsource(function_ref)
        with open(file_basename + ".py", "w") as f:
            f.write(lines)
        os.chmod(file_basename + ".py", stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        with zipfile.ZipFile(file_basename + '.zip', 'w') as myzip:
            myzip.write(file_basename + ".py")
        env_variables = dict() # Environment Variables
        with open(file_basename + '.zip', 'rb') as f:
            zipped_code = f.read()
        os.remove(file_basename + '.zip')
        os.remove(file_basename + '.py')
        return zipped_code
    
    
    def create_lambda_iam_role(self, rolename):
        iam_client = boto3.client('iam')
        role_policy_document = {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "",
              "Effect": "Allow",
              "Principal": {
                "Service": "lambda.amazonaws.com"
              },
              "Action": "sts:AssumeRole"
            }
          ]
        }
        iam_client.create_role(
          RoleName=rolename,
          AssumeRolePolicyDocument=json.dumps(role_policy_document),
        )
        role = iam_client.get_role(RoleName=rolename)
        response = iam_client.attach_role_policy(
            RoleName=rolename,
            PolicyArn='arn:aws:iam::aws:policy/AmazonKinesisFullAccess'
        )
        response = iam_client.attach_role_policy(
            RoleName=rolename,
            PolicyArn='arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'
        )
        return role['Role']['Arn']