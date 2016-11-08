from globals import *
import psycopg2
import pandas as pd
import numpy as np
import talib as ta
import file_iterator as fi


table_name = 'forexanalysis2'


def create_table(table):
    sql_connection = psycopg2.connect(host=host, port=port, user=user, database=database)
    cursor = sql_connection.cursor()
    cursor.execute("""CREATE TABLE public.""" + table + """ (
        id INTEGER PRIMARY KEY NOT NULL,
        symbol VARCHAR(10),
        timestamp TIMESTAMP,
        date DATE,
        time TIME,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        import TIMESTAMP,
        ema NUMERIC,
        rsi NUMERIC,
        slow_rsi NUMERIC,
        roc NUMERIC,
        slow_roc NUMERIC,
        mama NUMERIC,
        fama NUMERIC,
        ht_trend NUMERIC );""")
    sql_connection.commit()
    sql_connection.close()
    print("Created new table: " + table)


def get_data():
    print("Getting raw data for foreximport")
    sql_connection = psycopg2.connect(host=host, port=port, user=user, database=database)
    sql = "SELECT * FROM foreximport WHERE symbol = 'eurusd';"
    data_frame = pd.read_sql(sql, sql_connection)

    print("Getting technicals")
    data_frame['ema'] = ta.EMA(np.array(data_frame.close), timeperiod=100)
    data_frame['rsi'] = ta.RSI(np.array(data_frame.close), timeperiod=10)
    data_frame['slow_rsi'] = ta.EMA(np.array(data_frame.rsi), timeperiod=10)
    data_frame['roc'] = ta.ROC(np.array(data_frame.close), timeperiod=10)
    data_frame['slow_roc'] = ta.EMA(np.array(data_frame.roc), timeperiod=10)
    data_frame['mama'], data_frame['fama'] = ta.MAMA(np.array(data_frame.close), fastlimit=0.5, slowlimit=0.05)
    data_frame['ht_trend'] = ta.HT_TRENDLINE(np.array(data_frame.close))

    return data_frame


def insert_db(df, table):
    print("Inserting to: " + table)
    sql_connection = psycopg2.connect(host=host, port=port, user=user, database=database)
    cursor = sql_connection.cursor()

    data_dict = df.to_dict(orient='index')

    series = []

    for row in data_dict.values():
        # cursor.execute(
        #     """INSERT INTO """ + table + """ VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        #     , %s, %s, %s, %s, %s);"""
        #     , (row['id']
        #     , row['symbol']
        #     , row['timestamp']
        #     , row['date']
        #     , row['time']
        #     , row['open']
        #     , row['high']
        #     , row['low']
        #     , row['close']
        #     , row['import']
        #     , row['ema'] if "nan" not in str(row['ema']) else 0
        #     , row['rsi'] if "nan" not in str(row['rsi']) else 0
        #     , row['slow_rsi'] if "nan" not in str(row['slow_rsi']) else 0
        #     , row['roc'] if "nan" not in str(row['roc']) else 0
        #     , row['slow_roc'] if "nan" not in str(row['slow_roc']) else 0
        #     , row['mama'] if "nan" not in str(row['mama']) else 0
        #     , row['fama'] if "nan" not in str(row['fama']) else 0
        #     , row['ht_trend'] if "nan" not in str(row['ht_trend']) else 0))

        series.append(((row['id']
           , row['symbol']
           , row['timestamp']
           , row['date']
           , row['time']
           , row['open']
           , row['high']
           , row['low']
           , row['close']
           , row['import']
           , row['ema'] if "nan" not in str(row['ema']) else 0
           , row['rsi'] if "nan" not in str(row['rsi']) else 0
           , row['slow_rsi'] if "nan" not in str(row['slow_rsi']) else 0
           , row['roc'] if "nan" not in str(row['roc']) else 0
           , row['slow_roc'] if "nan" not in str(row['slow_roc']) else 0
           , row['mama'] if "nan" not in str(row['mama']) else 0
           , row['fama'] if "nan" not in str(row['fama']) else 0
           , row['ht_trend'] if "nan" not in str(row['ht_trend']) else 0)))

    series.sort()
    # print(series[0])
    # records_list_template = ','.join(['%s'] * len(series))
    # insert_query = 'INSERT INTO ' + table + ' VALUES {0}'.format(records_list_template)
    # cursor.execute(insert_query, series)
    f = fi.IteratorFile(("{}\t{}".format(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]
                                         , x[8], x[9], x[10], x[11], x[12], x[13], x[14]
                                         , x[15], x[16], x[17]) for x in series))
    cursor.copy_from(f, table, columns=('id', 'symbol', 'timestamp', 'date', 'time', 'open'
                                        , 'high', 'low', 'close', 'import', 'ema', 'rsi'
                                        ,'slow_rsi', 'roc', 'slow_roc', 'mama', 'fama', 'ht_trend'))
    sql_connection.commit()
    cursor.close()
    sql_connection.close()
    print("Finished inserting to: " + table)


def main():
    # create_table(table_name)
    df = get_data()
    insert_db(df, table_name)

main()
