SQL_QUERIES = {

    # ==================== BASIC QUERIES (1–5) ====================

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
                WHERE branch_id = %s
            )
            ORDER BY payment_id
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

    # 5. Retrieve sales belonging to Chennai branch
    "5. [Basic] Retrieve sales belonging to Chennai branch": {
        "super": """
            SELECT cs.*
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            WHERE b.branch_name = 'Chennai'
            ORDER BY cs.sale_id
        """,
        "admin": """
            SELECT cs.*
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            WHERE b.branch_name = 'Chennai'
              AND cs.branch_id = %s
            ORDER BY cs.sale_id
        """
    },


    # ================= AGGREGATION QUERIES (6–10) =================

    # 6. Calculate total gross sales
    "6. [Aggregation] Calculate total gross sales": {
        "super": """
            SELECT SUM(gross_sales) AS total_gross_sales
            FROM customer_sales
        """,
        "admin": """
            SELECT SUM(gross_sales) AS total_gross_sales
            FROM customer_sales
            WHERE branch_id = %s
        """
    },

    # 7. Calculate total received amount
    "7. [Aggregation] Calculate total received amount": {
        "super": """
            SELECT SUM(received_amount) AS total_received_amount
            FROM customer_sales
        """,
        "admin": """
            SELECT SUM(received_amount) AS total_received_amount
            FROM customer_sales
            WHERE branch_id = %s
        """
    },

    # 8. Calculate total pending amount
    "8. [Aggregation] Calculate total pending amount": {
        "super": """
            SELECT SUM(pending_amount) AS total_pending_amount
            FROM customer_sales
        """,
        "admin": """
            SELECT SUM(pending_amount) AS total_pending_amount
            FROM customer_sales
            WHERE branch_id = %s
        """
    },

    # 9. Count sales in each branch
    "9. [Aggregation] Count sales per branch": {
        "super": """
            SELECT branch_id,
            COUNT(sale_id) AS total_sales
            FROM customer_sales
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

    # 10. Find average gross sales
    "10. [Aggregation] Find average gross sales": {
        "super": """
            SELECT b.branch_name,
               AVG(cs.gross_sales) AS average_gross_sales
        FROM branches b
        JOIN customer_sales cs
            ON b.branch_id = cs.branch_id
        GROUP BY b.branch_id, b.branch_name
        ORDER BY average_gross_sales DESC
        """,
        "admin": """
            SELECT AVG(gross_sales) AS average_gross_sales
            FROM customer_sales
            WHERE branch_id = %s
        """
    },


    # ================= JOIN-BASED QUERIES (11–15) =================

    # 11. Retrieve sales with branch name
    "11. [Join-Based] Retrieve sales with branch name": {
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

    # 12. Retrieve sales with total payment received
    "12. [Join-Based] Retrieve sales with total payment received": {
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

    # 13. Branch-wise total gross sales
    "13. [Join-Based] Branch-wise total gross sales": {
        "super": """
            SELECT b.branch_name,
                   SUM(cs.gross_sales) AS total_gross_sales
            FROM customer_sales cs
            RIGHT JOIN branches b
                ON cs.branch_id = b.branch_id
            GROUP BY b.branch_id, b.branch_name
            ORDER BY total_gross_sales DESC
        """,
        "admin": """
            SELECT b.branch_name,
                   SUM(cs.gross_sales) AS total_gross_sales
            FROM customer_sales cs
            RIGHT JOIN branches b
                ON cs.branch_id = b.branch_id
            WHERE b.branch_id = %s
            GROUP BY b.branch_id, b.branch_name
               ORDER BY total_gross_sales DESC
             """
    },

    # 14. Display sales with payment method
    "14. [Join-Based] Display sales with payment method": {
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

    # 15. Retrieve sales with branch admin name
    "15. [Join-Based] Retrieve sales with branch admin name": {
        "super": """
            SELECT cs.sale_id,
                   cs.name AS customer_name,
                   cs.product_name,
                   cs.gross_sales,
                   b.branch_name,
                   b.branch_admin_name
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
                   b.branch_name,
                   b.branch_admin_name
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            WHERE cs.branch_id = %s
            ORDER BY cs.sale_id
        """
    },


    # =============== FINANCIAL TRACKING QUERIES (16–20) ===============

    # 16. Find sales with pending amount greater than 5000
    "16. [Financial] Find pending amounts greater than 5000": {
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

    # 17. Retrieve top 3 highest gross sales
    "17. [Financial] Retrieve top 3 highest gross sales": {
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

    # 18. Find branch with highest total gross sales
    "18. [Financial] Find branch with highest total gross sales": {
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
    },

    # 19. Monthly sales summary
    "19. [Financial] Monthly sales summary": {
        "super": """
            SELECT YEAR(date) AS sales_year,
                   MONTH(date) AS sales_month,
                   COUNT(*) AS total_sales,
                   SUM(gross_sales) AS total_gross_sales
            FROM customer_sales
            GROUP BY YEAR(date), MONTH(date)
            ORDER BY sales_year, sales_month
        """,
        "admin": """
            SELECT YEAR(date) AS sales_year,
                   MONTH(date) AS sales_month,
                   COUNT(*) AS total_sales,
                   SUM(gross_sales) AS total_gross_sales
            FROM customer_sales
            WHERE branch_id = %s
            GROUP BY YEAR(date), MONTH(date)
            ORDER BY sales_year, sales_month
        """
    },

    # 20. Payment method-wise total collection
    "20. [Financial] Payment method-wise total collection": {
        "super": """
            SELECT payment_method,
                   SUM(amount_paid) AS total_collection
            FROM payment_splits
            GROUP BY payment_method
            ORDER BY total_collection DESC
        """,
        "admin": """
            SELECT ps.payment_method,
                   SUM(ps.amount_paid) AS total_collection
            FROM payment_splits ps
            JOIN customer_sales cs
                ON ps.sale_id = cs.sale_id
            WHERE cs.branch_id = %s
            GROUP BY ps.payment_method
            ORDER BY total_collection DESC
        """
    }
}
