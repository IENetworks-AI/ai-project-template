import cx_Oracle
import pandas as pd
import os

def extract_from_oracle():
    dsn = cx_Oracle.makedsn(
        os.getenv("ORACLE_HOST"),
        os.getenv("ORACLE_PORT", "1521"),
        service_name=os.getenv("ORACLE_SERVICE_NAME")
    )

    conn = cx_Oracle.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=dsn
    )

    query = "SELECT * FROM procurement_records"  # Customize this query
    df = pd.read_sql(query, con=conn)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/procurement_data.csv", index=False)
    conn.close()

if __name__ == "__main__":
    extract_from_oracle()
