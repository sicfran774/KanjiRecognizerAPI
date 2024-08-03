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
        self.subscribed = None

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
        self.subscribed = self.accounts.find({ "settings.subscribed": True })

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
                    <p>To stop these emails, go to your Account Settings and uncheck &quot;Get daily email reminders to study due kanji in your decks&quot;.</p>
                </h3> 
            </div>
        """

    def separate_accounts(self):
        now = self.utc.localize(datetime.utcnow())
        print(now)
        for account in self.subscribed:
            email = account['email']
            streak = 0
            if('stats' in account and account['stats'] != None):
                streak = account['stats']['dayStreak']
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
            self.build_HTML(email, decks, counts, streak)

        return {"result": "Success!"}

    def filter_by_date(self, deck, now, count=False):
        newCardCount, reviewCount = deck[1]['newCardCount'], deck[1]['reviewCount']
        due_kanjis = [] if count else [deck[0]]
        for i in range(2, len(deck)):
            kanji_time = parser.parse(deck[i]['due'])
            if kanji_time < now or kanji_time.day == now.day:
                if not deck[i]['learning'] and not deck[i]['graduated'] and newCardCount < deck[1]['maxNewCards']:
                    newCardCount += 1
                    if count:
                        due_kanjis.append(deck[i])
                    else:
                        print("test")
                        due_kanjis.append(deck[i]['kanji'])
                elif ((deck[i]['learning'] or deck[i]['graduated'])) and reviewCount < deck[1]['maxReviews']:
                    reviewCount += 1
                    if count:
                        due_kanjis.append(deck[i])
                    else:
                        due_kanjis.append(deck[i]['kanji'])

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

    def build_HTML(self, email, decks, counts, streak):
        deckString = "<div>"

        for i in range(len(decks)):
            newCards = counts[i][0]
            reviews = counts[i][1] + counts[i][2]
            total = sum(counts[i])
            kanji = decks[i][1:]

            if total > 0:
                deckString += f"""
                    <p>
                        You have <span style="color:green;">{total}</span> kanji due in <span style="color:blue;">{decks[i][0]}</span> 
                        (<span style="color:blue;">{newCards}</span> new cards, <span style="color:red;">{reviews}</span> reviews)
                    </p>
                    <p>
                        {''.join(kanji)}
                    </p>
                """

        deckString += "</div>"

        body = f"""
            <div>
                {deckString}

                <p>You are on a <span style="color:green;">{streak}</span>-day streak!</p>
            </div>
        """

        html = f"""
            <div>
                {self.emailHeader}
                {body}
                {self.emailFooter}
            </div>
        """

        print(html)

        self.send_email(html, email)

    def send_email(self, body, email):
        msg = MIMEMultipart()
        msg['Subject'] = "もしもし… Don't forget to study your kanji! Your Daily Trace Kanji Reminder"
        msg['From'] = '"Trace Kanji"<study@tracekanji.com>'

        html = MIMEText(body, 'html')
        msg.attach(html)

        smtp = smtplib.SMTP_SSL(self.host, self.port)
        smtp.ehlo()
        smtp.login(self.sender, self.password)
        
        smtp.sendmail(self.sender, email, msg.as_string())
        print("Email sent to " + email)
        smtp.quit()

#emailer = EmailDriver()
#emailer.separate_accounts()
