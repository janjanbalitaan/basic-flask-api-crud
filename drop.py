#!python

from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint,
)

def drop(db_url):
    engine = create_engine(db_url)

    # if targeting a specific schema name, set it here
    my_schema = None

    # the transaction only applies if the DB supports
    with engine.begin() as conn:

        inspector = inspect(conn)

        for tname, fkcs in reversed(
                inspector.get_sorted_table_and_fkc_names(schema=my_schema)):
            if tname:
                conn.execute(DropTable(
                    Table(tname, MetaData(), schema=my_schema)
                ))
            elif fkcs:
                if not engine.dialect.supports_alter:
                    continue
                for tname, fkc in fkcs:
                    fk_constraint = ForeignKeyConstraint((), (), name=fkc)
                    Table(tname, MetaData(), fk_constraint)
                    conn.execute(DropConstraint(fk_constraint))