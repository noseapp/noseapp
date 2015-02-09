# -*- coding: utf-8 -*-

from selenium.webdriver.ie.webdriver import WebDriver as IeWebDriver
from selenium.webdriver.opera.webdriver import WebDriver as OperaWebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.phantomjs.webdriver import WebDriver as PhantomJSWebDriver


IE = 'ie'
OPERA = 'opera'
CHROME = 'chrome'
FIREFOX = 'firefox'
PHANTOMJS = 'phantomjs'


__all__ = (
    IE,
    OPERA,
    CHROME,
    FIREFOX,
    PHANTOMJS,
    IeWebDriver,
    OperaWebDriver,
    RemoteWebDriver,
    ChromeWebDriver,
    FirefoxWebDriver,
    PhantomJSWebDriver,
)
