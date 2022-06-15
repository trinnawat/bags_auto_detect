import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


sort_by_map = {
    "HIGHNEST_PRICE": "pricedsc",
    "LOWEST_PRICE": "priceasc",
    "RELEVANCE": ""
}


def print_with_ts(msg):
    dt_now = datetime.now()
    msg = f"{dt_now} : {msg}"
    print(msg)


def send_noti(msg, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {token}'
            }
    res = requests.post(url, headers=headers , data={'message':msg})
    print_with_ts(f"Line noti status: {res.status_code}")


def main():
    SORT_BY = os.getenv("SORT_BY")
    URL = os.getenv("URL")
    url = URL + "/#|" + sort_by_map.get(SORT_BY)
    DELAY_TIME_SEC = int(os.getenv("DELAY_TIME_SEC"))
    TOKEN = os.getenv("TOKEN")
    RETRY = int(os.getenv("RETRY"))
    count_retry = 0
    print_with_ts(f"Get: {url}")
    last_n = 0

    # switch_header = 1
    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"}
    headers = {}
    while True:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        if "captcha-delivery" in res.text:
            msg = "Blocked by Captcha!!!"
            print_with_ts(msg)
            send_noti(msg, TOKEN)
            count_retry += 1
            if count_retry == RETRY:
                msg = f"reach max retry: {RETRY}, process will stop..."
                print_with_ts(msg)
                send_noti(msg, TOKEN)
                break
            else:
                wait_time = 5 * 60
                msg = f"wait {wait_time} sec"
                print_with_ts(msg)
                send_noti(msg, TOKEN)
                time.sleep(wait_time)
        else:
            print_with_ts("-")
        target_component = soup.find_all(attrs={"class": "total"})[0]
        target_num = int(target_component.string.strip().replace("(", "").replace(")", ""))
        if last_n != target_num:
            # Alert!!
            last_n = target_num
            msg = f"Detect update!!!: {last_n}"
            print_with_ts(msg)
            send_noti(msg, TOKEN)
        time.sleep(DELAY_TIME_SEC)


if __name__ == "__main__":
    load_dotenv()
    main()