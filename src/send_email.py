# Change flask endpoint .env in Vercel

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv
from load_mongo import get_database
from datetime import datetime, time
from dateutil import parser
import pytz

utc=pytz.UTC

# Load .env
load_dotenv()

sender = os.getenv('EMAIL')
password = os.getenv('APP_PASSWORD')
host = os.getenv('EMAIL_HOST')
port = os.getenv('EMAIL_PORT')

# Load database
db = get_database()
accounts = db["accounts"]
subscribed = accounts.find({ "subscribed": True })

emailHeader = """
    <div>
        <h1>Trace Kanji</h1>
        <h3>Don't forget to study your kanji today!</h3>
    </div>
"""

emailFooter = """
    <div>
        <h3>
            <a href="https://tracekanji.com">Click here to start studying!</a> がんばって！
        </h3> 
    </div>
"""

def separate_accounts():
    now = utc.localize(datetime.utcnow())
    print(now)
    for account in subscribed:
        email = account['email']
        decks = []
        counts = []
        for deck in account['decks']:
            decks.append(filter_by_date(deck, now, True))        
        for deck in decks:
            counts.append(count_kanji(deck))
        decks = []
        for deck in account['decks']:
            decks.append(filter_by_date(deck, now))

        print(email, decks, counts)
        build_HTML(email, decks, counts)

def filter_by_date(deck, now, count=False):
    due_kanjis = [] if count else [deck[0]]
    for i in range(2, len(deck)):
        kanji_time = parser.parse(deck[i]['due'])
        if kanji_time < now:
            due_kanjis.append(deck[i]) if count else due_kanjis.append(deck[i]['kanji'])

    return due_kanjis

def count_kanji(deck):
    counts = [0, 0, 0]
    if(deck):
        for kanji in deck:
            if(kanji['learning']):
                counts[1] += 1
            elif(kanji['graduated']):
                counts[2] += 1
            else:
                counts[0] += 1
    return counts

def build_HTML(email, decks, counts):
    deckString = "<div>"

    for i in range(len(decks)):
        total = sum(counts[i])
        kanji = decks[i][1:]

        deckString += f"""
            <p>
                You have <span style="color:green;">{total}</span> kanji due in <span style="color:blue;">{decks[i][0]}</span>
            </p>
            <p>
                {''.join(kanji)}
            </p>
        """

    deckString += "</div>"

    body = f"""
        <div>
            {deckString}
        </div>
    """

    html = f"""
        <div>
            {emailHeader}
            {body}
            {emailFooter}
        </div>
    """

    send_email(html, email)

def send_email(body, email):
    msg = MIMEMultipart()
    msg['Subject'] = "もしもし… Don't forget to study your kanji! Your Daily Trace Kanji Reminder"

    html = MIMEText(body, 'html')
    msg.attach(html)

    smtp = smtplib.SMTP_SSL(host, port)
    smtp.ehlo()
    smtp.login(sender, password)
    
    smtp.sendmail(sender, email, msg.as_string())
    print("Email sent to " + email)
    smtp.quit()

if __name__ == "__main__":
    separate_accounts()