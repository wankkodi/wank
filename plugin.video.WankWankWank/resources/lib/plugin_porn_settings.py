# import xbmcgui
# import xbmc
from os import path
import pickle
from datetime import datetime, timedelta


class SettingStructure(object):
    is_pin_code = None
    pin_code = None
    is_send_data = None
    last_blocked_time = None
    must_enter_pin = False


class Settings(object):
    # # Pin code select
    # pin_code_select_message_heading = 'Welcome to WANK! WANK! WANK! add-on!'
    # pin_code_select_message = 'In the following screens we will set-up the initial settings.\r\n' \
    #                           'Remember that you always can change them in the setting section in the future... ' \
    #                           'Do you want to set up the children protection PIN code?\r\n'\
    #                           'In case of 5 incorrect attempts, the login screen add-on be blocked for half an ' \
    #                           'hour.\r\n' \
    #                           'It will be impossible to restore that PIN code, so in case you forget the code, ' \
    #                           'you will must reinstall the add-on...'
    #
    # # Pin code input
    # pin_code_input = 'Please enter the page PIN code (4 digits).'
    # pin_code_input2 = 'Please validate the PIN code (4 digits).'
    # pin_code_error_heading = 'Wrong PIN code'
    # pin_code_length_error_message = 'The PIN code must have the length 4!'
    # pin_code_wrong_validation_error_message = 'The validated PIN code does not match the one stored in the system!'
    # pin_code_inconsistent_validation_error_message = 'The validated PIN code does not match the initial one! ' \
    #                                                  'lease re-enter.'
    # pin_code_user_wrong_error_message = 'The Entered PIN code is incorrect. Please re-enter. ' \
    #                                     'You have {n} attempts left.'
    #
    # # Pin code block
    # block_heading = 'You got blocked!'
    #
    # # Pin code select
    # send_data_select_message_heading = 'Do You want to send anonymous data?'
    # send_data_select_message = 'Do you want to anonymously send data to our server.\r\n' \
    #                            'This will allow us to fix any bugs ASAP and provide you quicker response, ' \
    #                            'as some of the sites settings changes dynamically and such data will improve ' \
    #                            'the overall user experience.\r\n' \
    #                            'NO PERSONAL DATA, NOR YOUR IP, WILL BE STORED IN OUR SERVERS! '

    @property
    def block_message(self):
        time_diff = self.__settings.last_blocked_time - datetime.now() + self.__block_period
        template = self.__localized_strings(42005).replace('%s', '{!s}')
        return template.format(self.__number_of_allowed_attempts, time_diff.seconds // 60, time_diff.seconds % 60)

    @property
    def is_blocked(self):
        return (self.__settings.last_blocked_time is not None and
                self.__settings.last_blocked_time + self.__block_period > datetime.now())

    @property
    def must_enter_pin(self):
        return self.__settings.must_enter_pin

    @property
    def is_use_pin(self):
        return self.__settings.is_pin_code

    @property
    def pin_code(self):
        return self.__settings.is_pin_code

    @property
    def is_send_data(self):
        return self.__settings.is_send_data

    def __init__(self, user_data_filename, dialog, localized_strings, first_run):
        self.__dialog = dialog
        self.__number_of_allowed_attempts = 5
        self.__user_data_filename = user_data_filename
        self.__localized_strings = localized_strings
        self._initialize_strings()
        # self.__default_language = None

        # todo: to change to 30, 3 is for debug purpose only
        # self.__block_period = timedelta(minutes=30)
        self.__block_period = timedelta(seconds=20)

        if not path.isfile(self.__user_data_filename):
            # We have a first run
            self.__settings = SettingStructure()
            self._prepare_first_run_setting()
        else:
            self.__load_setting()
            # xbmc.log('is_blocked: {x}'.format(x=self.is_blocked))
            if self.is_blocked:
                self.__dialog.ok(self.block_heading, self.block_message)
            if (first_run and self.__settings.is_pin_code) or self.__settings.must_enter_pin is True:
                self._check_user_pin_code()

    def _initialize_strings(self):
        # Pin code select
        self.pin_code_select_message_heading = self.__localized_strings(40001)
        self.pin_code_select_message = self.__localized_strings(40002)

        # Pin code input
        self.pin_code_input = self.__localized_strings(42011)
        self.pin_code_input2 = self.__localized_strings(42012)
        self.pin_code_error_heading = self.__localized_strings(42013)
        self.pin_code_length_error_message = self.__localized_strings(42014)
        self.pin_code_wrong_validation_error_message = self.__localized_strings(42016)
        self.pin_code_inconsistent_validation_error_message = self.__localized_strings(42017)
        self.pin_code_user_wrong_error_message = \
            self.__localized_strings(42015).replace('%s', '{!s}')

        # Pin code block
        self.block_heading = self.__localized_strings(42004)

        # Pin code select
        self.send_data_select_message_heading = self.__localized_strings(42031)
        self.send_data_select_message = self.__localized_strings(42032)

    def _check_user_pin_code(self):
        number_of_wrong_attempts = 0
        while 1:
            user_pin_code = self._input_pin_code(self.pin_code_input)
            if user_pin_code is None:
                # We want to go back
                self.__settings.must_enter_pin = True
                self.__save_setting()
                return False
            elif user_pin_code != self.__settings.pin_code:
                number_of_wrong_attempts += 1
                attempts_left = self.__number_of_allowed_attempts - number_of_wrong_attempts
                if attempts_left > 0:
                    self.__dialog.ok(self.pin_code_error_heading,
                                     self.pin_code_user_wrong_error_message.format(attempts_left)
                                     )
                else:
                    self.__settings.last_blocked_time = datetime.now()
                    self.__settings.must_enter_pin = True
                    self.__dialog.ok(self.block_heading, self.block_message)
                    self.__save_setting()
                    return False
            else:
                if self.__settings.must_enter_pin is True or self.__settings.last_blocked_time is not None:
                    self.__settings.must_enter_pin = False
                    self.__settings.last_blocked_time = None
                    self.__save_setting()
                return True

    def _prepare_pin_code_dialog(self):
        return self.__dialog.yesno(self.pin_code_select_message_heading, self.pin_code_select_message)

    def _prepare_send_data_dialog(self):
        return self.__dialog.yesno(self.send_data_select_message_heading, self.send_data_select_message)

    def _input_pin_code(self, message):
        while 1:
            res = self.__dialog.numeric(0, message)
            if len(res) == 4:
                return res
            elif len(res) == 0:
                return None
            else:
                self.__dialog.ok(self.pin_code_error_heading, self.pin_code_length_error_message)

    def _prepare_first_run_setting(self):
        self.update_is_pin_code()
        self.update_is_send_data()

    def _validate_previous_pin_code(self):
        validate_pin_code = self._input_pin_code(self.pin_code_input2)
        if self.__settings.pin_code != validate_pin_code:
            self.__dialog.ok(self.pin_code_error_heading, self.pin_code_wrong_validation_error_message)
            return False
        else:
            return True

    def update_is_pin_code(self, value=None):
        prev_value = self.__settings.is_pin_code
        if self.__settings.is_pin_code is True:
            if self._validate_previous_pin_code() is False:
                return
        while 1:
            if value is None:
                self.__settings.is_pin_code = self._prepare_pin_code_dialog()
            else:
                self.__settings.is_pin_code = value
            if self.__settings.is_pin_code:
                self.update_pin_code(validate_before_update=False)
                if self.__settings.pin_code is None:
                    if prev_value is True:
                        # We return as no action was taken and the previous settings is being stored in the system
                        return
                    else:
                        continue
            break

        if self.__settings.is_pin_code != prev_value or self.__settings.is_pin_code is True:
            self.__save_setting()
        return self.__settings.is_pin_code

    def update_settings_gui(self):
        return NotImplemented
        # prev_value = self.__settings.is_send_data
        # if value is None:
        #     self.__settings.is_send_data = self._prepare_send_data_dialog()
        # else:
        #     # todo: add dialog convincing user to change his mind...
        #     self.__settings.is_send_data = value
        # if self.__settings.is_send_data != prev_value:
        #     self.__save_setting()

    def update_is_send_data(self, value=None):
        prev_value = self.__settings.is_send_data
        if value is None:
            self.__settings.is_send_data = self._prepare_send_data_dialog()
        else:
            # todo: add dialog convincing user to change his mind...
            self.__settings.is_send_data = value
        if self.__settings.is_send_data != prev_value:
            self.__save_setting()
        return self.__settings.is_send_data

    def update_pin_code(self, validate_before_update=True):
        prev_value = self.__settings.pin_code
        if validate_before_update is True and prev_value is not None:
            if self._validate_previous_pin_code() is False:
                return
        self.__settings.pin_code = self._prepare_pin_code()
        if self.__settings.pin_code != prev_value:
            self.__save_setting()
        return self.__settings.pin_code

    def _prepare_pin_code(self):
        messages = (self.pin_code_input, self.pin_code_input2)
        while 1:
            pin_codes = []
            for i, message in enumerate(messages):
                pin_code = self._input_pin_code(message)
                if pin_code is None:
                    if i == 0:
                        return None
                    else:
                        # We want to start from the beginning
                        break
                pin_codes.append(pin_code)
            if len(pin_codes) == 2:
                if pin_codes[0] == pin_codes[1]:
                    return pin_codes[0]
                else:
                    self.__dialog.ok(self.pin_code_error_heading, self.pin_code_inconsistent_validation_error_message)

    def __save_setting(self):
        with open(self.__user_data_filename, 'wb') as fl:
            pickle.dump(self.__settings, fl)

    def __load_setting(self):
        with open(self.__user_data_filename, 'rb') as fl:
            self.__settings = pickle.load(fl)
