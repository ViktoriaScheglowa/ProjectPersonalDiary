import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection


def check_tables():
    with connection.cursor() as cursor:
        # Для PostgreSQL
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name IN ('habits_habit', 'goal_goal', 'idea_myidea', 'moments_moment')
            ORDER BY table_name, ordinal_position;
        """)

        tables = {}
        for table, column, data_type in cursor.fetchall():
            if table not in tables:
                tables[table] = []
            tables[table].append((column, data_type))

        for table, columns in tables.items():
            print(f"\n{table}:")
            for column, data_type in columns:
                print(f"  {column} ({data_type})")


if __name__ == "__main__":
    check_tables()
