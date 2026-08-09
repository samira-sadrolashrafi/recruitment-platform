import logging
from django.conf import settings
logger = logging.getLogger("otp")


def send_otp_sms(phone: str, code: str):

    if phone.startswith("0"):
        phone = "+98" + phone[1:]

    if settings.DEBUG:
        logger.info(f"[DEV SMS OTP] {phone} -> {code}")
        return

    logger.info(f"Production SMS OTP would be sent to {phone} -> {code}")


def send_otp_email(email: str, code: str):

    if settings.DEBUG:
        logger.info(f"[DEV EMAIL OTP] {email} -> {code}")
        return


    logger.info(f"Production Email OTP would be sent to {email} -> {code}")
