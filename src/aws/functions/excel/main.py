from excel_utils import get_template, set_header, add_events
from objects import HeaderData, Event
from metadata import header_metadata

from mangum import Mangum
from fastapi import FastAPI
import boto3

from io import BytesIO
import os

app = FastAPI()
handler = Mangum(app)

bucket_name = os.environ['BUCKET_NAME']

# Note: extend the timeout of this function to ~8 seconds

@app.post("/create")
def create_excel(header_data: HeaderData, events: list[Event]):
    wb = get_template()
    set_header(wb, header_data, header_metadata)
    add_events(wb, events)
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    s3_client = boto3.client('s3')
    s3_client.upload_fileobj(stream, bucket_name, "excel/" + header_data.id + '.xlsx')

    return {
        'statusCode': 200,
        'body': 'Workbook uploaded successfully!'
    }


