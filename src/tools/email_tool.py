import email
import imaplib
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.config.settings import (
    IMAP_HOST,
    IMAP_PORT,
    SMTP_HOST,
    SMTP_PASS,
    SMTP_PORT,
    SMTP_USER,
)


class EmailInput(BaseModel):
    action: str = Field(
        description="Action to perform: 'send', 'read', or 'search'"
    )
    to: str = Field(default="", description="Recipient email address (for send)")
    subject: str = Field(default="", description="Email subject (for send)")
    body: str = Field(default="", description="Email body in HTML (for send)")
    search_query: str = Field(
        default="", description="Search term for subject line (for search/read)"
    )
    max_results: int = Field(
        default=5, description="Max emails to return (for search/read)"
    )


class EmailTool(BaseTool):
    name: str = "email_tool"
    description: str = (
        "Read and send emails for procurement communications. "
        "Can search inbox for supplier quotes, read emails, "
        "and send deal reports to stakeholders."
    )
    args_schema: Type[BaseModel] = EmailInput

    def _run(
        self,
        action: str,
        to: str = "",
        subject: str = "",
        body: str = "",
        search_query: str = "",
        max_results: int = 5,
    ) -> str:
        if not SMTP_USER or not SMTP_PASS:
            return json.dumps(
                {
                    "success": False,
                    "error": "Email not configured. Set SMTP_USER and SMTP_PASS in .env",
                }
            )

        if action == "send":
            return self._send_email(to, subject, body)
        elif action in ("read", "search"):
            return self._search_emails(search_query, max_results)
        else:
            return json.dumps(
                {"success": False, "error": f"Unknown action: {action}"}
            )

    def _send_email(self, to: str, subject: str, body: str) -> str:
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = SMTP_USER
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, to, msg.as_string())

            return json.dumps(
                {
                    "success": True,
                    "action": "send",
                    "to": to,
                    "subject": subject,
                }
            )
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    def _search_emails(self, search_query: str, max_results: int) -> str:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
            mail.login(SMTP_USER, SMTP_PASS)
            mail.select("inbox")

            criteria = f'(SUBJECT "{search_query}")' if search_query else "ALL"
            _, message_ids = mail.search(None, criteria)

            ids = message_ids[0].split()
            ids = ids[-max_results:]  # Get most recent

            emails = []
            for msg_id in reversed(ids):
                _, msg_data = mail.fetch(msg_id, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                body_text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body_text = part.get_payload(decode=True).decode(
                                errors="replace"
                            )[:1000]
                            break
                else:
                    body_text = msg.get_payload(decode=True).decode(
                        errors="replace"
                    )[:1000]

                emails.append(
                    {
                        "from": msg.get("From", ""),
                        "subject": msg.get("Subject", ""),
                        "date": msg.get("Date", ""),
                        "body_preview": body_text[:500],
                    }
                )

            mail.logout()

            return json.dumps(
                {
                    "success": True,
                    "action": "search",
                    "query": search_query,
                    "count": len(emails),
                    "emails": emails,
                }
            )
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
