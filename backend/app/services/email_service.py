import smtplib
from email.mime.text import MIMEText
from app.config import settings
from app.models.order_request import OrderRequest


def notify_new_order_request(request: OrderRequest) -> None:
    """
    Simple SMTP email to the owner when a new order request comes in
    (Handbook Section 11). Silently skips if SMTP isn't configured yet --
    the badge counter in the admin panel still works either way.
    """
    if not settings.smtp_host or not settings.notify_email:
        return

    body = (
        f"New order request from {request.shop_name} ({request.contact_phone})\n"
        f"Note: {request.note or '-'}\n"
        f"Items: {len(request.items)}\n"
        f"Log in to the admin panel to review and confirm."
    )
    msg = MIMEText(body)
    msg["Subject"] = f"New order request from {request.shop_name}"
    msg["From"] = settings.smtp_user
    msg["To"] = settings.notify_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except Exception as e:
        # Never let email failure break the order-request flow
        print(f"[email] Failed to send notification: {e}")
