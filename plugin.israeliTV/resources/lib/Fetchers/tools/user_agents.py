import requests

# Parsing tool
# from lxml import etree
from .my_parser_wrapper import MyParser, html5lib

# Wait & random
import random
from time import sleep

# OS
from os import path, makedirs

# Pickle
import pickle

# Internet tools
from .. import urljoin


class UserAgents(object):
    base_url = 'https://developers.whatismybrowser.com/useragents/explore/software_type_specific/web-browser/'
    # browser_suffixes = {'chrome', 'internet-explorer', }
    # parser = etree.HTMLParser()
    # parser = html5lib.html5parser.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"),
    #                                          namespaceHTMLElements=False)

    def __init__(self, data_dir='Data'):
        self.parser = MyParser(tree=html5lib.treebuilders.getTreeBuilder("etree"), namespaceHTMLElements=False)
        self.data_dir = data_dir
        if not path.isdir(self.data_dir):
            makedirs(self.data_dir)
        self.user_agents_latest_filename = path.join(self.data_dir, 'user_agents_latest.dat')
        if path.isfile(self.user_agents_latest_filename):
            with open(self.user_agents_latest_filename, 'rb') as fl:
                self.user_agents = self.stored_user_agents = pickle.load(fl)
        else:
            self.user_agents = None

    def get_user_agent(self, num_of_pages=5, os_filter='Windows', common_filter='Very common'):
        """
        Randomly picks the user-agent among those which stored in the system. In case no data is stored, we fetch it...
        :param num_of_pages: number of pages we want to parse for the latest browsers. 5 by default.
        :param os_filter: Filter of the OS of the browser. None by default.
        :param common_filter: Filter of the commonness of the browser. None by default.
        :return:
        """
        if self.user_agents is None:
            self.user_agents = self.get_latest_user_agents(num_of_pages=num_of_pages, os_filter=os_filter,
                                                           common_filter=common_filter)
            with open(self.user_agents_latest_filename, 'wb') as fl:
                pickle.dump(self.user_agents, fl)
        return random.choice(self.user_agents)[0]

    def get_latest_user_agents(self, num_of_pages=5, os_filter=None, common_filter=None):
        """
        Gets the latest user agents for the browsers: Chrome, Firefox, Safari, IE, Edge, Opera.
        :param num_of_pages: number of pages we want to parse for the latest browsers. 5 by default.
        :param os_filter: Filter of the OS of the browser. None by default.
        :param common_filter: Filter of the commonness of the browser. None by default.
        :return: List of tuples of (User agent, Software name, OS, Layout engine, Popularity)
        """
        res = []
        for i in range(1, num_of_pages+1):
            url = urljoin(self.base_url, str(i))
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en',
                'Cache-Control': 'max-age=0',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/76.0.3809.100 Safari/537.36'
            }

            req = requests.get(url, headers=headers)
            # tree = etree.fromstring(req.text, self.parser)
            tree = self.parser.parse(req.text)
            xpath = './/table[@class="table table-striped table-hover table-bordered table-useragents"]/tbody/tr'
            raw_browsers = tree.xpath(xpath)
            for raw_browser in raw_browsers:
                xpath = './td'
                raw_browser_data = raw_browser.xpath(xpath)
                if len(raw_browser_data) != 5:
                    continue
                loc_res = []
                broken_flag = False
                for j, x in enumerate(raw_browser_data):
                    if j == 0:
                        xpath = './a/text()'
                    elif j == 1:
                        xpath = './@title' if 'title' in x.attrib else './text()'
                    else:
                        xpath = './text()'
                    loc_value = x.xpath(xpath)
                    if len(loc_value) != 1:
                        # Something went wrong, we skip that value
                        broken_flag = True
                        break
                    loc_res.append(str(loc_value[0]))
                if broken_flag is False and loc_res not in res:
                    res.append(loc_res)
            sleep(random.uniform(0, 5))

        if os_filter is not None:
            res = [x for x in res if x[2] == os_filter]
        if common_filter is not None:
            res = [x for x in res if x[4] == common_filter]
        return res


if __name__ == '__main__':
    ua = UserAgents()
    ua.get_latest_user_agents(num_of_pages=5, os_filter='Windows', common_filter='Very common')
