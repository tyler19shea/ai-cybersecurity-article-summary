import smtplib
from email.message import EmailMessage
import markdown
import os
from datetime import datetime

def sendemail(message_file: str):
    with open(message_file) as f:
        message=f.read()
    msg=EmailMessage()
    msg['Subject']=f'Cyber Breakdown: {datetime.now().strftime("%m-%d-%Y")}'
    msg['From']='CyberMan' + f'<{os.getenv("FROM_EMAIL")}>'
    msg['TO']=f'{os.getenv('TO_EMAIL')}'
    msg.set_content(markdown.markdown(message), subtype='html')

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(f'{os.getenv("FROM_EMAIL")}', f'{os.getenv('PASSWORD_EMAIL')}')
    s.send_message(msg)
    s.quit()