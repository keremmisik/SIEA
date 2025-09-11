from sqlalchemy import text
from .database import engine

def add_multiple_products_support():
    """Add multiple products support columns to invoices table"""
    
    # Add new columns
    add_columns_sql = """
    ALTER TABLE invoices 
    ADD COLUMN has_multiple_products BOOLEAN DEFAULT FALSE,
    ADD COLUMN products_data JSON;
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(add_columns_sql))
            conn.commit()
            print("✅ Multiple products support columns added successfully")
    except Exception as e:
        print(f"❌ Error adding columns: {e}")

def rollback_multiple_products_support():
    """Remove multiple products support columns from invoices table"""
    
    remove_columns_sql = """
    ALTER TABLE invoices 
    DROP COLUMN has_multiple_products,
    DROP COLUMN products_data;
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(remove_columns_sql))
            conn.commit()
            print("✅ Multiple products support columns removed successfully")
    except Exception as e:
        print(f"❌ Error removing columns: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_multiple_products_support()
    else:
        add_multiple_products_support()