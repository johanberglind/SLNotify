SL Notify
========

SL Notify is a Python application to query SL's ASP.NET servers for any disturbance in the buslines relevant to you.
I've added the ability to recieve push-notifications through Pushovers service if you are a member of said service. Just add
your token and user-id to the class-variables at the top. Also be sure to edit the buslines so they are relevant to you.

Requirements
------------

BeautifulSoup - For parsing the asp.net responses (BS4)                  
Pushwrapper - If you want to use Pushover (Included)


License
-------

See LICENSE.MD


Usage
-----

You can run SLNotify as a stand-alone script however you can also integrate it to your own application:

    from SLNotify import Notify
    n = Notify('410, 474')
    issues = n.issue_check()
    
This will return a maximum of three issues per query into the variable issues. Issues is a dictionary with a key and a value
which is the string returned from the ASP.NET Server. Optional:

    n.poster(issues)

    
    
Best regards!

// Johan
