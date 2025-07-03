#
# * In this example, we will take advantage of the `Result<T, E>` and `Option<T>` types
# * to build a simple email server simulation.
#

from __future__ import annotations

import logging

from sain.result import Result, Ok, Err
from sain.option import Option, Some

from enum import Enum
from dataclasses import dataclass, field

# errors are basic enums with 0 overhead, not exception, their job is to
# give the user a cozy way to handle errors. with 0 try/except.


class MailError(Enum, str):
    """Possible errors when sending an email."""

    EMAIL_PARSE_ERROR = "failed to parse the email address"
    SERVER_UNAVAILABLE = "Mail server is unavailable"
    CONTENT_TOO_LONG = "Email content exceeds the maximum length"


@dataclass
class Email:
    from_: str
    """who's sending the email"""
    to: str
    """who's receiving the email"""
    subject: str = "(no subject)"
    """subject of the email"""
    content: Option[str] = field(default=Some(None))
    """content of the email, can be None if not provided."""

    # Send an email, returning `Ok(None)` if all is good,
    # otherwise returning an `Err(MailError)` with the context of the mail.
    def send(self) -> Result[None, MailError]:
        # This demonstrated parsing an email address.
        if self.from_.count("@") != 1 or self.to.count("@") != 1:
            return Err(MailError.EMAIL_PARSE_ERROR)

        # handle the absence and length of the content in one single line.
        if self.content.is_some_and(lambda content: len(content) >= 1000):
            return Err(MailError.CONTENT_TOO_LONG)

        # some http error.
        if 500:
            return Err(MailError.SERVER_UNAVAILABLE)

        # send the actual email via an API call, and handle potential HTTP errors.
        # ...
        # At the end, return Ok(None), indicating a successful send.
        return Ok(None)


# Create an email instance.
email = Email(
    from_="billgates@google.com",
    to="Jeff Bozo",
    subject="hop on lost ark",
    content=Some("buh!!!"),
)

# The best way to handle a result is via pattern matching.
match email.send():
    # Handle the success variant.
    case Ok(None):
        print("Waiting for jeff to hop on.")
    # Handle the error variant.
    case Err(reason):
        match reason:
            # Failed parsing.
            case MailError.EMAIL_PARSE_ERROR:
                print("invalid email address")
            case MailError.CONTENT_TOO_LONG:
                print("expected a fewer than 1000 characters for the content :<")
            # catch any other errors.
            case err:
                print(f"failed to send an email: {err=}")

# or just unwrap it if you need the result, not recommended since it causes runtime exceptions.
result = email.send().unwrap()
# instead, handle it with "unwrap_or", it will just log the error, if any.
result = email.send().unwrap_or_else(logging.error)
