import xbmcgui


class LoginWin(LoginBase):
    def __init__(self, *args, **kwargs):
        super(LoginBase, self).__init__(self, *args)
        self.mem = kwargs.get('member')
        self.inputwin = None

    def on_init(self):
        print("Starting onInit Loop")
        while not self.mem.logged_in:
            if self.mem.bad_creds is True:
                self.getControl(10).setLabel('Login failed! Try again...')
                print("Set fail label message")
            self.inputwin = InputDialog()
            self.inputwin.show_input_dialog()
            self.mem.login_member(self.inputwin.name_txt, self.inputwin.pswd_txt)
            print("Logged_in value: {0}".format(self.mem.logged_in))
            print("Bad Creds value: {0}".format(self.mem.bad_creds))

        print("Exited the while loop! Calling the close function")
        self.close()


class InputDialog(xbmcgui.WindowDialog):
    def __init__(self):
        self.name = xbmcgui.ControlEdit(530, 320, 400, 120, '', 'font16', '0xDD171717')
        self.addControl(self.name)
        # self.inputbox_username.setText("Here's some sample text")
        self.pswd = xbmcgui.ControlEdit(530, 320, 400, 120, '', font='font16', textColor='0xDD171717', isPassword=1)
        self.addControl(self.pswd)
        # self.inputbox_password.setText("Here's the password field")
        self.butn = xbmcgui.ControlButton(900, 480, 130, 50, 'Sign In', font='font24_title', textColor='0xDD171717',
                                          focusedColor='0xDD171717')
        self.addControl(self.butn)
        self.setFocus(self.name)
        self.name_txt = ""
        self.pswd_txt = ""

    def on_control(self, control):
        if control == self.butn:
            # print "if condition met: control == self.butn"
            # print "closing dialog window"
            self.close()
            self.name_txt = self.name.getText()
            self.pswd_txt = self.pswd.getText()
            # print self.name_txt
            # print self.pswd_txt

    def show_input_dialog(self):
        self.name.setPosition(600, 320)
        self.name.setWidth(400)
        self.name.controlDown(self.pswd)
        self.pswd.setPosition(600, 410)
        self.pswd.setWidth(400)
        self.pswd.controlUp(self.name)
        self.pswd.controlDown(self.butn)
        self.butn.controlUp(self.pswd)
        self.doModal()
