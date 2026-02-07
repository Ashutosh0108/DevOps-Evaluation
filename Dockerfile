# Step 1: Use official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.9

# Step 2: Copy requirements and install
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Step 3: Copy your Lambda function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Step 4: Set the CMD to your handler (file_name.function_name)
CMD [ "lambda_function.lambda_handler" ]