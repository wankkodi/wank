"""
Data server stores some data which needs some calculation/heavy fetching and takes care about user queries regarding
that data.
"""

# Internet tools
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# URL tools
from .. import urljoin


class DataServer(object):
    base_site = 'https://wankkodierrorreporter.000webhostapp.com/'

    def __init__(self, session=None):
        """
        C'tor
        :param session: Connection session (optional)
        """
        self.send_url = urljoin(self.base_site, 'send_report.php')
        if session is None:
            retries = 3
            backoff_factor = 0.3
            status_forcelist = (500, 502, 504)

            self.session = requests.session()
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
        else:
            self.session = session

    def fetch_request(self, url, page_filters, general_filters):
        """
        Fetches user request
        :param url: Url, which data we want to fetch.
        :param page_filters: Page filters.
        :param general_filters: General filters.
        :return: dictionary with status, value of the data and error in case such occurred.
        """
        params = {'action': 'get_number_of_pages',
                  'url': url,
                  'page_filters': page_filters,
                  'general_filters': general_filters}
        request_result = self.session.get(self.send_url, params=params)
        if not request_result.ok:
            raise ConnectionRefusedError(request_result.text())
        return request_result.json()

    def push_request(self, site_name, url, page_filters, general_filters, number_of_pages):
        """
        Sends new number of pages.
        :param site_name: Site name.
        :param url: Url, which data we want to fetch.
        :param page_filters: Page filters.
        :param general_filters: General filters.
        :param number_of_pages: Updated number of pages.
        :return: dictionary with status, value of the data and error in case such occurred.
        """
        params = {'action': 'push_number_of_pages',
                  'site_name': site_name,
                  'url': url,
                  'page_filters': page_filters,
                  'general_filters': general_filters,
                  'number_of_pages': number_of_pages,
                  }
        request_result = self.session.get(self.send_url, params=params)
        result_json = request_result.json()
        if not request_result.ok or result_json['status'] is False:
            raise ConnectionRefusedError(request_result.text())
        return result_json

    def push_error(self, report_type_id, site_name, url, message, page_filters, general_filters, version):
        """
        Sends new number of pages.
        :param report_type_id: Report type id. 0 for error, 1 for warning.
        :param site_name: Site name.
        :param url: Url, which data we want to fetch.
        :param message: Error message.
        :param page_filters: Page filters.
        :param general_filters: General filters.
        :param version: Module version.
        :return: dictionary with status, value of the data and error in case such occurred.
        """
        params = {'action': 'push_error',
                  'report_type_id': report_type_id,
                  'site_name': site_name,
                  'url': url,
                  'message': message,
                  'page_filters': page_filters,
                  'general_filters': general_filters,
                  'version': version,
                  }
        request_result = self.session.get(self.send_url, params=params)
        if not request_result.ok:
            raise ConnectionRefusedError(request_result.text())
        return bool(request_result.text)


if __name__ == '__main__':
    a = DataServer('../../Data/DataServer')
    # # Section with non-existing error for the first run and ok for every other
    # res = a.fetch_request('https://www.keezmovies.com/sophie-dee', 'num_of_sub_pages')
    # print('test1: ' + str(res))
    #
    # # We add a new value (suppose to be ok)
    # res = a.push_request('https://www.keezmovies.com/sophie-dee', 'num_of_sub_pages', 15)
    # print('test2: ' + str(res))

    # # We add a new value (suppose to be ok)
    # num_of_pages = 17
    # data = '["1571165181", "1566409621", "1561767293", "1557154868", "1552330016", "1547724516", "1541416217", ' \
    #        '"1535364313", "1528282398", "1522235951", "1516640931", "1510577875", "1500475842", "1494330142", ' \
    #        '"1488798649", "1486385222"]'
    # res1 = a.push_request('https://www.xvideos.com/channels/fakingsoficial', 'num_of_sub_pages', num_of_pages)
    # res2 = a.push_request('https://www.xvideos.com/channels/fakingsoficial', 'additional_data', data)
    # print('test3_1: ' + str(res1))
    # print('test3_2: ' + str(res2))

    # We remove page
    # res = a.remove_page('https://vqtube.com/tags/')

    # Remove host
    # res = a.remove_site('https://anyporn.com/')
    # res = a.remove_site('https://www.porngo.com/')
    # res = a.remove_site('https://www.xvideos.com/')

    # print(res)
