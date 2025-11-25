# utils.py
def normalize_url(url):
    if not url.startswith(('http://', 'https://')):
        return 'http://' + url
    return url

