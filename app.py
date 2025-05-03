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
from models.user import check_user_credentials, initialize_users
from services.finance_tracker import FinanceTracker

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
    
    This application helps Brian and Felix track their AirBnB business:
    
    
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

# Main Application (only shown if authenticated)
else:
    # Initialize the tracker with user_id
    if "finance_tracker" not in st.session_state:
        st.session_state.finance_tracker = FinanceTracker(st.session_state.user_id)
    
    tracker = st.session_state.finance_tracker
    
    # App title and description
    st.title("weRock Services: AirBnB Finance Tracker")
    st.markdown(f"""
    Welcome back, **{st.session_state.user_name}**! ({st.session_state.user_email})  
    
    This application helps you track your AirBnB business finances, including expenses, revenue, assets, and cash positions.
    Use the sidebar to navigate between different sections.
    """)
    
    # Currency selector in the sidebar
    st.sidebar.title("Settings")
    selected_currency = st.sidebar.radio(
        "Currency", 
        options=["EUR", "KSh"],
        index=0 if st.session_state.currency == "EUR" else 1,
        format_func=lambda x: "Euro (€)" if x == "EUR" else "Kenyan Shilling (KSh)"
    )
    
    # Update currency if changed
    if selected_currency != st.session_state.currency:
        st.session_state.currency = selected_currency
        st.rerun()
    
    # Get currency symbol for display
    currency_symbol = "€" if st.session_state.currency == "EUR" else "KSh"
    
    # Logout button in the sidebar
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Transactions", "Cash", "Assets", "Reports"])
    
    # Dashboard Page
    if page == "Dashboard":
        st.header("AirBnB Business Dashboard")
        
        # Get current month and year
        current_date = datetime.datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Get monthly summary
        monthly_summary = tracker.get_monthly_summary(current_year, current_month)
        
        # Display summary in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Revenue", f"{currency_symbol}{monthly_summary['total_revenue']:,.2f}")
        
        with col2:
            st.metric("Total Expenses", f"{currency_symbol}{monthly_summary['total_expenses']:,.2f}")
        
        with col3:
            st.metric("Net Income", f"{currency_symbol}{monthly_summary['net_income']:,.2f}", 
                     delta=f"{monthly_summary['savings_rate']:.1f}%" if monthly_summary['savings_rate'] > 0 else f"{monthly_summary['savings_rate']:.1f}%")
        
        # Cash position
        st.subheader("Cash Position")
        cash_data = tracker.get_cash_position()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Cash in Hand", f"{currency_symbol}{cash_data['in_hand']:,.2f}")
        
        with col2:
            st.metric("Cash in Bank", f"{currency_symbol}{cash_data['in_bank']:,.2f}")
        
        with col3:
            total_cash = cash_data['in_hand'] + cash_data['in_bank']
            st.metric("Total Cash", f"{currency_symbol}{total_cash:,.2f}")
        
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
            
            # Format for display
            recent_transactions['date'] = pd.to_datetime(recent_transactions['date']).dt.strftime('%Y-%m-%d')
            recent_transactions['amount'] = recent_transactions['amount'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
            
            st.dataframe(recent_transactions, use_container_width=True)
        else:
            st.info("No transactions found. Start by adding expenses and revenue in the Transactions section.")
        
        # Monthly summary chart
        st.subheader("Monthly Summary")
        fig = tracker.plot_monthly_summary(current_year, current_month)
        st.pyplot(fig)
    
    # Transactions Page
    elif page == "Transactions":
        st.header("Manage AirBnB Transactions")
        
        # Create tabs for expenses and revenue
        tab1, tab2 = st.tabs(["Add Expense", "Add Revenue"])
        
        # Tab 1: Add Expense
        with tab1:
            st.subheader("Add New Expense")
            
            with st.form("expense_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    expense_amount = st.number_input(f"Amount ({currency_symbol})", min_value=0.01, step=0.01)
                    expense_date = st.date_input("Date", value=datetime.datetime.now())
                    expense_category = st.selectbox("Category", tracker.expense_categories)
                
                with col2:
                    expense_description = st.text_input("Description")
                    expense_payment_method = st.selectbox("Payment Method", ["Cash", "Debit Card", "Credit Card", "Bank Transfer", "Mobile Money", "Other"])
                    expense_notes = st.text_area("Notes", height=100)
                
                submit_expense = st.form_submit_button("Add Expense")
            
            if submit_expense:
                if expense_amount > 0 and expense_description:
                    # Format date
                    formatted_date = expense_date
                    
                    # Add expense
                    try:
                        tracker.add_expense(
                            expense_amount,
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
                    revenue_amount = st.number_input(f"Amount ({currency_symbol})", min_value=0.01, step=0.01, key="revenue_amount")
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
                    
                    # Add revenue
                    try:
                        tracker.add_revenue(
                            revenue_amount,
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
                display_df['amount'] = display_df['amount'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Show total
                st.metric("Total Expenses", f"{currency_symbol}{expenses_df['amount'].sum():,.2f}")
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
                display_df['amount'] = display_df['amount'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Show total
                st.metric("Total Revenue", f"{currency_symbol}{revenue_df['amount'].sum():,.2f}")
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
                display_df['amount'] = display_df['amount'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Show totals
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Expenses", f"{currency_symbol}{expenses_df['amount'].sum():,.2f}")
                with col2:
                    st.metric("Total Revenue", f"{currency_symbol}{revenue_df['amount'].sum():,.2f}")
                with col3:
                    net = revenue_df['amount'].sum() - expenses_df['amount'].sum()
                    st.metric("Net Income", f"{currency_symbol}{net:,.2f}")
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
        
        with col1:
            st.metric("Cash in Hand", f"{currency_symbol}{cash_data['in_hand']:,.2f}")
        
        with col2:
            st.metric("Cash in Bank", f"{currency_symbol}{cash_data['in_bank']:,.2f}")
        
        with col3:
            total_cash = cash_data['in_hand'] + cash_data['in_bank']
            st.metric("Total Cash", f"{currency_symbol}{total_cash:,.2f}")
        
        st.caption(f"Last Updated: {cash_data['last_updated']}")
        
        # Update cash position form
        st.subheader("Update Cash Position")
        
        with st.form("cash_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                cash_in_hand = st.number_input(f"Cash in Hand ({currency_symbol})", min_value=0.0, value=float(cash_data['in_hand']), step=0.01)
            
            with col2:
                cash_in_bank = st.number_input(f"Cash in Bank ({currency_symbol})", min_value=0.0, value=float(cash_data['in_bank']), step=0.01)
            
            submit_cash = st.form_submit_button("Update Cash")
        
        if submit_cash:
            try:
                tracker.update_cash(cash_in_hand, cash_in_bank)
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
                    asset_current_value = st.number_input(f"Current Value ({currency_symbol})", min_value=0.01, step=0.01)
                
                with col2:
                    asset_purchase_value = st.number_input(f"Purchase Value ({currency_symbol}, Optional)", min_value=0.0, step=0.01)
                    asset_purchase_date = st.date_input("Purchase Date", value=datetime.datetime.now())
                    asset_location = st.text_input("Location (Optional)")
                
                asset_notes = st.text_area("Notes (Optional)")
                
                submit_asset = st.form_submit_button("Add Asset")
            
            if submit_asset:
                if asset_name and asset_current_value > 0:
                    # Format date
                    formatted_date = asset_purchase_date
                    
                    # Add asset
                    try:
                        tracker.add_asset(
                            asset_name,
                            asset_type,
                            asset_current_value,
                            asset_purchase_value,
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
                
                # Format date and currency columns
                display_df['purchase_date'] = pd.to_datetime(display_df['purchase_date']).dt.strftime('%Y-%m-%d')
                display_df['current_value'] = display_df['current_value'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
                display_df['purchase_value'] = display_df['purchase_value'].apply(lambda x: f"{currency_symbol}{x:,.2f}" if pd.notnull(x) and x > 0 else "N/A")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Show total assets value
                st.metric("Total Assets Value", f"{currency_symbol}{assets_df['current_value'].sum():,.2f}")
                
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
            
            # Display summary in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Revenue", f"{currency_symbol}{monthly_summary['total_revenue']:,.2f}")
            
            with col2:
                st.metric("Total Expenses", f"{currency_symbol}{monthly_summary['total_expenses']:,.2f}")
            
            with col3:
                st.metric("Net Income", f"{currency_symbol}{monthly_summary['net_income']:,.2f}", 
                         delta=f"{monthly_summary['savings_rate']:.1f}%" if monthly_summary['savings_rate'] > 0 else f"{monthly_summary['savings_rate']:.1f}%")
            
            # Display charts
            fig = tracker.plot_monthly_summary(year, month)
            st.pyplot(fig)
            
        elif report_type == "Yearly Trends":
            st.subheader(f"Yearly Financial Trends - {year}")
            
            # Get yearly summary
            yearly_summary = tracker.get_yearly_summary(year)
            
            # Display summary in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Revenue", f"{currency_symbol}{yearly_summary['total_revenue']:,.2f}")
            
            with col2:
                st.metric("Total Expenses", f"{currency_symbol}{yearly_summary['total_expenses']:,.2f}")
            
            with col3:
                st.metric("Net Income", f"{currency_symbol}{yearly_summary['net_income']:,.2f}")
            
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