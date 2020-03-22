from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

'''
THIS CLASS ASSUMES ALL <IFRAME>'S HAVE AN ID ATTRIBUTE
THIS CLASS ASSUMES ASYNC <IFRAME>'S WILL BE ADDED TO THE DOM AT THE default_content() LEVEL
'''

__author__ = "Todd Kingham"
__copyright__ = "Copyright 2019, Selenium Iframe Recursion"
__credits__ = ["Todd Kingham"]
__license__ = "GPL"
__version__ = "0.0.2"
__maintainer__ = "Todd Kingham"
__email__ = "toddkingham@gmail.com"
__status__ = "Experimental"

class Iframes():
    driver = None
    iframes = {}

    '''
    __init__() will be called on instantiation, and will map all existing <iframe>'s for easier
    switching between frames
    '''
    def __init__(self, driver):
        # set the driver to the class property
        self.driver = driver

        # set the driver to the default content frame to start off
        self.driver.switch_to.default_content()

        # down the rabbit hole... the __map__() method will:
        # recurse the DOM,
        # find all nested <iframes>,
        # and set a reference to it in self.iframes
        self.__map__([])

        # now that we have mapped all iframes to self.iframes, let's the driver back to the default
        self.driver.switch_to.default_content()

    '''
    __map__() is an "internal method" called from __init__() and recursively from within itself.
    it will map a reference of every <iframe> it finds to self.iframes where the key will be the 
    HTML "id" of the <iframe> and the value will be an array of ancestor iframe elements. It also
    can get called from switch_to() in an attempt to locate an iframe that was added to the DOM 
    dynamically after initial page render
    '''
    def __map__(self, path):
        # first, find all iframes at this level ...
        iframes = self.driver.find_elements_by_tag_name('iframe')

        # ...and loop through those iframes...
        for iframe in iframes:

            # ... so we can add them to self.iframes (if they aren't already there)
            key = iframe.get_attribute('id')
            if key not in self.iframes:
                self.iframes[key] = path + [iframe]

            # now, while still in the loop lets switch to the iframe we're currently looping & re-run this process there
            self.driver.switch_to.frame(iframe)
            self.__map__(self.iframes[key])

        # finally, outside the loop move back to the parent frame so we can leave off where we started
        self.driver.switch_to.parent_frame()

    '''
    switch_to() is the only public method exposed in this class and is used as an 
    override to the driver.switch_to.frame() method. you simply pass an iframe ID to
    it and it will automatically move between frames without the need to do so manually
    '''
    def switch_to(self, key):
        # reset to the top window
        self.driver.switch_to.default_content()

        # create a new mapping in self.iframes in case the
        # requested <iframe> didn't exist when the page loaded.
        if key not in self.iframes:
            self.__map__([])

        if key not in self.iframes:
            wait = WebDriverWait(self.driver, 300)
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, key)))

        else:
            # loop over the list off ancestor frames until we reach the level of the <iframe> requested
            for iframe in self.iframes[key]:
                self.driver.switch_to.frame(iframe)
