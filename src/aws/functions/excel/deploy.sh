# Runs commands to generate .zip file for AWS Lambda function
# https://youtu.be/7-CvGFJNE_o?si=evSpTfI1AuBK2YM2&t=224
# Make sure to run this script from src/aws/functions/excel directory

pip install -t dependencies -r requirements.txt
cd dependencies
zip ../aws_lambda_artifact.zip -r .
cd ..
zip aws_lambda_artifact.zip -u data/template.xlsx
zip aws_lambda_artifact.zip -u excel_utils.py
zip aws_lambda_artifact.zip -u metadata.py
zip aws_lambda_artifact.zip -u objects.py
zip aws_lambda_artifact.zip -u main.py
