import requests
import os
import os.path
from requests.adapters import HTTPAdapter

class monitor(object):
    """ You are responsible for monitoring a web property for changes, the first proof of concept is a simple page monitor.  The requirements are:
1) Log to a file the changed/unchanged state of the URL http://www.oracle.com/index.html.
2) Retry a configurable number of times in case of connection oriented errors.
3) Handle URL content change or unavailability as a program error with a non-zero exit.
4) Any other design decisions are up to the implementer.  Bonus for solid design and extensibility.
    """

    def __init__(self, monitor_host, monitor_page, monitor_user, monitor_password, monitor_retries, monitor_timeout):
        """ Class initialization method
        :param monitor_host: monitor host or IP address of server
        :param monitor_uri: monitor URI page /index.html
        :param monitor_user: user name (optional)
        :param monitor_password: password (optional)
        :param monitor_retries: number of retries
        :param monitor_timeout: connection timeout for each attempt
        #:param monitor_verify_ssl : SSL Certificate checks on https, turn off = False
        """
        self.monitor_host = monitor_host
        self.monitor_uri = monitor_page
        self.monitor_usernmae = monitor_user
        self.monitor_password = monitor_password
        self.monitor_retries = monitor_retries
        self.monitor_timeout = monitor_timeout
        #self.monitor_verify_ssl = monitor_verify_ssl

    def get_http_content(self):
        url = 'http://' + self.monitor_host + '/' + self.monitor_uri
        try:
            r = requests.Session()
            r.mount(url, HTTPAdapter(max_retries=self.monitor_retries))
            r_html = r.get(url,timeout=self.monitor_timeout)
            if len(r_html.text) > 0:
                #print r_html.status_code
                #print r_html.text
                return [ r_html.status_code, r_html.text ]
            else:
                return [ r_html.status_code,'']

        except Exception:
            return [ -1,'unreachable']

def getcontents(file):
    # This checks if the file exists and if it does returns the contents of the file, making it json so I can store status and content of page

    #STATUS_FILE='./monitor-json.out'
    STATUS_FILE='./' + file 
    #HTMLOUT_FILE='./monitor-html.out'

    if os.path.isfile(STATUS_FILE) and os.access(STATUS_FILE, os.R_OK):
        #print "File exists and is readable"
        #newstatus = '{ "monitor_status": "' + status + '"}'
        f = open (STATUS_FILE, 'r')
        return f.read()
    else:
        return ''

def updatefile(file,content):
    STATUS_FILE='./' + file
    #HTMLOUT_FILE='./monitor-html.out'

    #if os.access(STATUS_FILE, os.W_OK):
    #    print "File exists and is writable"
        #newstatus = '{ "monitor_status": "' + status + '"}' # json out next
    with open (STATUS_FILE, 'w') as f: f.write (content)
    #else:
    #    print "ERROR:unable to update file " + file

def main():
    # Set variables and log files
    host = 'oracle.com'
    page = 'index.html'
    username = ''
    password = ''
    debug = 1
    retries = 10 # configure the number of retries if a connection attempt fails
    timeout = 1.0 # number of seconds to wait for a connection attempt to fail
    connect = monitor(host, page, username, password, retries,timeout)
    changed = 0 # used to determine if page has changed
    status = 0 # used to get back status from web site call
    WEBSITE_UP = 0 # This is the main state to tell if the site passes the test. 1 is UP, 0 is down
    filestatus='monitor-status.out' # logs the current web site http status code
    filehtml='monitor-html.out' # returns the content of the web site's html
    statusfile='monitor-state.out' # Logs if the web site is up or down
    content = ''
    try:
        currentstatus = getcontents(filestatus)
        #print currentstatus
        currentcontent = getcontents(filehtml)
        if currentstatus:
            print "Old status is " + currentstatus
        else:
            print "Old status is unknown"

        # make the call to web site
        status,content = connect.get_http_content()

        # Check the status of old and new
        # print currentstatus
        if str(status) == str(currentstatus):
            if debug:
                print "HTML status hasn't changed " + str(status)
        else:
            if debug:
                print "HTML status has changed from " + str(currentstatus) + ' to ' + str(status)
            changed=1
        
        # 200 means the site is up. 
        if status == 200:
            WEBSITE_UP=1 # Web site is up, horray! lets check the contents of the html
            if str(currentcontent) == str(content):
                if debug:
                    print "HTML content hasn't changed" 
            else:
                if debug:
                    print "ERROR: HTML content has changed"
                changed=1
        else: # The site is down
            print "ERROR: Unable to connect to the web server(http://" + host + "/" + page + ") or the URL is incorrect"

        if changed:
            if debug:
                print "Changed state, updating"
            updatefile(filestatus,str(status))
            updatefile(filehtml,content)

        if WEBSITE_UP:
            if changed: 
                print "Web site (http://" + host + "/" + page + ") is UP but content changed" 
                updatefile(statusfile,"UP but changed")
            else:
                updatefile(statusfile,"UP")

        else:
            print "ERROR: Web site (http://" + host + "/" + page + ") is DOWN" 
            updatefile(statusfile,"DOWN")

    except Exception as e:
        print e

if __name__ == "__main__":
    main()
