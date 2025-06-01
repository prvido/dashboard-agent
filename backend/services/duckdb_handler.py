"""
DuckDB-specific handler service for managing DuckDB operations including connections,
table management, and data processing.
"""

import duckdb
from typing import Tuple, List, Dict, Any, Callable
import logging
import contextlib
from contextlib import contextmanager
import re


logger = logging.getLogger(__name__)

class DuckDBHandler:
    def __init__(self):
        self._active_connections = {}

        # Map file types to their corresponding DuckDB read functions
        self._file_type_readers: Dict[str, Callable[[str], str]] = {
            'csv': lambda path: f"read_csv_auto('{path}')",
            'json': lambda path: f"read_json_auto('{path}')",
            'parquet': lambda path: f"read_parquet('{path}')"
        }

    @staticmethod
    def _standardize_column_name(name: str) -> str:
        """Convert column name to lowercase and replace spaces with underscores."""
        # Convert to lowercase
        name = name.lower()
        # Replace spaces and special characters with underscores
        name = re.sub(r' ', '_', name)
        # Remove consecutive underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        return name

    @staticmethod
    def _convert_datetime_columns(df):
        """Convert datetime columns to ISO format strings."""
        for column in df.select_dtypes(include=['datetime64']).columns:
            df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df

    @contextmanager
    def get_connection(self, database_path: str, read_only: bool = True):
        conn = None
        try:
            # Close any existing connections to the same database
            for existing_conn, path in list(self._active_connections.items()):
                try:
                    if path == database_path:
                        existing_conn.close()
                        del self._active_connections[existing_conn]
                except Exception as e:
                    logger.warning(f"Error closing existing connection: {e}")

            # Create new connection
            conn = duckdb.connect(database=database_path, read_only=read_only)
            self._active_connections[conn] = database_path

            # Add logging when opening a connection
            logger.info(f"Opening DuckDB connection to {database_path} with read_only={read_only}")

            yield conn
        finally:
            if conn:
                try:
                    conn.close()
                    self._active_connections.pop(conn, None)

                    # Add logging when closing a connection
                    logger.info(f"Closing DuckDB connection to {database_path}")
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")

    def list_tables(self, database_path: str) -> List[str]:
        with self.get_connection(database_path) as conn:
            # Use DuckDB's information_schema.tables to list all tables
            tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
            return [table[0] for table in tables]

    def process_data(self, database_path: str, data_path: str, table_name: str, file_type: str) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        try:
            with self.get_connection(database_path, read_only=False) as conn:

                quoted_table_name = f'"{table_name}"'

                read_function = self._file_type_readers.get(file_type)
                if not read_function:
                    raise ValueError(f"Unsupported file type: {file_type}")

                # First read the data to get original column names
                temp_df = conn.execute(f"SELECT * FROM {read_function(data_path)}").fetchdf()
                original_columns = temp_df.columns.tolist()
                
                # Create standardized column names
                standardized_columns = [self._standardize_column_name(col) for col in original_columns]
                
                # Create the table with standardized column names
                select_clause = ', '.join([f'"{col}" as "{standardized_columns[i]}"' 
                                         for i, col in enumerate(original_columns)])
                
                conn.execute(f"CREATE OR REPLACE TABLE {quoted_table_name} AS "
                           f"SELECT {select_clause} FROM {read_function(data_path)}")

                columns_query = conn.execute(f"PRAGMA table_info({quoted_table_name})").fetchall()
                columns = [{"name": col[1], "type": col[2]} for col in columns_query]

                preview_df = conn.execute(f"SELECT * FROM {quoted_table_name} LIMIT 5").fetchdf()
                # Convert datetime columns to ISO format strings before converting to dict
                preview_df = self._convert_datetime_columns(preview_df)
                preview_data = preview_df.to_dict(orient='records')

                return columns, preview_data

        except Exception as e:
            logger.error(f"Error processing with DuckDB: {e}")
            raise


    def delete_table(self, database_path: str, table_name: str) -> None:
        try:
            # Log tables before deletion
            existing_tables = self.list_tables(database_path)
            logger.info(f"Tables in DuckDB file before deletion: {existing_tables}")

            with self.get_connection(database_path, read_only=False) as conn:
                quoted_table_name = f'"{table_name}"'

                # Check if table exists
                table_exists = conn.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'").fetchone()[0] > 0

                if table_exists:
                    conn.execute(f"DROP TABLE {quoted_table_name}")
                    # Log tables after deletion
                    updated_tables = self.list_tables(database_path)
                    logger.info(f"Tables in DuckDB file after deletion: {updated_tables}")
                else:
                    raise ValueError(f"Table {table_name} does not exist in the warehouse")

        except Exception as e:
            logger.error(f"Error deleting table from DuckDB: {e}")
            raise

    def execute_query(self, database_path: str, query: str) -> List[Dict[str, Any]]:
        try:
            with self.get_connection(database_path) as conn:
                result_df = conn.execute(query).fetchdf()

                # Converte automaticamente colunas de data para string ISO
                for col in result_df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
                    result_df[col] = result_df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

                # Converte o DataFrame em lista de dicionários
                return result_df.to_dict(orient='records')

        except Exception as e:
            logger.error(f"Error executing query on DuckDB: {str(e)}")
            raise Exception(str(e))
