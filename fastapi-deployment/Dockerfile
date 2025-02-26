FROM public.ecr.aws/lambda/python:3.10

# Copy function code
COPY ./app ${LAMBDA_TASK_ROOT}

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip3 install --target "${LAMBDA_TASK_ROOT}" --upgrade --no-cache-dir -r requirements.txt

# AWS Lambda requires a handler function
CMD ["main.handler"]
