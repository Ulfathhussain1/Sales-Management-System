SQL_QUERIES = {
    # 1. Retrieve all customer sales
    "1. [Basic] Retrieve all records from customer_sales": {
        "super": """
            SELECT *
            FROM customer_sales
            ORDER BY sale_id
        """,
        "admin": """
            SELECT *
            FROM customer_sales
            WHERE branch_id = %s
            ORDER BY sale_id
        """
    },

    # 2. Retrieve all branches
    "2. [Basic] Retrieve all records from branches": {
        "super": """
            SELECT *
            FROM branches
            ORDER BY branch_id
        """,
        "admin": """
            SELECT *
            FROM branches
            WHERE branch_id = %s
            ORDER BY branch_id
        """
    },

    # 3. Retrieve all payment records
    "3. [Basic] Retrieve all records from payment_splits": {
        "super": """
            SELECT *
            FROM payment_splits
            ORDER BY payment_id
        """,
        "admin": """
            SELECT *
            FROM payment_splits
            WHERE sale_id IN (
            SELECT sale_id
            FROM customer_sales
            WHERE branch_id = %s)
            ORDER BY payment_id;
        """
    },

    # 4. Display sales with Open status
    "4. [Basic] Display all sales with status Open": {
        "super": """
            SELECT *
            FROM customer_sales
            WHERE status = 'Open'
            ORDER BY sale_id
        """,
        "admin": """
            SELECT *
            FROM customer_sales
            WHERE status = 'Open'
              AND branch_id = %s
            ORDER BY sale_id
        """
    },

    # 5. Calculate total gross sales
    "5. [Aggregation] Calculate total gross sales": {
        "super": """
            SELECT SUM(gross_sales)
            AS total_gross_sales
            FROM customer_sales
        """,
        "admin": """
            SELECT SUM(gross_sales)
            AS total_gross_sales
            FROM customer_sales
            WHERE branch_id = %s
        """
    },

    # 6. Calculate total received amount
    "6. [Aggregation] Calculate total received amount": {
        "super": """
            SELECT SUM(received_amount)
            AS total_received_amount
            FROM customer_sales
        """,
        "admin": """
            SELECT SUM(received_amount)
            AS total_received_amount
            FROM customer_sales
            WHERE branch_id = %s
        """
    },

    # 7. Calculate total pending amount
    "7. [Aggregation] Calculate total pending amount": {
        "super": """
            SELECT SUM(pending_amount)
            AS total_pending_amount
            FROM customer_sales
        """,
        "admin": """
            SELECT SUM(pending_amount)
            AS total_pending_amount
            FROM customer_sales
            WHERE branch_id = %s
        """
    },

    # 8. Count sales in each branch
    "8. [Aggregation] Count sales per branch": {
        "super": """
            SELECT branch_id,
                   COUNT(sale_id) AS total_sales
            FROM customer_sales
            WHERE customer_sales
            GROUP BY branch_id
            ORDER BY total_sales DESC
        """,
        "admin": """
            SELECT branch_id,
                   COUNT(sale_id) AS total_sales
            FROM customer_sales 
            WHERE branch_id = %s
            GROUP BY branch_id
        """
    },

    # 9. Retrieve sales with branch names
    "9. [Join-Based] Retrieve sales with branch name": {
        "super": """
            SELECT cs.sale_id,
                   cs.name AS customer_name,
                   cs.product_name,
                   cs.gross_sales,
                   b.branch_name
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            ORDER BY cs.sale_id
        """,
        "admin": """
            SELECT cs.sale_id,
                   cs.name AS customer_name,
                   cs.product_name,
                   cs.gross_sales,
                   b.branch_name
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            WHERE cs.branch_id = %s
            ORDER BY cs.sale_id
        """
    },

    # 10. Retrieve sales with total payment received
    "10. [Join-Based] Retrieve sales with total payment received": {
        "super": """
            SELECT cs.sale_id,
                   cs.name AS customer_name,
                   cs.product_name,
                   cs.gross_sales,
                   cs.received_amount,
                   cs.pending_amount,
                   COALESCE(SUM(ps.amount_paid), 0)
                       AS total_payment_received
            FROM customer_sales cs
            LEFT JOIN payment_splits ps
                ON cs.sale_id = ps.sale_id
            GROUP BY cs.sale_id, cs.name,
                     cs.product_name, cs.gross_sales,
                     cs.received_amount, cs.pending_amount
            ORDER BY cs.sale_id
        """,
        "admin": """
            SELECT cs.sale_id,
                   cs.name AS customer_name,
                   cs.product_name,
                   cs.gross_sales,
                   cs.received_amount,
                   cs.pending_amount,
                   COALESCE(SUM(ps.amount_paid), 0)
                       AS total_payment_received
            FROM customer_sales cs
            LEFT JOIN payment_splits ps
                ON cs.sale_id = ps.sale_id
            WHERE cs.branch_id = %s
            GROUP BY cs.sale_id, cs.name,
                     cs.product_name, cs.gross_sales,
                     cs.received_amount, cs.pending_amount
            ORDER BY cs.sale_id
        """
    },

    # 11. Branch-wise total gross sales
    "11. [Join-Based] Branch-wise total gross sales": {
        "super": """
            SELECT b.branch_name,
                   SUM(cs.gross_sales) AS total_gross_sales
            FROM branches b
            JOIN customer_sales cs
                ON b.branch_id = cs.branch_id
            GROUP BY b.branch_id, b.branch_name
            ORDER BY total_gross_sales DESC
        """,
        "admin": """
            SELECT b.branch_name,
                   SUM(cs.gross_sales) AS total_gross_sales
            FROM branches b
            JOIN customer_sales cs
                ON b.branch_id = cs.branch_id
            WHERE b.branch_id = %s
            GROUP BY b.branch_id, b.branch_name
            ORDER BY total_gross_sales DESC
        """
    },

    # 12. Display sales with payment methods
    "12. [Join-Based] Display sales with payment method": {
        "super": """
            SELECT cs.sale_id,
                   cs.name AS customer_name,
                   cs.product_name,
                   cs.gross_sales,
                   ps.payment_id,
                   ps.payment_date,
                   ps.amount_paid,
                   ps.payment_method
            FROM customer_sales cs
            JOIN payment_splits ps
                ON cs.sale_id = ps.sale_id
            ORDER BY cs.sale_id, ps.payment_date
        """,
        "admin": """
            SELECT cs.sale_id,
                   cs.name AS customer_name,
                   cs.product_name,
                   cs.gross_sales,
                   ps.payment_id,
                   ps.payment_date,
                   ps.amount_paid,
                   ps.payment_method
            FROM customer_sales cs
            JOIN payment_splits ps
                ON cs.sale_id = ps.sale_id
            WHERE cs.branch_id = %s
            ORDER BY cs.sale_id, ps.payment_date
        """
    },

    # 13. Find sales with pending amount above 5000
    "13. [Financial] Find pending amounts greater than 5000": {
        "super": """
            SELECT sale_id,
                   name AS customer_name,
                   product_name,
                   gross_sales,
                   received_amount,
                   pending_amount,
                   status
            FROM customer_sales
            WHERE pending_amount > 5000
            ORDER BY pending_amount DESC
        """,
        "admin": """
            SELECT sale_id,
                   name AS customer_name,
                   product_name,
                   gross_sales,
                   received_amount,
                   pending_amount,
                   status
            FROM customer_sales
            WHERE pending_amount > 5000
              AND branch_id = %s
            ORDER BY pending_amount DESC
        """
    },

    # 14. Retrieve top 3 highest gross sales
    "14. [Financial] Retrieve top 3 highest gross sales": {
        "super": """
            SELECT sale_id,
                   name AS customer_name,
                   product_name,
                   gross_sales,
                   received_amount,
                   pending_amount
            FROM customer_sales
            ORDER BY gross_sales DESC
            LIMIT 3
        """,
        "admin": """
            SELECT sale_id,
                   name AS customer_name,
                   product_name,
                   gross_sales,
                   received_amount,
                   pending_amount
            FROM customer_sales
            WHERE branch_id = %s
            ORDER BY gross_sales DESC
            LIMIT 3
        """
    },

    # 15. Find branch with highest total gross sales
    "15. [Financial] Find branch with highest total gross sales": {
        "super": """
            SELECT b.branch_name,
                   SUM(cs.gross_sales) AS total_gross_sales
            FROM branches b
            JOIN customer_sales cs
                ON b.branch_id = cs.branch_id
            GROUP BY b.branch_id, b.branch_name
            ORDER BY total_gross_sales DESC
            LIMIT 1
        """,
        "admin": """
            SELECT b.branch_name,
                   SUM(cs.gross_sales) AS total_gross_sales
            FROM branches b
            JOIN customer_sales cs
                ON b.branch_id = cs.branch_id
            WHERE b.branch_id = %s
            GROUP BY b.branch_id, b.branch_name
            ORDER BY total_gross_sales DESC
            LIMIT 1
        """
    }
}