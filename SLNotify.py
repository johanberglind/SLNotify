# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib
import urllib2
import re
import hashlib
from pushbullet import PushBullet


class Notify(object):
    def __init__(self, bus_lines):
        self.bus_lines = bus_lines

    def get_relevant_string(self, string):
        """ get_relevant_string() parses the string and returns the
        string between span-tags, it also removes a br tag which is
        left in from the bs4 parsing.

        Returns:
            String relevant to user.
        """
        return re.search("<span>(.*)</span>", unicode(string)).group(1).\
            replace('<br/>', '')

    def query_asp_pre(self):
        """ Finds the eventvalidate and viewstate strings from the ASP page.
        Since these are not static, it's required to fetch these
        before request.

        Returns:
            viewstate - parameter required for request
            eventvalidate - parameter required for request

        """
        __url__ = 'http://storningsinformation.sl.se/sv/?State=Search'
        request = urllib2.Request(__url__)
        request_open = urllib2.urlopen(request)
        request_read = request_open.read()
        soup = BeautifulSoup(request_read)
        event_validate_raw = soup.findAll('input',
                                          attrs={'id': '__EVENTVALIDATION'})
        viewstate_raw = soup.findAll('input', attrs={'id': '__VIEWSTATE'})
        viewstate_re = re.search('value="(.*)"', str(viewstate_raw))
        event_validate_re = re.search('value="(.*)"', str(event_validate_raw))
        viewstate = viewstate_re.group(1)
        event_validate = event_validate_re.group(1)
        return viewstate, event_validate

    def hash_string(self, string):
        """ hash_string hashes the string using md5 and returns
        the digest of this. This is because it's easier to store and
        compare the hashes instead of complete strings.

        Returns:
            Hashed string.
        """
        hashedString = hashlib.md5(string).hexdigest()
        return hashedString

    def poster(self, issues):
        """ poster() goes through all the issues and
        checks if they are already in the db. If not,
        use the pushbullet_post()-function to sent these
        to the user.
        """

        for issue in issues:
            if not (self.hash_string(issue) in open('posts.db', 'a+').read()):
                self.pushbullet_post(issue)
                print("Disturbance found and sent.")
                open('posts.db', 'a+').write(self.hash_string(issue) + '\n')

    def pushbullet_post(self, issue):
        """ Posts to Pushbullet API.
        For future reference, the push_note() function returns two
        values. One bool that specificies whether the push was a success
        or not, and a dict with additional info.
        """

        pb = PushBullet('YOUR-API-KEY')
        worked, push = pb.push_note(u"Förseningar", issue)
        if not worked:
            print(push)

    def issue_check(self):
        """ issue_check() polls the ASP.net server and checks for
        any potential issues relating to the bus lines specified.
        If it find any disturbances it will return these in a list.

        Returns: issues - str lst containing issues
        """

        viewstate, event_validate = self.query_asp_pre()

        headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22\ (KHTML, like Gecko)\ Chrome/25.0.1364.97 Safari/537.22',
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
            ('ctl00$FullRegion$SearchDeviation1$tbLineNumber',
                '{}'.format(self.bus_lines)),
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
        return [self.get_relevant_string(issue).encode('utf-8') for
                issue in issues]

if __name__ == '__main__':
    n = Notify('471')
    issues = n.issue_check()
    n.poster(issues)
