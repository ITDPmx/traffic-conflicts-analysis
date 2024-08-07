from typing import Union

from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from email_utils import send_email_with_oauth2

app = FastAPI()
handler = Mangum(app)

class Email(BaseModel):
    destination: str
    subject: str
    link: str

@app.post("/")
def send_email(emailData: Email):
    return {"Result": send_email_with_oauth2(emailData.destination, emailData.subject, emailData.link)}


