import json
from typing import Optional

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

RED = '\033[91m'
RESET = '\033[0m'

cookies = {
    '_gcl_au': '1.1.2041851994.1678788530',
    '_gid': 'GA1.2.1264789269.1678788531',
    '_ym_uid': '1678788531347404686',
    '_ym_d': '1678788531',
    'info_cookie_block': 'info_cookie_block',
    'AMP_MKTG_a017a061b9': 'JTdCJTdE',
    'AMP_a017a061b9': 'JTdCJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJkZXZpY2VJZCUyMiUzQSUyMmY3OWU1ZGVlLTU2OGUtNGM4YS1hZjg2LThm'
                      'NzBiODRhOTkwMiUyMiUyQyUyMmxhc3RFdmVudFRpbWUlMjIlM0ExNjc4OTUxNTc3MjI2JTJDJTIyc2Vzc2lvbklkJTIyJTNB'
                      'MTY3ODk1MTU3NzE3MiU3RA==',
    '_ga': 'GA1.1.380466577.1678788531',
    '_ym_isad': '1',
    'XSRF-TOKEN': 'eyJpdiI6Im5LbktPd2JuMTA0MkNyU0tWNDhRREE9PSIsInZhbHVlIjoidDBkYUVVdjF2YkI2d0lBVVhlaEJlZm5hWWlRZG9kM3cv'
                  'RDJEV01vWWYvemo5T29XMzE0dmg1a2ZoUElOd1piQkxpdFZYNFFIWTdqQjF5VzY2L1NNaWk5bURoN0grQVVHQm9OcVZiNCt2WFBm'
                  'Tit1Z0FXYWtma29lTW1ZQUo1ajkiLCJtYWMiOiI5YjI2MmJjMTUxYWJhYjdkYmQyYmEyZTJjYjlkYzVmOTYzMmVlNzg2YzYwMmZh'
                  'Mjg5NTllNDZhOGVmYzRjM2Q2IiwidGFnIjoiIn0%3D',
    'enter_session': 'WcXx6OtIg2i62dPmQ0T17MlSACZB9zA0j8Q5RkiS',
    '_ga_E4ZP05TBD7': 'GS1.1.1678954621.8.1.1678954622.59.0.0',
}

headers = {
    'authority': 'enter.online',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'cookie': '_gcl_au=1.1.2041851994.1678788530; _gid=GA1.2.1264789269.1678788531; _ym_uid=1678788531347404686; '
              '_ym_d=1678788531; info_cookie_block=info_cookie_block; AMP_MKTG_a017a061b9=JTdCJTdE; AMP_a017a061b9=JT'
              'dCJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJkZXZpY2VJZCUyMiUzQSUyMmY3OWU1ZGVlLTU2OGUtNGM4YS1hZjg2LThmNzBiODRhO'
              'TkwMiUyMiUyQyUyMmxhc3RFdmVudFRpbWUlMjIlM0ExNjc4OTUxNTc3MjI2JTJDJTIyc2Vzc2lvbklkJTIyJTNBMTY3ODk1MTU3NzE3'
              'MiU3RA==; _ga=GA1.1.380466577.1678788531; _ym_isad=1; XSRF-TOKEN=eyJpdiI6Im5LbktPd2JuMTA0MkNyU0tWNDhRRE'
              'E9PSIsInZhbHVlIjoidDBkYUVVdjF2YkI2d0lBVVhlaEJlZm5hWWlRZG9kM3cvRDJEV01vWWYvemo5T29XMzE0dmg1a2ZoUElOd1piQ'
              'kxpdFZYNFFIWTdqQjF5VzY2L1NNaWk5bURoN0grQVVHQm9OcVZiNCt2WFBmTit1Z0FXYWtma29lTW1ZQUo1ajkiLCJtYWMiOiI5YjI2'
              'MmJjMTUxYWJhYjdkYmQyYmEyZTJjYjlkYzVmOTYzMmVlNzg2YzYwMmZhMjg5NTllNDZhOGVmYzRjM2Q2IiwidGFnIjoiIn0%3D; en'
              'ter_session=WcXx6OtIg2i62dPmQ0T17MlSACZB9zA0j8Q5RkiS; _ga_E4ZP05TBD7=GS1.1.1678954621.8.1.1678954622.'
              '59.0.0',
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/111.0.0.0 Safari/537.36',
}


def get_status(logs):
    for log in logs:
        if log['message']:
            d = json.loads(log['message'])
            try:
                content_type = 'text/html' in d['message']['params']['response']['headers']['content-type']
                response_received = d['message']['method'] == 'Network.responseReceived'
                if content_type and response_received:
                    return d['message']['params']['response']['status']
            except KeyError:
                pass


def logging(
        message: str,
        data: Optional[str] = None,
        execution_time: Optional[float] = None,
        **kwargs
) -> None:
    logger.error(f"{RED}{message}{RESET}", extra={
        "data": data, "execution_time": execution_time, **kwargs
    })
