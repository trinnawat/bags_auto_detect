import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from itertools import cycle
from random import randint

sort_by_map = {
    "HIGHNEST_PRICE": "pricedsc",
    "LOWEST_PRICE": "priceasc",
    "RELEVANCE": ""
}


def print_with_ts(msg):
    dt_now = datetime.now()
    msg = f"{dt_now} : {msg}"
    print(msg)


def send_noti(msg, token_list):
    url = 'https://notify-api.line.me/api/notify'
    for token in token_list:
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
    TOKEN2 = os.getenv("TOKEN2")
    token_list = [TOKEN, TOKEN2]
    RETRY = int(os.getenv("RETRY"))
    count_retry = 0
    print_with_ts(f"Get: {url}")
    last_n = 0

    random_list = map(int, os.getenv("RANDOM_LIST").split(","))
    random_list = cycle(random_list)
    random_range = list(map(int, os.getenv("RANDOM_RANGE").split(",")))
    random_mode = int(os.getenv("RANDOM_MODE"))
    # switch_header = 1
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"}
    # headers = {}
    while True:
        if count_retry == RETRY:
            msg = f"reach max retry: {RETRY}, process will stop..."
            print_with_ts(msg)
            send_noti(msg, token_list)
            break

        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        if "captcha-delivery" in res.text:
            msg = "Blocked by Captcha!!!"
            print_with_ts(msg)
            send_noti(msg, token_list)
            count_retry += 1
            # wait
            wait_time = 5 * 60
            msg = f"wait {wait_time} sec"
            print_with_ts(msg)
            send_noti(msg, token_list)
            time.sleep(wait_time)
            continue

        print_with_ts("-")
        try:
            target_component = soup.find_all(attrs={"class": "total"})[0]
        except:
            print_with_ts("Cannot read webpage")
            count_retry += 1
            print(res.text)

            # wait
            wait_time = 5 * 60
            msg = f"wait {wait_time} sec"
            print_with_ts(msg)
            send_noti(msg, token_list)
            time.sleep(wait_time)

            continue
        target_num = int(target_component.string.strip().replace("(", "").replace(")", ""))

        if last_n != target_num:
            # Alert!!
            last_n = target_num
            msg = f"Detect update!!!: {last_n}"
            print_with_ts(msg)
            send_noti(msg, token_list)
        if random_mode == 1:
            DELAY_TIME_SEC = next(random_list)
        elif random_mode == 2:
            DELAY_TIME_SEC = randint(*random_range)
        print_with_ts(f"delay: {DELAY_TIME_SEC} sec")
        time.sleep(DELAY_TIME_SEC)


if __name__ == "__main__":
    load_dotenv()
    main()
