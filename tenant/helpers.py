from django.db import connection

def reset_sequences(target_schema):
    sql_query = f"""
        SELECT 'SELECT SETVAL(' ||
            quote_literal(quote_ident(PGT.schemaname) || '.' || quote_ident(S.relname)) ||
            ', COALESCE(MAX(' ||quote_ident(C.attname)|| '), 1) ) FROM ' ||
            quote_ident(PGT.schemaname)|| '.'||quote_ident(T.relname)|| ';'
        FROM pg_class AS S,
            pg_depend AS D,
            pg_class AS T,
            pg_attribute AS C,
            pg_tables AS PGT
        WHERE S.relkind = 'S'
            AND S.oid = D.objid
            AND D.refobjid = T.oid
            AND D.refobjid = C.attrelid
            AND D.refobjsubid = C.attnum
            AND T.relname = PGT.tablename
            AND quote_ident(PGT.schemaname) = '{target_schema}'
        ORDER BY S.relname;
        """

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        cursor.fetchall()
