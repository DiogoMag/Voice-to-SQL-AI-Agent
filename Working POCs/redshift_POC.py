import configparser
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import redshift-connector, fallback to psycopg2
try:
    import redshift_connector
    USE_REDSHIFT_CONNECTOR = True
except ImportError:
    try:
        import psycopg2
        USE_REDSHIFT_CONNECTOR = False
    except ImportError:
        print("ERROR: Neither 'redshift-connector' nor 'psycopg2-binary' is installed.")
        print("Install one of them using:")
        print("  pip install redshift-connector")
        print("  OR")
        print("  pip install psycopg2-binary")
        sys.exit(1)

# Load config values from ../config/config.ini
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.ini')
config.read(config_path)

# Get Redshift connection parameters
redshift_host = config['redshift']['host']
redshift_port = int(config['redshift']['port'])
redshift_user = config['redshift']['user']
redshift_password = config['redshift']['password']
redshift_database = config['redshift']['database']


def connect_to_redshift():
    """Establish connection to Redshift RA3 cluster."""
    try:
        if USE_REDSHIFT_CONNECTOR:
            conn = redshift_connector.connect(
                host=redshift_host,
                port=redshift_port,
                database=redshift_database,
                user=redshift_user,
                password=redshift_password,
                ssl=True
            )
            print(f"✓ Connected to Redshift using redshift-connector")
        else:
            conn = psycopg2.connect(
                host=redshift_host,
                port=redshift_port,
                database=redshift_database,
                user=redshift_user,
                password=redshift_password,
                sslmode='require'
            )
            print(f"✓ Connected to Redshift using psycopg2")
        
        return conn
    except Exception as e:
        print(f"✗ Failed to connect to Redshift: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your cluster endpoint, port, and credentials in config/config.ini")
        print("2. Ensure your IP is whitelisted in the Redshift security group")
        print("3. Check that the cluster is available and not paused")
        sys.exit(1)


def query_todos(conn, user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
    """Query the todos table.
    
    Args:
        conn: Database connection object
        user_id: Optional filter by user_id
        status: Optional filter by status (e.g., 'open', 'completed')
    
    Returns:
        List of todo records as dictionaries
    """
    cursor = conn.cursor()
    
    query = "SELECT id, user_id, task, due_date, status, created_at FROM todos"
    conditions = []
    params = []
    
    if user_id:
        conditions.append("user_id = %s")
        params.append(user_id)
    
    if status:
        conditions.append("status = %s")
        params.append(status)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC"
    
    try:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        cursor.close()
        return results
    except Exception as e:
        cursor.close()
        print(f"✗ Error querying todos: {e}")
        return []


def query_shopping_list(conn, user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
    """Query the shopping_list table.
    
    Args:
        conn: Database connection object
        user_id: Optional filter by user_id
        status: Optional filter by status (e.g., 'pending', 'completed')
    
    Returns:
        List of shopping list items as dictionaries
    """
    cursor = conn.cursor()
    
    query = "SELECT id, user_id, item_name, quantity, added_at, status FROM shopping_list"
    conditions = []
    params = []
    
    if user_id:
        conditions.append("user_id = %s")
        params.append(user_id)
    
    if status:
        conditions.append("status = %s")
        params.append(status)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY added_at DESC"
    
    try:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        cursor.close()
        return results
    except Exception as e:
        cursor.close()
        print(f"✗ Error querying shopping_list: {e}")
        return []


def format_timestamp(ts):
    """Format timestamp for display."""
    if ts is None:
        return "N/A"
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    return str(ts)


def display_todos(todos: List[Dict]):
    """Display todos in a readable format."""
    if not todos:
        print("\n📝 Todos: No records found")
        return
    
    print(f"\n📝 Todos ({len(todos)} records):")
    print("=" * 100)
    print(f"{'ID':<5} {'User ID':<15} {'Task':<40} {'Due Date':<20} {'Status':<12} {'Created':<20}")
    print("-" * 100)
    
    for todo in todos:
        print(f"{todo['id']:<5} {todo['user_id']:<15} {todo['task'][:38]:<40} "
              f"{format_timestamp(todo['due_date']):<20} {todo['status']:<12} "
              f"{format_timestamp(todo['created_at']):<20}")


def display_shopping_list(items: List[Dict]):
    """Display shopping list items in a readable format."""
    if not items:
        print("\n🛒 Shopping List: No records found")
        return
    
    print(f"\n🛒 Shopping List ({len(items)} records):")
    print("=" * 100)
    print(f"{'ID':<5} {'User ID':<15} {'Item Name':<30} {'Quantity':<15} {'Status':<12} {'Added':<20}")
    print("-" * 100)
    
    for item in items:
        print(f"{item['id']:<5} {item['user_id']:<15} {item['item_name'][:28]:<30} "
              f"{item['quantity'] or 'N/A':<15} {item['status']:<12} "
              f"{format_timestamp(item['added_at']):<20}")


def main():
    """Main function to run the POC."""
    print("=" * 100)
    print("Redshift RA3 POC - Querying Todos and Shopping Lists")
    print("=" * 100)
    
    # Connect to Redshift
    conn = connect_to_redshift()
    
    try:
        # Query todos
        todos = query_todos(conn)
        display_todos(todos)
        
        # Query shopping list
        shopping_items = query_shopping_list(conn)
        display_shopping_list(shopping_items)
        
        print("\n" + "=" * 100)
        print("✓ POC completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error during POC execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connection
        conn.close()
        print("✓ Connection closed")


if __name__ == "__main__":
    main()
