"""
Data server stores some data which needs some calculation/heavy fetching and takes care about user queries regarding
that data.
"""

# Datetime
from datetime import datetime, timedelta

# db
import sqlite3

# OS
from os import path, makedirs
import sys

# json
import json

# URL tools
from .. import urlparse


class DataServer(object):
    date_format = '%Y-%m-%d %H:%M:%S'
    max_date_margin = timedelta(days=1)

    def __init__(self, store_dir):
        self.store_dir = store_dir
        if not path.isdir(self.store_dir):
            makedirs(self.store_dir)
        self.store_filename = path.join(self.store_dir, 'server.dat')

        self._db = None
        self._prepare_db()

    def _prepare_db(self):
        """
        Maintain the logic behind the SQL db.
        """
        try:
            sql_create_site_data_table = """CREATE TABLE IF NOT EXISTS websites_data (
                                                id integer PRIMARY KEY,
                                                host text NOT NULL,
                                                name text,
                                                number_of_updates INTEGER DEFAULT 0
                                            );"""

            sql_create_page_data_table = """CREATE TABLE IF NOT EXISTS site_data (
                                                id integer PRIMARY KEY,
                                                full_url text NOT NULL,
                                                last_update_date text NOT NULL,
                                                raw_data text NOT NULL,
                                                site_id int NOT NULL,
                                                FOREIGN KEY (site_id) REFERENCES websites_data (id)
                                            );"""
            self._db = sqlite3.connect(self.store_filename)
            if self._db is None:
                pass

            c = self._db.cursor()
            c.execute(sql_create_site_data_table)
            c.execute(sql_create_page_data_table)

        except sqlite3.Error as err:
            raise err

    def fetch_request(self, url):
        """
        Fetches user request
        :param url: Url, which data we want to fetch.
        :return: dictionary with status, value of the data and error in case such occurred.
        """
        try:
            now_date = datetime.now()
            cur = self._db.cursor()
            cur.execute("SELECT last_update_date,raw_data FROM site_data WHERE full_url=?",
                        (url, ))
            fetched_data = cur.fetchall()
            if len(fetched_data) == 0:
                return {'status': False, 'value': None, 'err': 'No value exists for the page.'}
            last_update_raw_date, raw_data = fetched_data[0]
            return_data = json.loads(raw_data)
            last_update_date = datetime.strptime(last_update_raw_date, self.date_format)
            if (now_date - last_update_date) > self.max_date_margin:
                # We have an outdated data.
                return {'status': False, 'value': return_data, 'err': 'Outdated'}

            # Everything is fine
            return {'status': True, 'value': return_data, 'err': None}
        except sqlite3.Error as err:
            return {'status': False, 'value': None, 'err': str(err)}

    def push_request(self, url, user_data):
        """
        Fetches user request
        :param url: Url, which data we want to fetch.
        :param user_data: New value.
        """
        try:
            host = urlparse(url).hostname
            update_date = datetime.now().strftime(self.date_format)

            cur = self._db.cursor()
            cur.execute("SELECT id FROM websites_data WHERE host=?", (host, ))
            site_id = cur.fetchall()
            if len(site_id) > 0:
                # We have that site in our db
                site_id = site_id[0][0]
            else:
                # We want to add the website to our db
                command = ''' INSERT INTO websites_data(host)
                              VALUES(?)'''
                cur.execute(command, (host,))
                site_id = cur.lastrowid

            # Now we want to add the value itself
            cur.execute("SELECT id, raw_data FROM site_data WHERE full_url=?", (url, ))
            correct_row = list(cur.fetchall())
            if len(correct_row) == 1:
                obj_id, previous_data = correct_row[0]
                previous_data = json.loads(previous_data)
                previous_data.update(user_data)
                command = ''' UPDATE site_data
                              SET last_update_date = ? ,
                                  raw_data = ?
                              WHERE id = ?'''
                cur.execute(command, (update_date, json.dumps(previous_data), obj_id))
            else:
                command = ''' INSERT INTO site_data(full_url,last_update_date,raw_data,site_id)
                              VALUES(?,?,?,?)'''
                cur.execute(command, (url, update_date, json.dumps(user_data), site_id))

            # Now we update the count of the updates.
            # No lock is needed, since it is already implied in the python library...
            cur.execute("SELECT number_of_updates FROM websites_data WHERE id=?", (site_id, ))
            prev_count = cur.fetchall()[0][0]
            command = ''' UPDATE websites_data
                          SET number_of_updates = ?
                          WHERE id = ?'''
            cur.execute(command, (int(prev_count) + 1, site_id))
            self._db.commit()
            return {'status': True, 'value': None, 'err': None}
        except sqlite3.Error as err:
            return {'status': False, 'value': None, 'err': str(err)}

    def remove_page(self, url):
        """
        Removes the data for the given page
        :param url: Url, which data we want to remove.
        """
        try:
            cur = self._db.cursor()
            cur.execute("SELECT last_update_date,raw_data FROM site_data WHERE full_url=?",
                        (url, ))
            fetched_data = cur.fetchall()
            if len(fetched_data) == 0:
                return {'status': False, 'value': None, 'err': 'No value exists for the page.'}

            cur.execute("DELETE FROM site_data WHERE full_url=?", (url, ))
            self._db.commit()
            return {'status': True, 'value': None, 'err': None}
        except sqlite3.Error as err:
            return {'status': False, 'value': None, 'err': str(err)}

    def remove_site(self, url):
        """
        Removes the data for the given page
        :param url: Url, which data we want to remove.
        """
        try:
            cur = self._db.cursor()
            host = urlparse(url).hostname
            cur.execute("SELECT id FROM websites_data WHERE host=?", (host, ))
            site_id = cur.fetchall()
            if len(site_id) == 0:
                # We have no suc h domain
                return {'status': True, 'value': None, 'err': None}
            site_id = site_id[0][0]
            cur.execute("DELETE FROM site_data WHERE site_id=?", (site_id, ))
            cur.execute("DELETE FROM websites_data WHERE id=?", (site_id, ))
            self._db.commit()
            return {'status': True, 'value': None, 'err': None}
        except sqlite3.Error as err:
            return {'status': False, 'value': None, 'err': str(err)}


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
    res = a.remove_page('https://vqtube.com/tags/')

    # Remove host
    # res = a.remove_site('https://anyporn.com/')
    # res = a.remove_site('https://www.porngo.com/')
    # res = a.remove_site('https://www.xvideos.com/')

    print(res)
