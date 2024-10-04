# Set mails with Mail API (Google Cloud)


## Steps
1. Create Google Cloud project or use an existing onee. (see tutorial for detailed instructions)
2. Download OAuth 2.0 Client credentials from Google Cloud.
3. Add the mail to use as the sender into the test users of the Google Cloud project (if the project has a testing status) 
4. Run send_email.py script once locally. This will prompt the browser and ask to login using the account you want to use to send emails.
5. After the first time, the script fetches refresh tokens on its own when needed, without additional user interaction.
6. The refresh token [expires](https://developers.google.com/identity/protocols/oauth2#expiration) after one week if the project is on "Testing" status. You can move it to production to avoid this.

- [tutorial](https://mailtrap.io/blog/python-send-email-gmail/)


## Launch API

### Run locally
- Create an env and install requirements.txt
```bash
# PWD: [project_root]/src/aws/functions/email

python3 -m venv venv # Create env
source venv/bin/activate # Activate env
pip install -r requirements
```
- Run the app itself
```bash
uvicorn main:app --reload  
```


### Deploy
- Check [tutorial](https://www.youtube.com/watch?v=7-CvGFJNE_o&t=2s)