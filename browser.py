import platform
import os
import tempfile
import urllib
import sys

class Browser:
    def __init__(self, name, path, page, installURL):
        self.page = page
        self.browser = path
        self.description = name
        self.path = path
        self.installURL = installURL

    def get_name(self):
        return self.description

    def get_page(self):
        return self.page

    def get_path(self):
        return self.path

    def get_os(self):
        return platform.system()

    @staticmethod
    def create_browser(name, path, page, installURL):
        os = platform.system()

        if os == "Linux":
            return UbuntuBrowser(name, path, page, installURL)
        elif os == "Darwin":
            return OSXBrowser(name, path, page, installURL)
        elif os == "Windows":
            return WinBrowser(name, path, page, installURL)
        else:
            assert(0)

class WinBrowser(Browser):
    def __init__(self, name, path, page, installURL):
        super().__init__(name, path, page, installURL)

    def initialize(self):
        path = ""
        file = self.browser
        tmpdir = tempfile.mkdtemp()
        if self.installURL:
            installer_file = os.path.join(tmpdir, self.installURL.split('/')[-1])

            try:
                # NOTE: .request is needed for python3
                urllib.request.urlretrieve(self.installURL, installer_file)
            except Exception:
                print("Exception while getting url: {}, {}".format(self.installURL, sys.exc_info()[1]))

            if os.path.isabs(self.browser):
                #uninstall
                os.system(installer_file + ' /S')
                print("Uninstalling old browser")

            if os.path.isabs(self.browser):
                print("Error, this should be uninstalled by now")

            os.system(installer_file + ' -ms')
            print("Installing new browser {}".format(installer_file))

            if os.path.isabs(self.browser):
                drive, path_and_file = os.path.splitdrive(self.browser)
                path, file = os.path.split(path_and_file)

# adding -setDefaultBrowswer might be needed for firefox, but fails for IE
#        cmd = "start /D \"" + path + "\" " + file + " -setDefaultBrowser " + self.page
        cmd = "start /D \"" + path + "\" " + file + " " + self.page
        print("going to execute: %s" % cmd)
        # We can't use Popen... terminate() doesn't shutdown the FF properly among all OSs
        # TODO: consider using mozprocess here
        os.system(cmd)

    def finalize(self):
        os.system("taskkill /im " + self.browser + ".exe > NUL 2>&1")

class OSXBrowser(Browser):
    def __init__(self, name, path, page, installURL):
        super().__init__(name, path, page, installURL)

    def initialize(self):
        if self.description == "Safari":
            os.system("open -a " + self.browser.replace(" ", "\\ ") + " " + ("http://" if not self.page.startswith("http") else "") + self.page)
        else:
            os.system("open -a " + self.browser.replace(" ", "\\ ") + " --args " + self.page)

    def finalize(self):
        os.system('osascript -e \"tell application \\\"' + self.browser + '\\\" to quit\"')

class UbuntuBrowser(Browser):
    def __init__(self, name, path, page, installURL):
        super().__init__(name, path, page, installURL)

    def initialize(self):
        os.system(self.browser + " " + self.page + "&")

    def finalize(self):
        if self.browser == "chromium-browser":
            os.system("wmctrl -c Chromium")
        elif self.browser == "firefox-trunk":
            os.system("wmctrl -c Nightly")
        else:
            os.system("wmctrl -c " + self.browser)
