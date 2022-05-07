from django.db import connection


def sqlserver_db(sql: str, query_parameter: tuple):
    data_list = []

    # 获取数据库连接
    conn = connection

    # parameterized query使用%s作为占位符
    sql = sql
    with conn.cursor() as cursor:
        cursor.execute(sql, query_parameter)
        # 获取查询数据的列名
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            data_list.append(dict(zip(columns, row)))
        conn.close()
    return data_list