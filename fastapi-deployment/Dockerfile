# Use an AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Set the working directory
WORKDIR /var/task

# Copy the application files
COPY app /var/task/

# Install dependencies
RUN pip install --no-cache-dir -r /var/task/requirements.txt

# Set the command for AWS Lambda
CMD ["main.handler"]
