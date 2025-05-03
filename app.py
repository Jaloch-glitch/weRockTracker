import streamlit as st

# App configuration must be the first Streamlit command
st.set_page_config(
    page_title="weRock Services",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Import our modules
from models.database import initialize_db
from models.user import check_user_credentials, initialize_users, change_password, add_user, get_all_users
from services.finance_tracker import FinanceTracker
from utils.currency_converter import converter, format_currency, convert_and_format

# Initialize MongoDB connection
initialize_db()

# Initialize users when the app starts
initialize_users()

# Set default currency if not already set
if "currency" not in st.session_state:
    st.session_state.currency = "EUR"  # Default to Euro

# Check if user is authenticated
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_email = None

# Login Page
if not st.session_state.authenticated:
    st.title("weRock Services: AirBnB Finance Tracker")
    
    st.markdown("""
    ### Welcome to weRock Services
    
    This application helps weRock team track their AirBnB business finances, including:
    - Expenses and revenue tracking in Euros (€) or Kenyan Shillings (KSh)
    - Currency conversion between EUR and KSh
    - Asset management
    - Cash position monitoring
    - Financial reports and visualizations
    
    Please log in to continue.
    """)
    
    # Login form
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            valid, user = check_user_credentials(email, password)
            if valid:
                st.session_state.authenticated = True
                st.session_state.user_id = user["user_id"]
                st.session_state.user_name = user["name"]
                st.session_state.user_email = user["email"]
                st.rerun()
            else:
                st.error("Invalid email or password")
    
    # Display allowed users for demo purposes 
    st.info("Log in with your weRock Services account")
    st.caption("""
    Have Fun Make Money!!
    """)

# Main Application (only shown if authenticated)
else:
    # Initialize the tracker - we use a single tracker instance since data is shared
    if "finance_tracker" not in st.session_state:
        # For shared data, we can use any user_id as all will see the same data
        st.session_state.finance_tracker = FinanceTracker("shared_data")
    
    tracker = st.session_state.finance_tracker
    
    # App title and description
    st.title("weRock Services: AirBnB Finance Tracker")
    st.markdown(f"""
    Welcome back, **{st.session_state.user_name}**! ({st.session_state.user_email})  
    
    This application helps the weRock team track their AirBnB business finances, including expenses, revenue, assets, and cash positions.
    Use the sidebar to navigate between different sections.
    """)
    
    # Currency selector in the sidebar
    st.sidebar.title("Settings")
    
    # Display current currency
    current_currency = st.session_state.currency  # EUR or KES
    current_symbol = "€" if current_currency == "EUR" else "KSh"
    
    selected_currency = st.sidebar.radio(
        "Currency", 
        options=["EUR", "KES"],
        index=0 if current_currency == "EUR" else 1,
        format_func=lambda x: "Euro (€)" if x == "EUR" else "Kenyan Shilling (KSh)"
    )
    
    # Update currency if changed
    if selected_currency != current_currency:
        st.session_state.currency = selected_currency
        st.rerun()
        
    # If current currency is KES, show conversion rate
    if current_currency == "KES":
        eur_to_kes_rate = converter.get_exchange_rate("EUR", "KES")
        st.sidebar.info(f"Current Rate: 1 EUR = {eur_to_kes_rate:.2f} KSh")
    else:
        kes_to_eur_rate = converter.get_exchange_rate("KES", "EUR")
        st.sidebar.info(f"Current Rate: 1 KSh = {kes_to_eur_rate:.4f} EUR")
    
    # User profile section
    with st.sidebar.expander("User Profile"):
        st.write(f"Name: {st.session_state.user_name}")
        st.write(f"Email: {st.session_state.user_email}")
        
        # Password change form
        st.subheader("Change Password")
        with st.form("password_form"):
            current_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            pwd_submit = st.form_submit_button("Change Password")
            
            if pwd_submit:
                if new_pwd != confirm_pwd:
                    st.error("New password and confirmation do not match")
                elif len(new_pwd) < 8:
                    st.error("New password must be at least 8 characters long")
                else:
                    success, message = change_password(st.session_state.user_id, current_pwd, new_pwd)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    # Admin section for managing users (only for Brian)
    if st.session_state.user_email == "brianGuru@werock.com":
        with st.sidebar.expander("Admin Settings"):
            st.subheader("Add New User")
            with st.form("add_user_form"):
                new_user_email = st.text_input("Email")
                new_user_name = st.text_input("Name")
                new_user_pwd = st.text_input("Password", type="password")
                add_user_submit = st.form_submit_button("Add User")
                
                if add_user_submit:
                    if len(new_user_pwd) < 8:
                        st.error("Password must be at least 8 characters long")
                    elif not new_user_email or not new_user_name:
                        st.error("Email and name are required")
                    else:
                        success, message = add_user(new_user_email, new_user_name, new_user_pwd)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
            
            st.subheader("Current Users")
            users = get_all_users()
            for user in users:
                st.write(f"• {user['name']} ({user['email']})")
    
    # Logout button in the sidebar
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Transactions", "Cash", "Assets", "Reports"])
    
    # Get currency symbol for display
    currency_symbol = "€" if current_currency == "EUR" else "KSh"
    alt_currency = "KES" if current_currency == "EUR" else "EUR"
    alt_symbol = "KSh" if current_currency == "EUR" else "€"
    
    # Dashboard Page
    if page == "Dashboard":
        st.header("AirBnB Business Dashboard")
        
        # Get current month and year
        current_date = datetime.datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Get monthly summary
        monthly_summary = tracker.get_monthly_summary(current_year, current_month)
        
        # Display summary in columns with both currencies
        col1, col2, col3 = st.columns(3)
        
        with col1:
            revenue_alt = converter.convert(monthly_summary['total_revenue'], "EUR", alt_currency)
            st.metric(
                "Total Revenue", 
                f"{currency_symbol}{monthly_summary['total_revenue']:,.2f}",
                delta=f"{alt_symbol}{revenue_alt:,.2f}"
            )
        
        with col2:
            expenses_alt = converter.convert(monthly_summary['total_expenses'], "EUR", alt_currency)
            st.metric(
                "Total Expenses", 
                f"{currency_symbol}{monthly_summary['total_expenses']:,.2f}",
                delta=f"{alt_symbol}{expenses_alt:,.2f}"
            )
        
        with col3:
            net_alt = converter.convert(monthly_summary['net_income'], "EUR", alt_currency)
            st.metric(
                "Net Income", 
                f"{currency_symbol}{monthly_summary['net_income']:,.2f}", 
                delta=f"{alt_symbol}{net_alt:,.2f}"
            )
        
        st.caption("Note: Primary currency shown in main value, alternative currency shown in delta")
        
        # Cash position
        st.subheader("Cash Position")
        cash_data = tracker.get_cash_position()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cash_hand_alt = converter.convert(cash_data['in_hand'], "EUR", alt_currency)
            st.metric(
                "Cash in Hand", 
                f"{currency_symbol}{cash_data['in_hand']:,.2f}",
                delta=f"{alt_symbol}{cash_hand_alt:,.2f}"
            )
        
        with col2:
            cash_bank_alt = converter.convert(cash_data['in_bank'], "EUR", alt_currency)
            st.metric(
                "Cash in Bank", 
                f"{currency_symbol}{cash_data['in_bank']:,.2f}",
                delta=f"{alt_symbol}{cash_bank_alt:,.2f}"
            )
        
        with col3:
            total_cash = cash_data['in_hand'] + cash_data['in_bank']
            total_cash_alt = converter.convert(total_cash, "EUR", alt_currency)
            st.metric(
                "Total Cash", 
                f"{currency_symbol}{total_cash:,.2f}",
                delta=f"{alt_symbol}{total_cash_alt:,.2f}"
            )
        
        # Recent transactions
        st.subheader("Recent Transactions")
        
        # Get transactions
        expenses_df = tracker.get_all_expenses()
        revenue_df = tracker.get_all_revenue()
        
        if not expenses_df.empty or not revenue_df.empty:
            # Initialize empty DataFrames if needed
            if expenses_df.empty:
                expenses_df = pd.DataFrame(columns=['date', 'description', 'category', 'amount'])
            if revenue_df.empty:
                revenue_df = pd.DataFrame(columns=['date', 'description', 'category', 'amount'])
            
            # Add transaction type
            expenses_df['type'] = 'Expense'
            revenue_df['type'] = 'Revenue'
            
            # Select columns
            expenses_df = expenses_df[['date', 'description', 'category', 'amount', 'type']]
            revenue_df = revenue_df[['date', 'description', 'category', 'amount', 'type']]
            
            # Combine and sort by date
            all_transactions = pd.concat([expenses_df, revenue_df], ignore_index=True)
            all_transactions = all_transactions.sort_values('date', ascending=False)
            
            # Display recent transactions (last 5)
            recent_transactions = all_transactions.head(5)
            
            # For display - create a copy to avoid modifying the original data
            display_df = recent_transactions.copy()
            
            # Format for display
            display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
            
            # Add converted amount column
            if current_currency == "EUR":
                display_df['amount'] = display_df['amount'].apply(lambda x: f"€{x:,.2f}")
                display_df['amount_alt'] = recent_transactions['amount'].apply(
                    lambda x: f"KSh{converter.convert(x, 'EUR', 'KES'):,.2f}"
                )
            else:
                # Convert EUR to KES for display
                display_df['amount'] = recent_transactions['amount'].apply(
                    lambda x: f"KSh{converter.convert(x, 'EUR', 'KES'):,.2f}"
                )
                display_df['amount_alt'] = recent_transactions['amount'].apply(lambda x: f"€{x:,.2f}")
            
            # Rename columns
            display_df.columns = ['Date', 'Description', 'Category', 
                                 f'Amount ({currency_symbol})', 'Type', 
                                 f'Amount ({alt_symbol})']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No transactions found. Start by adding expenses and revenue in the Transactions section.")
        
        # Monthly summary chart
        st.subheader("Monthly Summary")
        fig = tracker.plot_monthly_summary(current_year, current_month)
        st.pyplot(fig)
    
    # Transactions Page
    elif page == "Transactions":
        st.header("Manage AirBnB Transactions")
        
        # Currency conversion calculator
        with st.expander("Currency Converter"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                convert_amount = st.number_input("Amount", min_value=0.01, value=100.0, step=0.01)
            
            with col2:
                from_curr = st.selectbox("From", ["EUR", "KES"], 
                                         index=0 if current_currency == "EUR" else 1)
            
            with col3:
                to_curr = st.selectbox("To", ["KES", "EUR"], 
                                       index=0 if current_currency == "KES" else 1)
            
            # Calculate conversion
            converted = converter.convert(convert_amount, from_curr, to_curr)
            
            # Display result
            st.success(f"{convert_amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}")
        
        # Create tabs for expenses and revenue
        tab1, tab2 = st.tabs(["Add Expense", "Add Revenue"])
        
        # Tab 1: Add Expense
        with tab1:
            st.subheader("Add New Expense")
            
            with st.form("expense_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Always store in EUR internally but display in selected currency
                    if current_currency == "EUR":
                        expense_amount = st.number_input(f"Amount ({currency_symbol})", min_value=0.01, step=0.01)
                        # Internal amount is the same as input
                        internal_amount = expense_amount
                    else:
                        # Input in KES
                        expense_amount = st.number_input(f"Amount ({currency_symbol})", min_value=0.01, step=0.01)
                        # Convert to EUR for storage
                        internal_amount = converter.convert(expense_amount, "KES", "EUR")
                        # Show conversion
                        st.caption(f"Will be stored as: €{internal_amount:.2f}")
                        
                    expense_date = st.date_input("Date", value=datetime.datetime.now())
                    expense_category = st.selectbox("Category", tracker.expense_categories)
                
                with col2:
                    expense_description = st.text_input("Description")
                    expense_payment_method = st.selectbox(
                        "Payment Method", 
                        ["Cash", "Debit Card", "Credit Card", "Bank Transfer", "Mobile Money", "M-Pesa", "Other"]
                    )
                    expense_notes = st.text_area("Notes", height=100)
                
                submit_expense = st.form_submit_button("Add Expense")
            
            if submit_expense:
                if expense_amount > 0 and expense_description:
                    # Format date
                    formatted_date = expense_date
                    
                    # Add expense (always store in EUR)
                    try:
                        tracker.add_expense(
                            internal_amount,  # Already converted to EUR if needed
                            expense_description,
                            expense_category,
                            formatted_date,
                            expense_payment_method,
                            expense_notes
                        )
                        
                        st.success(f"✅ Expense added: {currency_symbol}{expense_amount:.2f} for {expense_description}")
                    except Exception as e:
                        st.error(f"Error adding expense: {str(e)}")
                else:
                    st.error("Please fill in all required fields (amount and description).")
        
        # Tab 2: Add Revenue
        with tab2:
            st.subheader("Add New Revenue")
            
            with st.form("revenue_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Always store in EUR internally but display in selected currency
                    if current_currency == "EUR":
                        revenue_amount = st.number_input(f"Amount ({currency_symbol})", min_value=0.01, step=0.01, key="revenue_amount")
                        # Internal amount is the same as input
                        internal_revenue = revenue_amount
                    else:
                        # Input in KES
                        revenue_amount = st.number_input(f"Amount ({currency_symbol})", min_value=0.01, step=0.01, key="revenue_amount")
                        # Convert to EUR for storage
                        internal_revenue = converter.convert(revenue_amount, "KES", "EUR")
                        # Show conversion
                        st.caption(f"Will be stored as: €{internal_revenue:.2f}")
                        
                    revenue_date = st.date_input("Date", value=datetime.datetime.now(), key="revenue_date")
                    revenue_category = st.selectbox("Category", tracker.revenue_categories)
                
                with col2:
                    revenue_description = st.text_input("Description", key="revenue_description")
                    revenue_source = st.text_input("Source (e.g., Booking Platform)")
                    revenue_notes = st.text_area("Notes", height=100, key="revenue_notes")
                
                submit_revenue = st.form_submit_button("Add Revenue")
            
            if submit_revenue:
                if revenue_amount > 0 and revenue_description:
                    # Format date
                    formatted_date = revenue_date
                    
                    # Add revenue (always store in EUR)
                    try:
                        tracker.add_revenue(
                            internal_revenue,  # Already converted to EUR if needed
                            revenue_description,
                            revenue_category,
                            formatted_date,
                            revenue_source,
                            revenue_notes
                        )
                        
                        st.success(f"✅ Revenue added: {currency_symbol}{revenue_amount:.2f} from {revenue_description}")
                    except Exception as e:
                        st.error(f"Error adding revenue: {str(e)}")
                else:
                    st.error("Please fill in all required fields (amount and description).")
        
        # Display all transactions
        st.subheader("View Transactions")
        view_type = st.radio("Show", ["Expenses", "Revenue", "All Transactions"])
        
        if view_type == "Expenses":
            expenses_df = tracker.get_all_expenses()
            if not expenses_df.empty:
                # Select columns to display
                display_cols = ['date', 'description', 'category', 'amount', 'payment_method', 'notes']
                display_df = expenses_df[display_cols].copy()
                
                # Format date and currency columns
                display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
                
                # If current currency is KES, convert from EUR to KES for display
                if current_currency == "KES":
                    display_df['amount_kes'] = display_df['amount'].apply(
                        lambda x: converter.convert(x, "EUR", "KES")
                    )
                    display_df['amount'] = display_df['amount_kes'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                    display_df.drop('amount_kes', axis=1, inplace=True)
                else:
                    display_df['amount'] = display_df['amount'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Calculate total and show in both currencies
                total_expenses_eur = expenses_df['amount'].sum()
                if current_currency == "EUR":
                    total_expenses_display = total_expenses_eur
                    total_expenses_alt = converter.convert(total_expenses_eur, "EUR", "KES")
                    st.metric("Total Expenses", f"€{total_expenses_display:,.2f}", delta=f"KSh{total_expenses_alt:,.2f}")
                else:
                    total_expenses_display = converter.convert(total_expenses_eur, "EUR", "KES")
                    st.metric("Total Expenses", f"KSh{total_expenses_display:,.2f}", delta=f"€{total_expenses_eur:,.2f}")
            else:
                st.info("No expenses found.")
        
        elif view_type == "Revenue":
            revenue_df = tracker.get_all_revenue()
            if not revenue_df.empty:
                # Select columns to display
                display_cols = ['date', 'description', 'category', 'amount', 'source', 'notes']
                display_df = revenue_df[display_cols].copy()
                
                # Format date and currency columns
                display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
                
                # If current currency is KES, convert from EUR to KES for display
                if current_currency == "KES":
                    display_df['amount_kes'] = display_df['amount'].apply(
                        lambda x: converter.convert(x, "EUR", "KES")
                    )
                    display_df['amount'] = display_df['amount_kes'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                    display_df.drop('amount_kes', axis=1, inplace=True)
                else:
                    display_df['amount'] = display_df['amount'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Calculate total and show in both currencies
                total_revenue_eur = revenue_df['amount'].sum()
                if current_currency == "EUR":
                    total_revenue_display = total_revenue_eur
                    total_revenue_alt = converter.convert(total_revenue_eur, "EUR", "KES")
                    st.metric("Total Revenue", f"€{total_revenue_display:,.2f}", delta=f"KSh{total_revenue_alt:,.2f}")
                else:
                    total_revenue_display = converter.convert(total_revenue_eur, "EUR", "KES")
                    st.metric("Total Revenue", f"KSh{total_revenue_display:,.2f}", delta=f"€{total_revenue_eur:,.2f}")
            else:
                st.info("No revenue found.")
        
        else:  # All Transactions
            expenses_df = tracker.get_all_expenses()
            revenue_df = tracker.get_all_revenue()
            
            if not expenses_df.empty or not revenue_df.empty:
                # Initialize empty DataFrames if needed
                if expenses_df.empty:
                    expenses_df = pd.DataFrame(columns=['date', 'description', 'category', 'amount'])
                if revenue_df.empty:
                    revenue_df = pd.DataFrame(columns=['date', 'description', 'category', 'amount'])
                
                # Add transaction type
                expenses_df['type'] = 'Expense'
                revenue_df['type'] = 'Revenue'
                
                # Select columns
                expenses_df = expenses_df[['date', 'description', 'category', 'amount', 'type']]
                revenue_df = revenue_df[['date', 'description', 'category', 'amount', 'type']]
                
                # Combine and sort by date
                all_transactions = pd.concat([expenses_df, revenue_df], ignore_index=True)
                all_transactions = all_transactions.sort_values('date', ascending=False)
                
                # Format for display
                display_df = all_transactions.copy()
                display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
                
                # If current currency is KES, convert from EUR to KES for display
                if current_currency == "KES":
                    display_df['amount_kes'] = display_df['amount'].apply(
                        lambda x: converter.convert(x, "EUR", "KES")
                    )
                    display_df['amount'] = display_df['amount_kes'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                    display_df.drop('amount_kes', axis=1, inplace=True)
                else:
                    display_df['amount'] = display_df['amount'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Show totals with both currencies
                col1, col2, col3 = st.columns(3)
                
                # Calculate totals in EUR (stored currency)
                total_expenses_eur = expenses_df['amount'].sum()
                total_revenue_eur = revenue_df['amount'].sum()
                net_income_eur = total_revenue_eur - total_expenses_eur
                
                with col1:
                    if current_currency == "EUR":
                        total_expenses_kes = converter.convert(total_expenses_eur, "EUR", "KES")
                        st.metric("Total Expenses", f"€{total_expenses_eur:,.2f}", delta=f"KSh{total_expenses_kes:,.2f}")
                    else:
                        total_expenses_kes = converter.convert(total_expenses_eur, "EUR", "KES")
                        st.metric("Total Expenses", f"KSh{total_expenses_kes:,.2f}", delta=f"€{total_expenses_eur:,.2f}")
                        
                with col2:
                    if current_currency == "EUR":
                        total_revenue_kes = converter.convert(total_revenue_eur, "EUR", "KES")
                        st.metric("Total Revenue", f"€{total_revenue_eur:,.2f}", delta=f"KSh{total_revenue_kes:,.2f}")
                    else:
                        total_revenue_kes = converter.convert(total_revenue_eur, "EUR", "KES")
                        st.metric("Total Revenue", f"KSh{total_revenue_kes:,.2f}", delta=f"€{total_revenue_eur:,.2f}")
                        
                with col3:
                    if current_currency == "EUR":
                        net_income_kes = converter.convert(net_income_eur, "EUR", "KES")
                        st.metric("Net Income", f"€{net_income_eur:,.2f}", delta=f"KSh{net_income_kes:,.2f}")
                    else:
                        net_income_kes = converter.convert(net_income_eur, "EUR", "KES")
                        st.metric("Net Income", f"KSh{net_income_kes:,.2f}", delta=f"€{net_income_eur:,.2f}")
            else:
                st.info("No transactions found.")
    
    # Cash Page
    elif page == "Cash":
        st.header("Cash Management")
        
        # Get current cash position
        cash_data = tracker.get_cash_position()
        
        # Display current cash position
        st.subheader("Current Cash Position")
        col1, col2, col3 = st.columns(3)
        
        # Cash values (stored in EUR)
        cash_in_hand_eur = cash_data['in_hand']
        cash_in_bank_eur = cash_data['in_bank']
        total_cash_eur = cash_in_hand_eur + cash_in_bank_eur
        
        # Calculate KES equivalents
        cash_in_hand_kes = converter.convert(cash_in_hand_eur, "EUR", "KES")
        cash_in_bank_kes = converter.convert(cash_in_bank_eur, "EUR", "KES")
        total_cash_kes = converter.convert(total_cash_eur, "EUR", "KES")
        
        with col1:
            if current_currency == "EUR":
                st.metric("Cash in Hand", f"€{cash_in_hand_eur:,.2f}", delta=f"KSh{cash_in_hand_kes:,.2f}")
            else:
                st.metric("Cash in Hand", f"KSh{cash_in_hand_kes:,.2f}", delta=f"€{cash_in_hand_eur:,.2f}")
        
        with col2:
            if current_currency == "EUR":
                st.metric("Cash in Bank", f"€{cash_in_bank_eur:,.2f}", delta=f"KSh{cash_in_bank_kes:,.2f}")
            else:
                st.metric("Cash in Bank", f"KSh{cash_in_bank_kes:,.2f}", delta=f"€{cash_in_bank_eur:,.2f}")
        
        with col3:
            if current_currency == "EUR":
                st.metric("Total Cash", f"€{total_cash_eur:,.2f}", delta=f"KSh{total_cash_kes:,.2f}")
            else:
                st.metric("Total Cash", f"KSh{total_cash_kes:,.2f}", delta=f"€{total_cash_eur:,.2f}")
        
        st.caption(f"Last Updated: {cash_data['last_updated']}")
        
        # Update cash position form
        st.subheader("Update Cash Position")
        
        with st.form("cash_form"):
            col1, col2 = st.columns(2)
            
            # Show input fields in current currency
            with col1:
                if current_currency == "EUR":
                    cash_in_hand = st.number_input(f"Cash in Hand ({currency_symbol})", min_value=0.0, value=float(cash_data['in_hand']), step=0.01)
                    internal_cash_hand = cash_in_hand
                else:
                    cash_in_hand_kes = converter.convert(cash_data['in_hand'], "EUR", "KES")
                    cash_in_hand = st.number_input(f"Cash in Hand ({currency_symbol})", min_value=0.0, value=float(cash_in_hand_kes), step=0.01)
                    internal_cash_hand = converter.convert(cash_in_hand, "KES", "EUR")
                    st.caption(f"Will be stored as: €{internal_cash_hand:.2f}")
            
            with col2:
                if current_currency == "EUR":
                    cash_in_bank = st.number_input(f"Cash in Bank ({currency_symbol})", min_value=0.0, value=float(cash_data['in_bank']), step=0.01)
                    internal_cash_bank = cash_in_bank
                else:
                    cash_in_bank_kes = converter.convert(cash_data['in_bank'], "EUR", "KES")
                    cash_in_bank = st.number_input(f"Cash in Bank ({currency_symbol})", min_value=0.0, value=float(cash_in_bank_kes), step=0.01)
                    internal_cash_bank = converter.convert(cash_in_bank, "KES", "EUR")
                    st.caption(f"Will be stored as: €{internal_cash_bank:.2f}")
            
            submit_cash = st.form_submit_button("Update Cash")
        
        if submit_cash:
            try:
                # Always update with EUR values internally
                tracker.update_cash(internal_cash_hand, internal_cash_bank)
                st.success("✅ Cash position updated")
                st.rerun()  # Refresh the page to show updated values
            except Exception as e:
                st.error(f"Error updating cash position: {str(e)}")
    
    # Assets Page
    elif page == "Assets":
        st.header("AirBnB Asset Management")
        
        # Create tabs
        tab1, tab2 = st.tabs(["Add Asset", "View Assets"])
        
        # Tab 1: Add Asset
        with tab1:
            st.subheader("Add New Asset")
            
            with st.form("asset_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    asset_name = st.text_input("Asset Name")
                    asset_type = st.selectbox("Asset Type", tracker.asset_types)
                    
                    # Show input fields in current currency
                    if current_currency == "EUR":
                        asset_current_value = st.number_input(f"Current Value ({currency_symbol})", min_value=0.01, step=0.01)
                        internal_current_value = asset_current_value
                    else:
                        asset_current_value = st.number_input(f"Current Value ({currency_symbol})", min_value=0.01, step=0.01)
                        internal_current_value = converter.convert(asset_current_value, "KES", "EUR")
                        st.caption(f"Will be stored as: €{internal_current_value:.2f}")
                
                with col2:
                    # Show input fields in current currency
                    if current_currency == "EUR":
                        asset_purchase_value = st.number_input(f"Purchase Value ({currency_symbol}, Optional)", min_value=0.0, step=0.01)
                        internal_purchase_value = asset_purchase_value
                    else:
                        asset_purchase_value = st.number_input(f"Purchase Value ({currency_symbol}, Optional)", min_value=0.0, step=0.01)
                        internal_purchase_value = converter.convert(asset_purchase_value, "KES", "EUR") if asset_purchase_value > 0 else 0
                        if asset_purchase_value > 0:
                            st.caption(f"Will be stored as: €{internal_purchase_value:.2f}")
                            
                    asset_purchase_date = st.date_input("Purchase Date", value=datetime.datetime.now())
                    asset_location = st.text_input("Location (Optional)")
                
                asset_notes = st.text_area("Notes (Optional)")
                
                submit_asset = st.form_submit_button("Add Asset")
            
            if submit_asset:
                if asset_name and asset_current_value > 0:
                    # Format date
                    formatted_date = asset_purchase_date
                    
                    # Add asset (always store in EUR)
                    try:
                        tracker.add_asset(
                            asset_name,
                            asset_type,
                            internal_current_value,
                            internal_purchase_value,
                            formatted_date,
                            asset_location,
                            asset_notes
                        )
                        
                        st.success(f"✅ Asset added: {asset_name} ({currency_symbol}{asset_current_value:.2f})")
                    except Exception as e:
                        st.error(f"Error adding asset: {str(e)}")
                else:
                    st.error("Please provide at least a name and current value for the asset.")
        
        # Tab 2: View Assets
        with tab2:
            st.subheader("AirBnB Business Assets")
            
            assets_df = tracker.get_all_assets()
            if not assets_df.empty:
                # Select columns to display
                display_cols = ['name', 'type', 'current_value', 'purchase_value', 'purchase_date', 'location']
                display_df = assets_df[display_cols].copy()
                
                # Format date
                display_df['purchase_date'] = pd.to_datetime(display_df['purchase_date']).dt.strftime('%Y-%m-%d')
                
                # If current currency is KES, convert from EUR to KES for display
                if current_currency == "KES":
                    display_df['current_value_kes'] = display_df['current_value'].apply(
                        lambda x: converter.convert(x, "EUR", "KES")
                    )
                    display_df['current_value'] = display_df['current_value_kes'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                    display_df.drop('current_value_kes', axis=1, inplace=True)
                    
                    # Only convert purchase value if it exists and is > 0
                    display_df['purchase_value'] = display_df.apply(
                        lambda row: f"{currency_symbol}{converter.convert(row['purchase_value'], 'EUR', 'KES'):,.2f}" 
                        if pd.notnull(row['purchase_value']) and row['purchase_value'] > 0 
                        else "N/A",
                        axis=1
                    )
                else:
                    display_df['current_value'] = display_df['current_value'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                    display_df['purchase_value'] = display_df['purchase_value'].apply(
                        lambda x: f"{currency_symbol}{x:,.2f}" if pd.notnull(x) and x > 0 else "N/A"
                    )
                
                st.dataframe(display_df, use_container_width=True)
                
                # Calculate total assets value in both currencies
                total_assets_eur = assets_df['current_value'].sum()
                total_assets_kes = converter.convert(total_assets_eur, "EUR", "KES")
                
                if current_currency == "EUR":
                    st.metric("Total Assets Value", f"€{total_assets_eur:,.2f}", delta=f"KSh{total_assets_kes:,.2f}")
                else:
                    st.metric("Total Assets Value", f"KSh{total_assets_kes:,.2f}", delta=f"€{total_assets_eur:,.2f}")
                
                # Plot assets breakdown
                st.subheader("Assets Breakdown")
                fig = tracker.plot_assets_breakdown()
                if fig:
                    st.pyplot(fig)
            else:
                st.info("No assets found. Start by adding some assets.")
    
    # Reports Page
    elif page == "Reports":
        st.header("AirBnB Financial Reports")
        
        # Report type selector
        report_type = st.radio("Report Type", ["Monthly Summary", "Yearly Trends", "Expense Categories", "Revenue Categories"])
        
        # Year and month selectors
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        
        col1, col2 = st.columns(2)
        
        with col1:
            year = st.selectbox("Year", range(current_year-5, current_year+1), index=5)
        
        with col2:
            if report_type == "Monthly Summary":
                month = st.selectbox("Month", range(1, 13), index=current_month-1, format_func=lambda x: datetime.date(2000, x, 1).strftime('%B'))
        
        # Generate and display the selected report
        if report_type == "Monthly Summary":
            st.subheader(f"Monthly Summary - {datetime.date(year, month, 1).strftime('%B %Y')}")
            
            # Get monthly summary
            monthly_summary = tracker.get_monthly_summary(year, month)
            
            # Display summary in columns with both currencies
            col1, col2, col3 = st.columns(3)
            
            # Calculate KES values
            revenue_kes = converter.convert(monthly_summary['total_revenue'], "EUR", "KES")
            expenses_kes = converter.convert(monthly_summary['total_expenses'], "EUR", "KES")
            net_income_kes = converter.convert(monthly_summary['net_income'], "EUR", "KES")
            
            with col1:
                if current_currency == "EUR":
                    st.metric("Total Revenue", f"€{monthly_summary['total_revenue']:,.2f}", delta=f"KSh{revenue_kes:,.2f}")
                else:
                    st.metric("Total Revenue", f"KSh{revenue_kes:,.2f}", delta=f"€{monthly_summary['total_revenue']:,.2f}")
            
            with col2:
                if current_currency == "EUR":
                    st.metric("Total Expenses", f"€{monthly_summary['total_expenses']:,.2f}", delta=f"KSh{expenses_kes:,.2f}")
                else:
                    st.metric("Total Expenses", f"KSh{expenses_kes:,.2f}", delta=f"€{monthly_summary['total_expenses']:,.2f}")
            
            with col3:
                if current_currency == "EUR":
                    st.metric("Net Income", f"€{monthly_summary['net_income']:,.2f}", 
                             delta=f"KSh{net_income_kes:,.2f}")
                else:
                    st.metric("Net Income", f"KSh{net_income_kes:,.2f}", 
                             delta=f"€{monthly_summary['net_income']:,.2f}")
            
            # Display charts
            fig = tracker.plot_monthly_summary(year, month)
            st.pyplot(fig)
            
        elif report_type == "Yearly Trends":
            st.subheader(f"Yearly Financial Trends - {year}")
            
            # Get yearly summary
            yearly_summary = tracker.get_yearly_summary(year)
            
            # Display summary in columns with both currencies
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate KES values
            revenue_kes = converter.convert(yearly_summary['total_revenue'], "EUR", "KES")
            expenses_kes = converter.convert(yearly_summary['total_expenses'], "EUR", "KES")
            net_income_kes = converter.convert(yearly_summary['net_income'], "EUR", "KES")
            
            with col1:
                if current_currency == "EUR":
                    st.metric("Total Revenue", f"€{yearly_summary['total_revenue']:,.2f}", delta=f"KSh{revenue_kes:,.2f}")
                else:
                    st.metric("Total Revenue", f"KSh{revenue_kes:,.2f}", delta=f"€{yearly_summary['total_revenue']:,.2f}")
            
            with col2:
                if current_currency == "EUR":
                    st.metric("Total Expenses", f"€{yearly_summary['total_expenses']:,.2f}", delta=f"KSh{expenses_kes:,.2f}")
                else:
                    st.metric("Total Expenses", f"KSh{expenses_kes:,.2f}", delta=f"€{yearly_summary['total_expenses']:,.2f}")
            
            with col3:
                if current_currency == "EUR":
                    st.metric("Net Income", f"€{yearly_summary['net_income']:,.2f}", delta=f"KSh{net_income_kes:,.2f}")
                else:
                    st.metric("Net Income", f"KSh{net_income_kes:,.2f}", delta=f"€{yearly_summary['net_income']:,.2f}")
            
            with col4:
                st.metric("Savings Rate", f"{yearly_summary['savings_rate']:.1f}%")
            
            # Display chart
            fig = tracker.plot_yearly_trend(year)
            st.pyplot(fig)
            
        elif report_type == "Expense Categories":
            st.subheader(f"Expense Categories - {year}")
            
            fig = tracker.plot_category_breakdown('expenses', year)
            if fig:
                st.pyplot(fig)
            
        elif report_type == "Revenue Categories":
            st.subheader(f"Revenue Categories - {year}")
            
            fig = tracker.plot_category_breakdown('revenue', year)
            if fig:
                st.pyplot(fig)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 weRock Services | AirBnB Finance Tracker")