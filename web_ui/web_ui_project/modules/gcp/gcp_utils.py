from oauth2client import client as oauth2client
import httplib2


def authenticate(scopes, http=None):
    """
    google cloud platform authentication.
    :param scopes: authentication target scopes
    :param http: http module(optional)
    :return: (authenticated credentials, http module)
    """
    credentials = oauth2client.GoogleCredentials.get_application_default()
    if credentials.create_scoped_required():
        credentials = credentials.create_scoped(scopes)
    if http is None:
        http = httplib2.Http(timeout=60)  # 60 sec

    credentials.authorize(http)
    return credentials, http
