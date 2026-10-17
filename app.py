import streamlit as st
from db_config import get_connection
from queries import SQL_QUERIES
import pandas as pd

st.set_page_config(page_title="Sales Intelligence Hub", page_icon="📊", layout="wide")

try:
    conn = get_connection()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

for key, default in [("logged_in", False), ("username", ""), ("role", ""), ("branch_id", None), ("branch_name", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

def get_branches():
    return pd.read_sql("SELECT branch_id, branch_name FROM branches ORDER BY branch_id", conn)

def logout():
    for key, value in [("logged_in", False), ("username", ""), ("role", ""), ("branch_id", None), ("branch_name", "")]:
        st.session_state[key] = value

if not st.session_state["logged_in"]:
    st.title("📊 Sales Intelligence Hub")
    st.subheader("Login")
    with st.form("login_form"):
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login", type="primary")
    if login_button:
        if not login_username.strip() or not login_password.strip():
            st.error("Please enter both username and password.")
        else:
            q = "SELECT user_id, username, role, branch_id FROM users WHERE username = %s AND password = %s"
            cur = conn.cursor(dictionary=True)
            cur.execute(q, (login_username.strip(), login_password))
            user = cur.fetchone()
            cur.close()
            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = user["username"]
                st.session_state["role"] = user["role"]
                st.session_state["branch_id"] = user["branch_id"]
                if user["branch_id"] is not None:
                    b = pd.read_sql("SELECT branch_name FROM branches WHERE branch_id = %s", conn, params=(user["branch_id"],))
                    st.session_state["branch_name"] = b.iloc[0]["branch_name"] if not b.empty else ""
                else:
                    st.session_state["branch_name"] = "All Branches"
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid username or password.")
else:
    username = st.session_state["username"]
    role = st.session_state["role"]
    user_branch_id = st.session_state["branch_id"]
    user_branch_name = st.session_state["branch_name"]

    st.sidebar.title("📊 Sales Intelligence Hub")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation Menu")
    menu = st.sidebar.radio("Select Category", ["📊 Dashboard & Reports", "📝 Data Entry Workspace", "🧮 Advanced SQL Engine"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("User Information")
    st.sidebar.write(f"**User:** {username}")
    st.sidebar.write(f"**Role:** {role}")
    st.sidebar.write(f"**Branch:** {user_branch_name if role == 'Admin' else 'All Branches'}")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        logout()
        st.rerun()

    st.title("📊 Sales Intelligence Hub")
    st.caption(f"Welcome, {username} | {role}")

    if menu == "📊 Dashboard & Reports":
        st.header("📊 Dashboard & Reports")
        st.info("Super Admin access: You can view sales data from all branches." if role == "Super Admin" else f"Admin access: You can view sales data only for the {user_branch_name} branch.")
        st.subheader("🔎 Sales Filters")
        branches_df = get_branches()
        if role == "Super Admin":
            branch_options = ["All Branches"] + branches_df["branch_name"].tolist()
            selected_branch = st.selectbox("Branch", branch_options, key="dashboard_branch_filter")
        else:
            selected_branch = user_branch_name
            st.text_input("Branch", value=user_branch_name, disabled=True, key="dashboard_admin_branch")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            selected_product = st.selectbox("Product Name", ["All Products", "DS", "DA", "BA", "FSD", "AI", "BI", "ML", "SQL"], key="dashboard_product_filter")
        with c2:
            start_date = st.date_input("Start Date", value=None, key="dashboard_start_date")
        with c3:
            end_date = st.date_input("End Date", value=None, key="dashboard_end_date")
        with c4:
            selected_status = st.selectbox("Status", ["All Status", "Open", "Close"], key="dashboard_status_filter")

        conditions, params = [], []
        if role == "Admin":
            conditions.append("cs.branch_id = %s"); params.append(user_branch_id)
        elif selected_branch != "All Branches":
            bid = branches_df.loc[branches_df["branch_name"] == selected_branch, "branch_id"].iloc[0]
            conditions.append("cs.branch_id = %s"); params.append(int(bid))
        if selected_product != "All Products":
            conditions.append("cs.product_name = %s"); params.append(selected_product)
        if start_date is not None:
            conditions.append("cs.date >= %s"); params.append(start_date)
        if end_date is not None:
            conditions.append("cs.date <= %s"); params.append(end_date)
        if selected_status != "All Status":
            conditions.append("cs.status = %s"); params.append(selected_status)
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        df = pd.read_sql(f"""
            SELECT cs.sale_id, cs.branch_id, b.branch_name, cs.date, cs.name, cs.mobile_number,
                   cs.product_name, cs.gross_sales, cs.received_amount, cs.pending_amount, cs.status
            FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id
            {where_clause} ORDER BY cs.sale_id
        """, conn, params=tuple(params))

        st.subheader("📈 Sales Summary")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Sales", len(df))
        with m2: st.metric("Total Gross Sales", f"₹{df['gross_sales'].sum() if not df.empty else 0:,.2f}")
        with m3: st.metric("Total Received", f"₹{df['received_amount'].sum() if not df.empty else 0:,.2f}")
        with m4: st.metric("Total Pending", f"₹{df['pending_amount'].sum() if not df.empty else 0:,.2f}")
        st.markdown("---")
        st.subheader("👥 Customer Sales")
        if df.empty: st.info("No sales records found for the selected filters.")
        else: st.dataframe(df.drop(columns=["branch_id"], errors="ignore"), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("💳 Payment History")
        ph_conditions, ph_params = [], []
        if role == "Admin": ph_conditions.append("cs.branch_id = %s"); ph_params.append(user_branch_id)
        elif selected_branch != "All Branches":
            bid = branches_df.loc[branches_df["branch_name"] == selected_branch, "branch_id"].iloc[0]
            ph_conditions.append("cs.branch_id = %s"); ph_params.append(int(bid))
        ph_where = "WHERE " + " AND ".join(ph_conditions) if ph_conditions else ""
        ph = pd.read_sql(f"""
            SELECT ps.payment_id, ps.sale_id, cs.name AS customer_name, b.branch_name,
                   ps.payment_date, ps.amount_paid, ps.payment_method
            FROM payment_splits ps JOIN customer_sales cs ON ps.sale_id = cs.sale_id
            JOIN branches b ON cs.branch_id = b.branch_id {ph_where} ORDER BY ps.payment_id
        """, conn, params=tuple(ph_params))
        if ph.empty: st.info("No payment records found.")
        else: st.dataframe(ph, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🏢 Branch-wise Sales Summary")
        if role == "Super Admin":
            bs = pd.read_sql("""
                SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales,
                       COALESCE(SUM(cs.gross_sales),0) AS total_gross_sales,
                       COALESCE(SUM(cs.received_amount),0) AS total_received,
                       COALESCE(SUM(cs.pending_amount),0) AS total_pending
                FROM branches b LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
                GROUP BY b.branch_id, b.branch_name ORDER BY total_gross_sales DESC
            """, conn)
        else:
            bs = pd.read_sql("""
                SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales,
                       COALESCE(SUM(cs.gross_sales),0) AS total_gross_sales,
                       COALESCE(SUM(cs.received_amount),0) AS total_received,
                       COALESCE(SUM(cs.pending_amount),0) AS total_pending
                FROM branches b LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
                WHERE b.branch_id = %s GROUP BY b.branch_id, b.branch_name
            """, conn, params=(user_branch_id,))
        st.dataframe(bs, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("💰 Financial Summary")
        fin = pd.read_sql(f"""
            SELECT COALESCE(SUM(cs.gross_sales),0) AS total_gross_sales,
                   COALESCE(SUM(cs.received_amount),0) AS total_received,
                   COALESCE(SUM(cs.pending_amount),0) AS total_pending,
                   COUNT(cs.sale_id) AS total_sales
            FROM customer_sales cs {where_clause}
        """, conn, params=tuple(params))
        if not fin.empty:
            r = fin.iloc[0]; f1, f2, f3, f4 = st.columns(4)
            with f1: st.metric("Gross Sales", f"₹{r['total_gross_sales']:,.2f}")
            with f2: st.metric("Received Amount", f"₹{r['total_received']:,.2f}")
            with f3: st.metric("Pending Amount", f"₹{r['total_pending']:,.2f}")
            with f4: st.metric("Number of Sales", int(r['total_sales']))

    elif menu == "📝 Data Entry Workspace":
        st.header("📝 Data Entry Workspace")
        st.info("Super Admin can create sales and payment entries for all branches." if role == "Super Admin" else f"Admin can create entries only for the {user_branch_name} branch.")
        branches_df = get_branches()

        st.subheader("➕ Add New Sale")
        with st.form("add_sale_form"):
            c1, c2 = st.columns(2)
            with c1:
                sale_date = st.date_input("Date")
                customer_name = st.text_input("Customer Name")
                mobile_number = st.text_input("Mobile Number")
            with c2:
                if role == "Super Admin":
                    entry_branch = st.selectbox("Branch", branches_df["branch_name"].tolist(), key="new_sale_branch")
                else:
                    entry_branch = user_branch_name
                    st.text_input("Branch", value=user_branch_name, disabled=True, key="new_sale_admin_branch")
                product_name = st.selectbox("Product Name", ["DS", "DA", "BA", "FSD", "AI", "BI", "ML", "SQL"])
                gross_sales = st.number_input("Gross Sales", min_value=0.0, step=1000.0, format="%.2f")
            add_sale_button = st.form_submit_button("Add New Sale", type="primary")
        if add_sale_button:
            if not customer_name.strip(): st.error("Customer name cannot be empty.")
            elif not mobile_number.strip(): st.error("Mobile number cannot be empty.")
            elif gross_sales <= 0: st.error("Gross sales must be greater than 0.")
            else:
                branch_id = user_branch_id if role == "Admin" else int(branches_df.loc[branches_df["branch_name"] == entry_branch, "branch_id"].iloc[0])
                cur = conn.cursor()
                try:
                    cur.execute("""
                        INSERT INTO customer_sales (branch_id, date, name, mobile_number, product_name, gross_sales)
                        VALUES (%s,%s,%s,%s,%s,%s)
                    """, (branch_id, sale_date, customer_name.strip(), mobile_number.strip(), product_name, gross_sales))
                    conn.commit(); cur.close(); st.success("New sales entry added successfully."); st.rerun()
                except Exception as e:
                    cur.close(); st.error(f"Error while adding sale: {e}")

        st.markdown("---")
        st.subheader("💳 Add Payment Entry")
        if role == "Super Admin":
            ps = pd.read_sql("""
                SELECT cs.sale_id, cs.name, b.branch_name, cs.gross_sales, cs.received_amount, cs.pending_amount
                FROM customer_sales cs JOIN branches b ON cs.branch_id=b.branch_id
                WHERE cs.pending_amount > 0 ORDER BY cs.sale_id
            """, conn)
        else:
            ps = pd.read_sql("""
                SELECT cs.sale_id, cs.name, b.branch_name, cs.gross_sales, cs.received_amount, cs.pending_amount
                FROM customer_sales cs JOIN branches b ON cs.branch_id=b.branch_id
                WHERE cs.branch_id=%s AND cs.pending_amount > 0 ORDER BY cs.sale_id
            """, conn, params=(user_branch_id,))
        if ps.empty:
            st.info("There are no sales with pending payments.")
        else:
            with st.form("add_payment_form"):
                selected_sale_id = st.selectbox("Select Sale", ps["sale_id"].tolist())
                selected_sale = ps[ps["sale_id"] == selected_sale_id].iloc[0]
                st.write(f"**Customer:** {selected_sale['name']}")
                st.write(f"**Branch:** {selected_sale['branch_name']}")
                st.write(f"**Gross Sales:** ₹{selected_sale['gross_sales']:,.2f}")
                st.write(f"**Received Amount:** ₹{selected_sale['received_amount']:,.2f}")
                st.write(f"**Pending Amount:** ₹{selected_sale['pending_amount']:,.2f}")
                payment_date = st.date_input("Payment Date")
                amount_paid = st.number_input("Amount Paid", min_value=0.0, step=500.0, format="%.2f")
                payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])
                add_payment_button = st.form_submit_button("Add Payment", type="primary")
            if add_payment_button:
                pending = float(selected_sale["pending_amount"])
                if amount_paid <= 0: st.error("Payment amount must be greater than 0.")
                elif amount_paid > pending: st.error(f"Payment cannot be greater than the pending amount of ₹{pending:,.2f}.")
                else:
                    cur = conn.cursor()
                    try:
                        cur.execute("""
                            INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
                            VALUES (%s,%s,%s,%s)
                        """, (int(selected_sale_id), payment_date, amount_paid, payment_method))
                        conn.commit(); cur.close(); st.success("Payment entry added successfully.")
                        st.info("The received amount and status were updated automatically by the SQL trigger."); st.rerun()
                    except Exception as e:
                        cur.close(); st.error(f"Error while adding payment: {e}")

    else:
        st.header("🧮 Advanced SQL Engine")
        st.write("Execute the required SQL queries directly against the Sales Management System database.")
        st.info("Super Admin: SQL queries can access all branches." if role == "Super Admin" else f"Admin: SQL queries are restricted to the {user_branch_name} branch.")

        sql_queries = SQL_QUERIES

        st.subheader("📚 Required SQL Queries")
        selected_query_name = st.selectbox("Select SQL Query", list(sql_queries.keys()))
        selected_query = sql_queries[selected_query_name]
        executable_sql = selected_query["super"] if role == "Super Admin" else selected_query["admin"]
        query_params = None if role == "Super Admin" else (user_branch_id,)
        executable_sql = executable_sql.strip()
        st.subheader("💻 SQL Query")
        st.code(executable_sql.replace("%s", str(user_branch_id)) if query_params else executable_sql, language="sql")
        if st.button("▶️ Execute Live Database Query", type="primary", use_container_width=True, key="execute_live_sql_query"):
            try:
                result_df = pd.read_sql(executable_sql, conn, params=query_params) if query_params else pd.read_sql(executable_sql, conn)
                st.success("Live SQL query executed successfully.")
                st.write(f"**Records returned:** {len(result_df)}")
                if result_df.empty: st.info("Query executed successfully, but no records were found.")
                else:
                    st.subheader("📋 Query Result")
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"SQL execution error: {e}")