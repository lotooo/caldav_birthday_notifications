#!/usr/bin/env python
import caldav
import logging
import sys
import re
import os
from mailer import Mailer
from mailer import Message
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime, timedelta, date

calendar_url = "https://%s:%s@%s" % (
    os.environ.get("WEBDAV_USER"), 
    os.environ.get("WEBDAV_PASS"), 
    os.environ.get("WEBDAV_URL"), 
)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

def search_birthdays(calendar, days=7):
    logging.info("Searching: Next %d days birthdays" % days)
    events = calendar.date_search(datetime.today(), datetime.today() + timedelta(days=days))
    return events

class Birthday:
    def __init__(self,event):
        for data in event.data.split('\r\n'):
            if data.startswith('SUMMARY:'):
                self.summary = data.split(':')[1]
            if data.startswith('DTSTART;VALUE=DATE:'):
                d = data.split(':')[1]
                self.date = date(int(d[0:4]), int(d[4:6]), int(d[6:8]))
    def __str__(self):
        return "  - %s: %s" % (self.date, self.summary)

class Report:
    def __init__(self, calender, days):
        self.duration = days
        self.birthdays = [ Birthday(event) for event in search_birthdays(calendar=calendar, days=days) ]

logging.info("Connecting to caldav calendar")
client = caldav.DAVClient(calendar_url)
principal = client.principal()
calendars = principal.calendars()

if len(calendars) > 0:
    calendar = calendars[0]
else:
    logging.error("No calendar found")
    sys.exit(1)

reports = [ Report(calendar, days=7), Report(calendar, days=30) ]

env = Environment(loader=FileSystemLoader('templates'), autoescape=select_autoescape(['html', 'xml']))

template = env.get_template('email_notification.html')
email_body_html = template.render(reports=reports)

message = Message(From=os.environ.get('EMAIL_FROM'),
                  To=[os.environ.get('EMAIL_TO')],
                  charset="utf-8")
message.Subject = "Rappel anniversaires !"
message.Html = email_body_html
message.Body = """This is alternate text."""

sender = Mailer(os.environ.get('SMTP_HOST'), port=os.environ.get('SMTP_PORT'), use_tls=False, use_ssl=True)
sender.login(os.environ.get('SMTP_USER'),os.environ.get('SMTP_PASS'))
sender.send(message)
