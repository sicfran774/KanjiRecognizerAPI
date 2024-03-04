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

class EmailDriver():
    def __init__(self):
        self.sender = None
        self.password = None
        self.host = None
        self.port = None

        self.db = None
        self.accounts = None
        self.subscriped = None

        self.emailHeader = ""
        self.emailFooter = ""
        self.utc = None

        self.init_envs()
        self.init_db()
        self.init_misc()
    
    def init_envs(self):
        # Load .env
        load_dotenv()
        self.sender = os.getenv('EMAIL')
        self.password = os.getenv('APP_PASSWORD')
        self.host = os.getenv('EMAIL_HOST')
        self.port = os.getenv('EMAIL_PORT')

    def init_db(self):
        # Load database
        self.db = get_database()
        self.accounts = self.db["accounts"]
        self.subscribed = self.accounts.find({ "subscribed": True })

    def init_misc(self):
        self.utc=pytz.UTC
        self.emailHeader = """
            <div>
                <h1>Trace Kanji</h1>
                <h3>Don't forget to study your kanji today!</h3>
            </div>
        """
        self.emailFooter = """
            <div>
                <h3>
                    <a href="https://tracekanji.com">Click here to start studying!</a> がんばって！
                </h3> 
            </div>
        """

    def separate_accounts(self):
        now = self.utc.localize(datetime.utcnow())
        print(now)
        for account in self.subscribed:
            email = account['email']
            decks = []
            counts = []
            for deck in account['decks']:
                decks.append(self.filter_by_date(deck, now, True))        
            for deck in decks:
                counts.append(self.count_kanji(deck))
            decks = []
            for deck in account['decks']:
                decks.append(self.filter_by_date(deck, now))

            print(email, decks, counts)
            self.build_HTML(email, decks, counts)

        return {"result": "Success!"}

    def filter_by_date(self, deck, now, count=False):
        due_kanjis = [] if count else [deck[0]]
        for i in range(2, len(deck)):
            kanji_time = parser.parse(deck[i]['due'])
            if kanji_time < now:
                due_kanjis.append(deck[i]) if count else due_kanjis.append(deck[i]['kanji'])

        return due_kanjis

    def count_kanji(self, deck):
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

    def build_HTML(self, email, decks, counts):
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
                {self.emailHeader}
                {body}
                {self.emailFooter}
            </div>
        """

        self.send_email(html, email)

    def send_email(self, body, email):
        msg = MIMEMultipart()
        msg['Subject'] = "もしもし… Don't forget to study your kanji! Your Daily Trace Kanji Reminder"

        html = MIMEText(body, 'html')
        msg.attach(html)

        smtp = smtplib.SMTP_SSL(self.host, self.port)
        smtp.ehlo()
        smtp.login(self.sender, self.password)
        
        smtp.sendmail(self.sender, email, msg.as_string())
        print("Email sent to " + email)
        smtp.quit()