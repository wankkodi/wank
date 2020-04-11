# random
import random

# Abstract
from abc import ABCMeta, abstractmethod

from .. import Enum


class TestStatus(Enum):
    __order__ = 'TRUE_STATUS, FALSE_STATUS, NOT_SUPPORTED_STATUS, SUSPICIOUS_STATUS'
    TRUE_STATUS = 1
    FALSE_STATUS = 2
    NOT_SUPPORTED_STATUS = 3
    SUSPICIOUS_STATUS = 4
    ERROR = 4


class BaseTest(object):
    metaclass = ABCMeta

    @property
    def _incomparable_object_types(self):
        return (self.test_module.categories_enum.VIDEO, self.test_module.categories_enum.SEARCH_PAGE,
                self.test_module.categories_enum.VIDEO_PAGE)

    @property
    def _search_object_type(self):
        return self.test_module.categories_enum.SEARCH_MAIN

    @property
    @abstractmethod
    def _available_tests(self):
        """
        Tuple of (test name, test method, object types the test is applied on)
        :return:
        """
        raise NotImplementedError

    def __init__(self, test_module):
        """
        C'tor.
        :param test_module: Test module (Fetcher)
        """
        super(BaseTest, self).__init__()
        self.test_module = test_module

    def _sub_pages_difference_test(self, test_obj, number_of_test_pages=3):
        """
        Compares the first and random picked page from the available test object sub objects.
        :param test_obj: Test object.
        :param number_of_test_pages: Number of test pages.
        :return: True if the random object differs from the first one and is not empty. False otherwise.
        """
        if test_obj.object_type in self._incomparable_object_types:
            # We reached the object
            # todo: to manage those objects to run video download test in the future...
            return TestResult(status=TestStatus.NOT_SUPPORTED_STATUS,
                              message='Not supported object type {ot}'.format(ot=test_obj.object_type))
        if test_obj.sub_objects is None:
            self.test_module.fetch_sub_objects(test_obj)
            if test_obj.sub_objects is None:
                self.test_module.fetch_sub_objects(test_obj)
        if test_obj.sub_objects is None or len(test_obj.sub_objects) == 0:
            return TestResult(status=TestStatus.FALSE_STATUS,
                              message='{p} has no sub elements'.format(p=test_obj.title))
        if len(test_obj.sub_objects) == 1:
            return TestResult(status=TestStatus.TRUE_STATUS)
        first_object = test_obj.sub_objects[0]
        first_res = self.test_module.fetch_sub_objects(first_object)
        if first_res is None or len(first_res) == 0:
            return TestResult(status=TestStatus.FALSE_STATUS,
                              message='{p} has no sub elements'.format(p=first_object.title))
        additional_objects = random.sample(test_obj.sub_objects[1:], min(number_of_test_pages,
                                                                         len(test_obj.sub_objects[1:])))
        for second_object in additional_objects:
            second_res = self.test_module.fetch_sub_objects(second_object)
            if second_res is None or len(second_res) == 0:
                return TestResult(status=TestStatus.FALSE_STATUS,
                                  message='{p} has no sub elements'.format(p=second_object.title))
            if all(x.id == y.id for x, y in zip(first_res, second_res)):
                return TestResult(status=TestStatus.FALSE_STATUS,
                                  message='Pages {p1}, {p2} has the same results'.format(p1=first_object.title,
                                                                                         p2=second_object.title))
        # If we are here, everything went smoothly...
        return TestResult(status=TestStatus.TRUE_STATUS)

    def _run_over_subclasses(self, test_method, test_args=None, results_summary=None, init_object=None, search_query='',
                             number_of_test_pages=3):
        """
        Make BFS run over all the sub_pages and perform the available tests
        :param test_method: Test method we are running over.
        :param test_args: Test method arguments.
        :param results_summary: Array of result summary..
        :param init_object: Init object on which we go one step further.
        :param search_query: Search query we are using in order to perform the test..
        :param number_of_test_pages: Number of test pages on the second hierarchy.
        :return:
        """
        if results_summary is None:
            results_summary = []
        if test_args is None:
            test_args = ()
        if init_object is None:
            # Main section
            init_object = self.test_module.dummy_super_object
            test_objects = init_object.sub_objects
        else:
            # Subsection
            if init_object.sub_objects is None:
                self.test_module.fetch_sub_objects(init_object)
                if init_object.sub_objects is None:
                    # Empty page
                    return TestResult(status=TestStatus.TRUE_STATUS)
            test_objects = random.sample(init_object.sub_objects, min(number_of_test_pages,
                                                                      len(init_object.sub_objects)))

        for sub_element in test_objects:
            if sub_element.object_type == self._search_object_type:
                self.test_module.search_query(search_query)
            elif sub_element.object_type == self.test_module.categories_enum.VIDEO:
                continue
            res = test_method(sub_element, *test_args)
            if res.status != TestStatus.NOT_SUPPORTED_STATUS:
                # We skip that test
                results_summary.append(res)
            self._run_over_subclasses(test_method, test_args, results_summary, sub_element, search_query,
                                      number_of_test_pages)
        return results_summary

    def main_test(self):
        return NotImplemented

    @staticmethod
    def print_test_results(test_name, test_results):
        """
        Prints the test results. Only those which wasn't successful are being printed explicitly.
        :param test_name: Test Name
        :param test_results: Test results. List of TestResult objects.
        :return:
        """
        suspicious_tests = [x for x in test_results if x.status == TestStatus.SUSPICIOUS_STATUS]
        unsuccessful_tests = [x for x in test_results if x.status == TestStatus.FALSE_STATUS]
        number_all_tests = len(test_results)
        number_successful_tests = number_all_tests - len(unsuccessful_tests) - len(suspicious_tests)
        status_sign = '✓' if number_all_tests == number_successful_tests else \
            ('✗' if len(unsuccessful_tests) > 0 else '?')
        print('{s} Test {tn}: {st}/{tt} successful results.'.format(s=status_sign,
                                                                    tn=test_name, st=number_successful_tests,
                                                                    tt=number_all_tests))
        if len(unsuccessful_tests) > 0:
            print('The following errors were found:')
            for x in unsuccessful_tests:
                print('\t{e}'.format(e=x.message))
        if len(suspicious_tests) > 0:
            print('The following suspicious results were found:')
            for x in suspicious_tests:
                print('\t{e}'.format(e=x.message))


class TestResult(object):
    def __init__(self, status, message=None):
        self.status = status
        self.message = message
