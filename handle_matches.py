from datetime import datetime

from pynder import Session

from config import X_AUTH_TOKEN, DATE_FORMAT

MATCHES_SINCE = datetime(2021, 5, 1).strftime(DATE_FORMAT)

session = Session(XAuthToken=X_AUTH_TOKEN)
new_matches = [match for match in session.matches(MATCHES_SINCE) if len(match.messages) == 0]
