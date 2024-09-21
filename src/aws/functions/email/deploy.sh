# Runs commands to generate .zip file for AWS Lambda function
# https://youtu.be/7-CvGFJNE_o?si=evSpTfI1AuBK2YM2&t=224
# Make sure to run this script from src/aws/functions/email directory

pip install -t dependencies -r requirements.txt --platform manylinux2014_x86_64 --only-binary=:all:
cd dependencies
zip ../aws_lambda_artifact.zip -r .
cd ..
zip aws_lambda_artifact.zip -u main.py
zip aws_lambda_artifact.zip -u email_utils.py

# Add credentials for automatic reload
zip aws_lambda_artifact.zip -u credentials.json
zip aws_lambda_artifact.zip -u token.json