import logging
# import watchtower
# import boto3

# Configure the root logger
logging.basicConfig(level=logging.INFO)

# # Set up CloudWatch handler
# cloudwatch_handler = watchtower.CloudWatchLogHandler(
#     boto3_session=boto3.Session(region_name='your-region'),  # Replace with your AWS region
#     log_group="your-log-group-name"  # Replace with your CloudWatch log group name
# )

# # Formatter for CloudWatch logs
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# cloudwatch_handler.setFormatter(formatter)

# # Get the root logger and add the CloudWatch handler
# root_logger = logging.getLogger()
# root_logger.addHandler(cloudwatch_handler)