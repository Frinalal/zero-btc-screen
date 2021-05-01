import json
import random
import time
import numpy as np
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.builder import Builder
from config.config import config
from logs import logger
from presentation.observer import Observable

DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"
API_URL = 'https://api.binance.com/api/v3/klines?symbol=DOGEEUR&interval=1m'


def get_dummy_data():
    logger.info('Generating dummy data')



def fetch_prices():
    logger.info('Fetching prices')
    #timeslot_end = datetime.now(timezone.utc)
    #end_date = timeslot_end.strftime(DATETIME_FORMAT)
    #start_data = (timeslot_end - timedelta(days=DATA_SLICE_DAYS)).strftime(DATETIME_FORMAT)
    #url = f'{API_URL}&startTime={start_data}&endTime={end_date}'
    req = Request(API_URL)
    data = urlopen(req).read()
    external_data = json.loads(data)
    trimmed_data = clean_data(external_data)
    prices = [entry[1:] for entry in trimmed_data]
    return prices

def clean_data(var):
    interm_data = [entry[:5] for entry in var]
    final_var = [[float(num) if num != float else num for num in numlist] for numlist in interm_data]
    return final_var

def main():
    logger.info('Initialize')

    data_sink = Observable()
    builder = Builder(config)
    builder.bind(data_sink)

    try:
        while True:
            try:
                prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()
                data_sink.update_observers(prices)
                time.sleep(config.refresh_interval)
            except (HTTPError, URLError) as e:
                logger.error(str(e))
                time.sleep(5)
    except IOError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        logger.info('Exit')
        data_sink.close()
        exit()


if __name__ == "__main__":
    main()
