# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib
import urllib2
import sys
import re
from pushwrapper import Pushover
import hashlib


class SLError(RuntimeError):
    """
    SLError Handling
    """


class Notify(object):
    def __init__(self, bus_lines):
        self.pushover_token = ''
        self.pushover_user = ''
        self.bus_lines = bus_lines
        self.bus_lines_list = self.bus_lines.replace(',', '').split()

    def html_cleaner(self, stringy):
        stringy = str(stringy)
        clean_stringy_re = re.search('<span>(.*)</span>', stringy)
        clean_stringy = clean_stringy_re.group(1)
        return clean_stringy

    # Asp_buddy finds the viewstate and eventvalidate string from the webpage, these are necessary in order to make a POST request and they are not static

    def asp_buddy(self):
        __url__ = 'http://storningsinformation.sl.se/sv/?State=Search'
        request = urllib2.Request(__url__)
        request_open = urllib2.urlopen(request)
        request_read = request_open.read()
        soup = BeautifulSoup(request_read)
        event_validate_raw = soup.findAll('input', attrs={'id': '__EVENTVALIDATION'})
        viewstate_raw = soup.findAll('input', attrs={'id': '__VIEWSTATE'})
        viewstate_re = re.search('value="(.*)"', str(viewstate_raw))
        event_validate_re = re.search('value="(.*)"', str(event_validate_raw))
        viewstate = viewstate_re.group(1)
        event_validate = event_validate_re.group(1)
        return viewstate, event_validate


    def hash_string(self, string):
        hashedString = hashlib.md5(string).hexdigest()
        return hashedString

    def poster(self, issues):
        try:
            for x in range(0, len(issues)):
                if self.bus_lines[x] in issues['issue_{0}'.format(x)]:
                    if '{}'.format(self.hash_string(issues['issue_{0}'.format(x)])) in open('posts.db').read():
                        print("**** Message: {} previously posted: **** || {} ||".format(x, issues['issue_{0}'.format(x)]))
                    else:
                        print("Sent! Message: {}".format(issues['issue_{0}'.format(x)]))
                        self.pushover_post(issues, x)
                        postdb = open('posts.db', 'a+')
                        postdb.write('{}'.format(self.hash_string(issues['issue_{0}'.format(x)])) + '\n')
                        postdb.close()
        except IOError:
            open('posts.db', 'w').close()
            self.poster(issues)


    def pushover_post(self, issues, x):
        p = Pushover()
        p.Send(self.pushover_token, self.pushover_user, issues['issue_{0}'.format(x)])



    def issue_check(self):
        # HTML POST REQUEST TO ASP.NET SERVER

        viewstate, event_validate = self.asp_buddy()

        headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22',
            'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded'


        }
        url = 'http://storningsinformation.sl.se/Avvikelser.aspx'
        formData = (
            ('__LASTFOCUS', ''),
            ('__EVENTTARGET', ''),
            ('__EVENTARGUMENT', ''),
            ('__VIEWSTATE', '{}'.format(viewstate)),
            ('ctl00$tbx', 'yes'),
            ('ctl00$TbSearch', ''),
            ('ctl00$QuickPlannerHolder$QuickPlanner1$tbFrom', ''),
            ('ctl00$QuickPlannerHolder$QuickPlanner1$tbTo', ''),
            ('ctl00$FullRegion$Sea  rchDeviation1$cblTransportMode$0', 'on'),
            ('ctl00$FullRegion$SearchDeviation1$cblTransportMode$1', 'on'),
            ('ctl00$FullRegion$SearchDeviation1$cblTransportMode$2', 'on'),
            ('ctl00$FullRegion$SearchDeviation1$cblTransportMode$3', 'on'),
            ('ctl00$FullRegion$SearchDeviation1$What', 'rbWhat2'),
            ('ctl00$FullRegion$SearchDeviation1$tbLineNumber', '{}'.format(self.bus_lines)),
            ('ctl00$FullRegion$SearchDeviation1$tbStopArea', ''),
            ('ctl00$FullRegion$SearchDeviation1$ddlFromDate ', 'Now'),
            ('ctl00$FullRegion$SearchDeviation1$btnSubmit', 'Sök'),
            ('__EVENTVALIDATION', '{}'.format(event_validate))
            )
        encodedFields = urllib.urlencode(formData)
        req = urllib2.Request(url, encodedFields, headers)
        req_Open = urllib2.urlopen(req)
        req_Read = req_Open.read()
        soup = BeautifulSoup(req_Read)
        issues = soup.findAll('a', attrs={'class': 'detailLink'})
        if not issues:
            print("No issues detected..")
            sys.exit()

        else:
            issues_dict = {}
            for x in range(0, len(issues)):
                issues_dict["issue_{0}".format(x)] = self.html_cleaner(issues[x])
            return issues_dict


if __name__ == '__main__':
    n = Notify('422, 474')
    issues = n.issue_check()
    n.poster(issues)
