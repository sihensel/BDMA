import pandas as pd

from cassandra.cluster import Cluster
from cassandra.query import dict_factory


CASSANDRA_HOST = "cassandra"
CASSANDRA_KEYSPACE = "pipeline"


def load_from_cassandra(t_name: str):
    """
    Load data from specified cassandra table

    params:
        t_name: name of the table to load

    returns:
        query result as a pandas DataFrame
    """
    cluster = Cluster([CASSANDRA_HOST])

    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory

    query = "SELECT * FROM %s;" % t_name
    rows = session.execute(query)

    return pd.DataFrame(rows)
