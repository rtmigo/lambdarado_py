import os
import sys
import urllib.request

# Class of different styles

RED = '\033[31m'
GREEN = '\033[32m'
CRESET = '\033[0m'


def get_text(url: str) -> str:
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    return response.read().decode('utf8')


if __name__ == "__main__":
    baseurl = sys.argv[1]
    print(f"Testing URL {baseurl}")
    os.system('')  # color support https://stackoverflow.com/a/54955094
    try:
        assert get_text(f'{baseurl}/a') == 'AAA'
        assert get_text(f'{baseurl}/b') == 'BBB'
        print(f"{GREEN}TEST OK!{CRESET}")
    except:
        print(f"{RED}TEST FAILED!{CRESET}")
        exit(1)

# text = get_text(f'{baseurl}/hello-server')
# if text != 'Hello, Client!':
