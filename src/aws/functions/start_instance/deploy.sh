# Runs commands to generate .zip file for AWS Lambda function
# https://youtu.be/7-CvGFJNE_o?si=evSpTfI1AuBK2YM2&t=224
# Make sure to run this script from src/aws/functions/email directory

pip install -t dependencies -r requirements.txt
cd dependencies
zip ../aws_lambda_artifact.zip -r .
cd ..
zip aws_lambda_artifact.zip -u main.py
zip aws_lambda_artifact.zip -u clients.py
zip aws_lambda_artifact.zip -u utils.py
zip aws_lambda_artifact.zip -u constants.py
