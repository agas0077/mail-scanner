# Standard Library
import base64
import datetime
import email
import imaplib
import os
import quopri
from email.message import Message
from pathlib import Path
from typing import List

# Third Party Library
import alive_progress


class MailMonitor:
    def __init__(
        self,
        imap_server: str,
        mail_monitor_email: str,
        mail_monitor_password: str,
    ) -> None:
        """
        Open connection to imap server and connect to inbox folder.
        To change folder call select_folder(folder) method.
        """
        self.email_ids = None
        self.mail = imaplib.IMAP4_SSL(imap_server)
        self.mail.login(mail_monitor_email, mail_monitor_password)
        self.select_folder()

    def _get_email(self, mail_id: int) -> Message:
        """Get email by its id and return Message object model."""

        # "(RFC822)" - all mail info
        result, data = self.mail.fetch(mail_id, "(RFC822)")

        if result != "OK":
            raise ValueError(f"Can't fetch email by its id {mail_id}.")

        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        return email_message

    def _decode_string(self, encoded_string: str) -> str:
        """
        Decode an encoded string using Base64 or Quoted-Printable.
        Return a decoded string.

        -   encoded_string: str. The encoded string to decode.
            str: The decoded string.

        Examples:
            >>> _decode_string('=?koi8-r?B?8/Xt4SAxMi4wNC5jc3Y=?=')
            'Пример текста в кодировке KOI8-R'
        """
        decoded_string = ""
        for part, encoding in email.header.decode_header(encoded_string):
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or "utf-8")
            else:
                decoded_string += part
        if encoded_string.startswith("=?") and encoded_string.endswith("?="):
            _, charset, __, encoding, *___ = encoded_string.split("?")
            if encoding.lower() == "b":
                decoded_string = base64.b64decode(decoded_string).decode(charset)
            elif encoding.lower() == "q":
                decoded_string = quopri.decodestring(decoded_string).decode(charset)
        return decoded_string

    def _check_name_exists(self, name: str, index: int = 1) -> str:
        """
        Checks if a file with the given name exists in the list
        of downloaded file paths.
        If a file with the same name exists, adds an index to the name
        and recursively calls itself
        until a unique file name is found.

        Args:
            name (str): The name of the file to check.
            index (int, default 1): The starting index to add to the file name.

        Returns:
            str: A unique file name.
        """
        exists = any(
            [os.path.basename(path) == name for path in self.downloaded_file_paths]
        )

        if exists:
            name, ext = os.path.splitext(name)
            name = f"{name} {index}{ext}"
            return self._check_name_exists(name, index=index + 1)

        return name

    def get_file_name(self, *args, **kwargs) -> str:
        """
        Generate file name by adding hash and email sending date to actual
        file name.
        Can be redefined in subclass to change the pattern.
        Called in download_attachments method.
        """
        part = kwargs.get("part")
        email_message = kwargs.get("email_message")

        # Get message recieved datetime and convert it to a string
        msg_date = datetime.datetime.strptime(
            email_message.get("Date"), "%a, %d %b %Y %H:%M:%S %z"
        )
        msg_date = msg_date.strftime("%d-%m-%Y")

        # Get actual file name
        file_name = self._decode_string(part.get_filename())

        name, ext = os.path.splitext(file_name)

        filename = f"{msg_date}_{name}{ext}"

        filename = self._check_name_exists(filename)
        return filename

    def select_folder(self, mail_monitor_folder: str = "inbox") -> None:
        """
        Switch between mail folders. Default 'inbox'.
        -   mail_monitor_folder: str. Name of the folder to work with.
        """
        self.mail.select(mail_monitor_folder)

    def search_mail(self, searching_string: str) -> List[int]:
        """
        Return a list of email ids matching specified searching string.

        -   searching_string - a string containing searching criterions
            such as f'(SUBJECT "{a}") (FROM "{b}")'.

        Conditions for searching_string.

        ALL
            All messages in the mailbox; the default initial key for
            ANDing.

        ANSWERED
            Messages with the Answered flag set.

        BCC
            Messages that contain the specified string in the envelope
            structure's BCC field.

        BEFORE
            Messages whose internal date (disregarding time and timezone)
            is earlier than the specified date.

        BODY
            Messages that contain the specified string in the body of the
            message.

        CC
            Messages that contain the specified string in the envelope
            structure's CC field.

        DELETED
            Messages with the Deleted flag set.

        DRAFT
            Messages with the Draft flag set.

        FLAGGED
            Messages with the Flagged flag set.

        FROM
            Messages that contain the specified string in the envelope
            structure's FROM field.

        HEADER
            Messages that have a header with the specified field-name (as
            defined in [RFC-2822]) and that contains the specified string
            in the text of the header (what comes after the colon).  If the
            string to search is zero-length, this matches all messages that
            have a header line with the specified field-name regardless of
            the contents.

        KEYWORD
            Messages with the specified keyword flag set.

        LARGER
            Messages with an [RFC-2822] size larger than the specified
            number of octets.

        NEW
            Messages that have the Recent flag set but not the Seen flag.
            This is functionally equivalent to "(RECENT UNSEEN)".

        NOT
            Messages that do not match the specified search key.

        OLD
            Messages that do not have the Recent flag set.  This is
            functionally equivalent to "NOT RECENT" (as opposed to "NOT
            NEW").

        ON
            Messages whose internal date (disregarding time and timezone)
            is within the specified date.

        OR
            Messages that match either search key.

        RECENT
            Messages that have the Recent flag set.

        SEEN
            Messages that have the Seen flag set.

        SENTBEFORE
            Messages whose [RFC-2822] Date: header (disregarding time and
            timezone) is earlier than the specified date.

        SENTON
            Messages whose [RFC-2822] Date: header (disregarding time and
            timezone) is within the specified date.

        SENTSINCE
            Messages whose [RFC-2822] Date: header (disregarding time and
            timezone) is within or later than the specified date.

        SINCE
            Messages whose internal date (disregarding time and timezone)
            is within or later than the specified date.

        SMALLER
            Messages with an [RFC-2822] size smaller than the specified
            number of octets.

        SUBJECT
            Messages that contain the specified string in the envelope
            structure's SUBJECT field.

        TEXT
            Messages that contain the specified string in the header or
            body of the message.

        TO
            Messages that contain the specified string in the envelope
            structure's TO field.

        UID
            Messages with unique identifiers corresponding to the specified
            unique identifier set.  Sequence set ranges are permitted.

        UNANSWERED
            Messages that do not have the Answered flag set.

        UNDELETED
            Messages that do not have the Deleted flag set.

        UNDRAFT
            Messages that do not have the Draft flag set.

        UNFLAGGED
            Messages that do not have the Flagged flag set.

        UNKEYWORD
            Messages that do not have the specified keyword flag set.

        UNSEEN
            Messages that do not have the Seen flag set.
        """
        result, data = self.mail.search("utf-8", f"{searching_string}".encode("utf-8"))
        if result != "OK":
            raise ValueError(f"Searching error:\nresult - {result}\ndata - {data}")

        # ids are returned as a string and we need a list
        self.email_ids = data[0].split()
        return self.email_ids

    def download_attachments(
        self,
        file_criterion: List[List[str]],
        folder_to_save: Path,
        all_any: str = "all",
    ) -> List[Path]:
        """
        Downloads attachments that satisfy file_criterion and
        return a list of paths to a temporary folder with downloaded files.
        Arguments:
        -   file_criterion: Dict[str, str]. Keys of the dict must be names
            of email.Message object such as 'get_content_type'
            or 'get_file_name'. Values are desired values that each method
            will return.
        -   folder_to_save: str. A directory where attachments must be saved.
        -   all_any: str (default 'all'). Indicates how file_criterion dict
            will be proccessd: if all of specifide methods should equal
            their values or at least one.

        The method uses get_file_name(part) method to determine how to name
        each file. In general it just adds hash and date to a file name
        if possible. In order to change the logic of nameing,
        make a subclass and redefine the method.
        By default it gets part and email_message objects.
        -   part is a Message subpart with attachment info.
        -   email_message is main Message object.
        """
        if not self.email_ids:
            raise ValueError(
                (
                    "There is no email ids specified in "
                    f"email_ids variable ({self.email_ids}). "
                    "Try call search_mail method again "
                    "and check searching string."
                )
            )

        if all_any not in ("all", "any"):
            raise ValueError(
                "All_any argument must be only 'all' or 'any'. "
                f"Instead given {all_any}"
            )

        bar = alive_progress.alive_bar(len(self.email_ids))
        self.downloaded_file_paths = []
        with bar as bar:
            for i, id in enumerate(self.email_ids):
                bar()
                email_message = self._get_email(id)

                for part in email_message.walk():
                    # filter out non-attachemnt parts of the message
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    # check if an attachment satisfies the criteria
                    check_result = set()
                    for method, required_val in file_criterion:
                        value = getattr(part, method)()
                        value = self._decode_string(value)
                        check_result.add(required_val in value)

                    if all_any == "all":
                        go_flag = all(check_result)
                    if all_any == "any":
                        go_flag = any(check_result)

                    # saves attachment
                    if go_flag:
                        temp_file_path = os.path.join(
                            folder_to_save,
                            self.get_file_name(part=part, email_message=email_message),
                        )
                        with open(temp_file_path, "wb") as f:
                            f.write(part.get_payload(decode=True))

                        self.downloaded_file_paths.append(temp_file_path)

        return self.downloaded_file_paths
