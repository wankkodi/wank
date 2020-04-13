from .base_test import BaseTest, TestResult, TestStatus

# # Permutations
from itertools import product

# Page types
from ..catalogs.porn_catalog import *
from ..fetchers.porn_fetcher import PornFetchUrlError

# Random
import random


class PornTest(BaseTest):
    # _incomparable_object_types = (PornCategories.VIDEO, PornCategories.SEARCH_PAGE, PornCategories.VIDEO_PAGE)
    # _search_object_type = PornCategories.SEARCH_MAIN

    @property
    def _available_tests(self):
        """
        Tuple of (test name, test method, object types the test is applied on)
        :return:
        """
        return (
            ('Sub pages difference test', self.pages_difference_test),
            ('All object filters test', self.all_original_filter_test),
            # ('Single object filters test', self.sort_order_original_filter_test, ),
        )

    def __init__(self, test_module):
        super(PornTest, self).__init__(test_module)

    def pages_difference_test(self):
        return self._run_over_subclasses(self._sub_pages_difference_test, search_query='anal')

    def all_original_filter_test(self):
        """
        Compares the first and random picked page from the available test object sub objects.
        :return: True if the random object differs from the first one and is not empty. False otherwise.
        """
        return self._run_over_filter_subclasses(self._all_original_filter_test, search_query='anal')

    def sort_order_original_filter_test(self):
        """
        Compares the first and random picked page from the available test object sub objects.
        :return: True if the random object differs from the first one and is not empty. False otherwise.
        """
        return self._run_over_filter_subclasses(self._single_original_filter_test, test_args=('sort_order', ),
                                                search_query='anal')

    def _all_original_filter_test(self, test_obj):
        """
        Compares the first and random picked page from the available test object sub objects.
        :param test_obj: Test object.
        :return: True if the random object differs from the first one and is not empty. False otherwise.
        """
        # available_filters = [x for x in self.test_module._video_filters]
        object_filters = self.test_module.get_proper_filter(test_obj)
        #     object_filters = self.test_module.get_proper_filter(test_obj)
        #     object_available_filters = [(x, getattr(object_filters, x)) for x in object_filters]

        object_available_filters = [(x, object_filters.filters[x]) for x in object_filters]
        object_original_filters = [(x[0], object_filters.current_filters[x[0]].filter_id) for x in
                                   object_available_filters]

        # if test_obj.true_object.object_type.category_type == PornCategoryTypes.VIDEO_CATEGORY:
        #     object_filter_combinations = list(product(*([(x[0], y) for y in x[1]] for x in object_available_filters
        #                                                 if x[0] != FilterTypes.SORT_ORDER_TYPE)))
        # else:
        #     object_filter_combinations = list(product(*([(x[0], y) for y in x[1]] for x in object_available_filters)))

        # The check for legal combination is being done inside the _object_filter_test_for_given_filter method
        object_filter_combinations = list(product(*([(x[0], y) for y in x[1]] for x in object_available_filters)))

        return self._object_filter_test_for_given_filter(test_obj, object_filter_combinations, object_original_filters)

    def _single_original_filter_test(self, test_obj, filter_name):
        """
        Compares the first and random picked page from the available test object sub objects.
        :param test_obj: Test object.
        :return: True if the random object differs from the first one and is not empty. False otherwise.
        """
        object_filters = self.test_module.get_proper_filter(test_obj)

        object_available_filters = [(x, object_filters.filters[x]) for x in object_filters]
        object_original_filters = [(x[0], object_filters.current_filters[x[0]].filter_id) for x in
                                   object_available_filters]

        object_filter_combinations = list(product(*([(x[0], y) for y in x[1]] for x in object_available_filters
                                                    if x[0] == filter_name)))

        return self._object_filter_test_for_given_filter(test_obj, object_filter_combinations, object_original_filters)

    def _object_filter_test_for_given_filter(self, test_obj, object_filter_combinations, object_original_filters):
        """
        Compares the first and random picked page from the available test object sub objects.
        :param test_obj: Test object.
        :param object_filter_combinations: Combinations of object filters.
        :return: True if the random object differs from the first one and is not empty. False otherwise.
        """
        def return_original_filters():
            for _fl in object_original_filters:
                object_filters.set_current_filter(*_fl)
            test_obj.clear_sub_objects()

        object_filters = self.test_module.get_proper_filter(test_obj)
        all_results = []
        min_number_of_sub_pages = 1000000
        for object_filter_combination in object_filter_combinations:
            if len(object_filter_combination) == 0:
                # Empty sequence
                continue
            # Common section
            # todo: make special parameter of default video pages _default_sort_by and use it value to check whether
            #  the sort order is the same as desired in the page (instead of 1).
            if (
                    any(any(z == y[0] and object_filters.conditions[x[0]][z] is not None and
                            y[1] not in object_filters.conditions[x[0]][z]
                            for z in object_filters.conditions[x[0]]
                            for y in object_filter_combination)
                        for x in object_filter_combination) or
                    (test_obj.true_object.object_type.category_type == PornCategoryTypes.VIDEO_CATEGORY and 1)
            ):
                # We have forbidden combination
                continue
            for object_filter in object_filter_combination:
                object_filters.set_current_filter(*object_filter)
            if test_obj.sub_objects is not None:
                test_obj.clear_sub_objects()

            if test_obj.object_type not in (PornCategories.PAGE, PornCategories.VIDEO_PAGE, PornCategories.SEARCH_PAGE):
                # We only look for number of sub objects
                try:
                    res = self.test_module.fetch_sub_objects(test_obj)
                    if res is None:
                        # For debug purpose
                        continue
                    if len(res) < min_number_of_sub_pages:
                        min_number_of_sub_pages = len(res)
                except PornFetchUrlError as err:
                    return TestResult(status=TestStatus.ERROR,
                                      message='Got redirection to non-existing page.\n'
                                              '{err}'.format(err=err)), None

            else:
                try:
                    res = self.test_module.fetch_sub_objects(test_obj)
                    if res is None:
                        # For debug purpose
                        continue
                    for prev_res in all_results:
                        if (
                                len(res) > 1 and len(res) == len(prev_res[0]) and
                                all(x.title == y.title for x, y in zip(res, prev_res[0]))
                        ):
                            return_original_filters()
                            return TestResult(status=TestStatus.SUSPICIOUS_STATUS,
                                              message='Same Result:'
                                                      '\n\t{cr}\n\t{pr}\n\t{url}'
                                                      ''.format(cr=object_filter_combination,
                                                                pr=prev_res[1],
                                                                url=test_obj.url)), None
                    all_results.append((res, object_filter_combination))
                except PornFetchUrlError:
                    pass

        if test_obj.object_type not in (PornCategories.PAGE, PornCategories.VIDEO_PAGE, PornCategories.SEARCH_PAGE):
            # Return the previous filters
            return_original_filters()
            return TestResult(status=TestStatus.NOT_SUPPORTED_STATUS,
                              message='Not supported object type {ot}'
                                      ''.format(ot=test_obj.object_type)), min_number_of_sub_pages
        else:
            # Return the previous filters
            return_original_filters()
            return TestResult(status=TestStatus.TRUE_STATUS), None

    def _run_over_filter_subclasses(self, test_method, test_args=None, results_summary=None, init_object=None,
                                    search_query='', min_number_of_test_pages=None, number_of_test_pages=3):
        """
        Make BFS run over all the sub_pages and perform the available tests
        :param test_method: Test method we are running over.
        :param test_args: Test method arguments.
        :param results_summary: Array of result summary..
        :param init_object: Init object on which we go one step further.
        :param search_query: Search query we are using in order to perform the test..
        :param min_number_of_test_pages: Minimal number of test pages on the second hierarchy.
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
            test_sub_objects = init_object.sub_objects
        else:
            # Subsection
            if init_object.sub_objects is None:
                self.test_module.fetch_sub_objects(init_object)
                if init_object.sub_objects is None:
                    # Empty page
                    return TestResult(status=TestStatus.TRUE_STATUS)
            test_sub_objects = init_object.sub_objects if min_number_of_test_pages is None \
                else init_object.sub_objects[:min_number_of_test_pages]
            test_sub_objects = random.sample(test_sub_objects, min(number_of_test_pages,
                                                                   len(test_sub_objects)))

        for sub_element in test_sub_objects:
            if sub_element.object_type == self._search_object_type:
                self.test_module.search_query(search_query)
            elif sub_element.object_type == self.test_module.categories_enum.VIDEO:
                continue
            res, min_number_of_test_pages = test_method(sub_element, *test_args)
            if res.status != TestStatus.NOT_SUPPORTED_STATUS:
                # We skip that test
                results_summary.append(res)
            self._run_over_filter_subclasses(test_method, test_args, results_summary, sub_element, search_query,
                                             min_number_of_test_pages, number_of_test_pages)
        return results_summary

    # def filters_test(self, test_obj):
    #     """
    #     Compares the first and random picked page from the available test object sub objects.
    #     :param test_obj: Test object.
    #     :return: True if the random object differs from the first one and is not empty. False otherwise.
    #     """
    #     def return_original_filters():
    #         for _fl in general_original_filters:
    #             general_filters.set_current_filter(*_fl)
    #         for _fl in object_original_filters:
    #             object_filters.set_current_filter(*_fl)
    #         test_obj.clear_sub_objects()
    #
    #     if test_obj.object_type not in (PornCategories.PAGE, PornCategories.VIDEO_PAGE, PornCategories.SEARCH_PAGE):
    #         return TestResult(status=TestStatus.NOT_SUPPORTED_STATUS,
    #                           message='Not supported object type {ot}'.format(ot=test_obj.object_type))
    #     # available_filters = [x for x in self.test_module._video_filters]
    #     object_filters = self.test_module.get_proper_filter(test_obj)
    #     object_available_filters = [(x, getattr(object_filters.filters, x)) for x in object_filters]
    #     object_original_filters = [(x[0], getattr(object_filters.current_filters, x[0]).filter_id) for x in
    #                                object_available_filters]
    #     general_filters = self.test_module.video_filters.general_filters
    #     general_available_filters = [(x, getattr(general_filters.filters, x)) for x in general_filters]
    #     general_original_filters = [(x[0], getattr(general_filters.current_filters, x[0]).filter_id) for x in
    #                                 general_available_filters]
    #     if test_obj.true_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR,
    #                                             PornCategories.TAG, PornCategories.CHANNEL):
    #         general_combinations = [general_original_filters]
    #     else:
    #         general_combinations = list(product(*([(x[0], y) for y in x[1]] for x in general_available_filters)))
    #
    #     if test_obj.true_object.object_type in PORN_VIDEO_CATEGORIES:
    #         object_combinations = list(product(*([(x[0], y) for y in x[1]] for x in object_available_filters
    #                                              if x[0] != 'sort_order')))
    #     else:
    #         object_combinations = list(product(*([(x[0], y) for y in x[1]] for x in object_available_filters)))
    #
    #     all_combinations = list(product(general_combinations, object_combinations))
    #
    #     all_results = []
    #     for general_combination, object_combination in all_combinations:
    #         if test_obj.true_object.object_type not in (PornCategories.CATEGORY, PornCategories.PORN_STAR,
    #                                                     PornCategories.TAG, PornCategories.CHANNEL):
    #             for fl in general_combination:
    #                 general_filters.set_current_filter(*fl)
    #         for fl in object_combination:
    #             object_filters.set_current_filter(*fl)
    #         if test_obj.sub_objects is not None:
    #             test_obj.clear_sub_objects()
    #         try:
    #             res = self.test_module.fetch_sub_objects(test_obj)
    #             if res is None:
    #                 # For debug purpose
    #                 continue
    #             for prev_res in all_results:
    #                 if all(x.title == y.title for x, y in zip(res, prev_res[0])):
    #                     return_original_filters()
    #                     return TestResult(status=TestStatus.FALSE_STATUS,
    #                                       message='Same Result: {nr}, {pr}'
    #                                               ''.format(nr=(general_combination, object_combination),
    #                                                         pr=prev_res[1:]))
    #             all_results.append((res, general_combination, object_combination))
    #         except PornFetchUrlError:
    #             pass
    #
    #     # Return the previous filters
    #     return_original_filters()
    #     return TestResult(status=TestStatus.TRUE_STATUS)

    def main_test(self):
        for test_name, test_method in self._available_tests:
            res = test_method()
            self.print_test_results(test_name, res)
