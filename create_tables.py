import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    print("Dropping existing tables...")
    for query in drop_table_queries:
        print("  ->", query.split()[-1])  # prints table name
        cur.execute(query)
        conn.commit()
    print("All existing tables dropped.")


def create_tables(cur, conn):
    print("Creating new tables...")
    for query in create_table_queries:
        print("  ->", query.split()[5])
        cur.execute(query)
        conn.commit()
    print("All new tables created.")


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()