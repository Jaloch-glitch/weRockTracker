import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from models.expense import add_expense, get_all_expenses
from models.revenue import add_revenue, get_all_revenue
from models.asset import add_asset, get_all_assets
from models.cash import initialize_cash_position, update_cash, get_cash_position

# Set better visual style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['font.size'] = 12

class FinanceTracker:
    def __init__(self, user_id):
        self.user_id = user_id
        
        # AirBnB-specific expense categories
        self.expense_categories = [
            'Cleaning', 'Maintenance', 'Utilities', 'Supplies', 
            'Furniture', 'Decor', 'Linens', 'Toiletries', 
            'Property Management', 'Booking Fees', 'Marketing',
            'Insurance', 'Taxes', 'Mortgage/Rent', 'Other'
        ]
        
        # AirBnB-specific revenue categories
        self.revenue_categories = [
            'Booking Revenue', 'Cleaning Fees', 'Late Checkout Fees', 
            'Extra Guest Fees', 'Special Services', 'Refunds', 'Other'
        ]
        
        # Asset types relevant to AirBnB
        self.asset_types = [
            'Cash', 'Bank Account', 'Property', 'Furniture', 
            'Appliances', 'Electronics', 'Vehicles', 'Other'
        ]
        
        # Initialize cash position if it doesn't exist
        initialize_cash_position(self.user_id)
    
    def add_expense(self, amount, description, category, date=None, payment_method=None, notes=None):
        """Add a new expense entry"""
        return add_expense(
            self.user_id, 
            amount, 
            description, 
            category, 
            date, 
            payment_method, 
            notes
        )
    
    def add_revenue(self, amount, description, category, date=None, source=None, notes=None):
        """Add a new revenue entry"""
        return add_revenue(
            self.user_id, 
            amount, 
            description, 
            category, 
            date, 
            source, 
            notes
        )
    
    def add_asset(self, name, asset_type, current_value, purchase_value=None, purchase_date=None, location=None, notes=None):
        """Add a new asset"""
        return add_asset(
            self.user_id, 
            name, 
            asset_type, 
            current_value, 
            purchase_value, 
            purchase_date, 
            location, 
            notes
        )
    
    def update_cash(self, cash_in_hand, cash_in_bank):
        """Update cash positions"""
        return update_cash(
            self.user_id, 
            cash_in_hand, 
            cash_in_bank
        )
    
    def get_all_expenses(self):
        """Return all expenses as a DataFrame"""
        return get_all_expenses(self.user_id)
    
    def get_all_revenue(self):
        """Return all revenue as a DataFrame"""
        return get_all_revenue(self.user_id)
    
    def get_all_assets(self):
        """Return all assets as a DataFrame"""
        return get_all_assets(self.user_id)
    
    def get_cash_position(self):
        """Return cash positions"""
        return get_cash_position(self.user_id)
    
    def get_monthly_summary(self, year=None, month=None):
        """Get financial summary for a specific month"""
        if year is None or month is None:
            now = datetime.datetime.now()
            year = now.year
            month = now.month
            
        # Convert to DataFrames
        expenses_df = self.get_all_expenses()
        revenue_df = self.get_all_revenue()
        
        # No data
        if expenses_df.empty and revenue_df.empty:
            return {
                'month': month,
                'year': year,
                'total_expenses': 0,
                'total_revenue': 0,
                'net_income': 0,
                'savings_rate': 0,
                'expense_by_category': {},
                'revenue_by_category': {}
            }
            
        # Filter by month and year
        if not expenses_df.empty:
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            month_expenses = expenses_df[
                (expenses_df['date'].dt.month == month) & 
                (expenses_df['date'].dt.year == year)
            ]
        else:
            month_expenses = pd.DataFrame()
            
        if not revenue_df.empty:
            revenue_df['date'] = pd.to_datetime(revenue_df['date'])
            month_revenue = revenue_df[
                (revenue_df['date'].dt.month == month) & 
                (revenue_df['date'].dt.year == year)
            ]
        else:
            month_revenue = pd.DataFrame()
            
        # Calculate totals
        total_expenses = month_expenses['amount'].sum() if not month_expenses.empty else 0
        total_revenue = month_revenue['amount'].sum() if not month_revenue.empty else 0
        net_income = total_revenue - total_expenses
        savings_rate = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        # Group by category
        expense_by_category = {}
        if not month_expenses.empty:
            for category in self.expense_categories:
                cat_amount = month_expenses[month_expenses['category'] == category]['amount'].sum()
                if cat_amount > 0:
                    expense_by_category[category] = float(cat_amount)
                    
        revenue_by_category = {}
        if not month_revenue.empty:
            for category in self.revenue_categories:
                cat_amount = month_revenue[month_revenue['category'] == category]['amount'].sum()
                if cat_amount > 0:
                    revenue_by_category[category] = float(cat_amount)
                    
        return {
            'month': month,
            'year': year,
            'total_expenses': float(total_expenses),
            'total_revenue': float(total_revenue),
            'net_income': float(net_income),
            'savings_rate': float(savings_rate),
            'expense_by_category': expense_by_category,
            'revenue_by_category': revenue_by_category
        }
        
    def get_yearly_summary(self, year=None):
        """Get financial summary for a specific year"""
        if year is None:
            year = datetime.datetime.now().year
            
        # Initialize month summaries
        monthly_data = []
        
        # Get summary for each month
        for month in range(1, 13):
            monthly_summary = self.get_monthly_summary(year, month)
            monthly_data.append({
                'month': month,
                'month_name': datetime.date(2000, month, 1).strftime('%b'),
                'total_expenses': monthly_summary['total_expenses'],
                'total_revenue': monthly_summary['total_revenue'],
                'net_income': monthly_summary['net_income']
            })
            
        # Calculate yearly totals
        total_expenses = sum(m['total_expenses'] for m in monthly_data)
        total_revenue = sum(m['total_revenue'] for m in monthly_data)
        net_income = total_revenue - total_expenses
        savings_rate = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'year': year,
            'total_expenses': float(total_expenses),
            'total_revenue': float(total_revenue),
            'net_income': float(net_income),
            'savings_rate': float(savings_rate),
            'monthly_data': monthly_data
        }

    # --- Visualization Functions ---
    
    def plot_monthly_summary(self, year=None, month=None):
        """Plot monthly summary charts"""
        summary = self.get_monthly_summary(year, month)
        
        month_name = datetime.date(2000, summary['month'], 1).strftime('%B')
        
        # Get currency symbol
        currency = st.session_state.get('currency', '€')  # Default to Euro if not set
        currency_symbol = '€' if currency == 'EUR' else 'KSh'
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Plot 1: Income vs Expenses
        labels = ['Revenue', 'Expenses', 'Net Income']
        values = [summary['total_revenue'], summary['total_expenses'], summary['net_income']]
        colors = ['#72b58e', '#d65f5f', '#5099d4']
        
        bars = ax1.bar(labels, values, color=colors)
        ax1.set_title(f'Financial Summary for {month_name} {summary["year"]}', fontsize=16)
        ax1.set_ylabel('Amount')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{currency_symbol}{height:,.2f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=12)
        
        # Plot 2: Expense Breakdown Pie Chart
        if summary['expense_by_category']:
            categories = list(summary['expense_by_category'].keys())
            amounts = list(summary['expense_by_category'].values())
            
            # Calculate percentages
            total = sum(amounts)
            percentages = [(amount / total * 100) for amount in amounts]
            
            labels = [f'{cat} ({currency_symbol}{amt:,.2f}, {pct:.1f}%)' for cat, amt, pct in zip(categories, amounts, percentages)]
            
            ax2.pie(amounts, labels=labels, autopct='', startangle=90)
            ax2.set_title(f'Expense Breakdown for {month_name} {summary["year"]}', fontsize=16)
            ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        else:
            ax2.text(0.5, 0.5, 'No expense data for this month', 
                  horizontalalignment='center', verticalalignment='center',
                  fontsize=14)
            ax2.axis('off')
            
        plt.tight_layout()
        return fig
        
    def plot_yearly_trend(self, year=None):
        """Plot yearly financial trends"""
        yearly_summary = self.get_yearly_summary(year)
        monthly_data = yearly_summary['monthly_data']
        
        # Create DataFrame for easier plotting
        df = pd.DataFrame(monthly_data)
        
        # Get currency symbol
        currency = st.session_state.get('currency', '€')  # Default to Euro if not set
        currency_symbol = '€' if currency == 'EUR' else 'KSh'
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [2, 1]})
        
        # Plot 1: Monthly income and expenses
        ax1.plot(df['month_name'], df['total_revenue'], marker='o', linewidth=3, color='#72b58e', label='Revenue')
        ax1.plot(df['month_name'], df['total_expenses'], marker='o', linewidth=3, color='#d65f5f', label='Expenses')
        
        ax1.set_title(f'Monthly Revenue and Expenses for {yearly_summary["year"]}', fontsize=16)
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Amount')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Annotate with values
        for i, month in enumerate(df['month_name']):
            rev = df.iloc[i]['total_revenue']
            exp = df.iloc[i]['total_expenses']
            
            if rev > 0:
                ax1.annotate(f'{currency_symbol}{rev:,.0f}', 
                           xy=(month, rev),
                           xytext=(0, 10),
                           textcoords='offset points',
                           ha='center')
                           
            if exp > 0:
                ax1.annotate(f'{currency_symbol}{exp:,.0f}', 
                           xy=(month, exp),
                           xytext=(0, -15),
                           textcoords='offset points',
                           ha='center')
        
        # Plot 2: Net income bars
        bars = ax2.bar(df['month_name'], df['net_income'], 
                     color=[('#72b58e' if x >= 0 else '#d65f5f') for x in df['net_income']])
        
        ax2.set_title(f'Monthly Net Income for {yearly_summary["year"]}', fontsize=16)
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Net Income')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            label_pos = height + 50 if height >= 0 else height - 150
            ax2.annotate(f'{currency_symbol}{height:,.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, label_pos),
                       xytext=(0, 0),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        return fig
        
    def plot_category_breakdown(self, transaction_type='expenses', year=None):
        """Plot category breakdown for expenses or revenue for a year"""
        if year is None:
            year = datetime.datetime.now().year
            
        # Get currency symbol
        currency = st.session_state.get('currency', '€')  # Default to Euro if not set
        currency_symbol = '€' if currency == 'EUR' else 'KSh'
            
        # Get data
        if transaction_type == 'expenses':
            df = self.get_all_expenses()
            categories = self.expense_categories
            title = 'Expense'
            color = '#d65f5f'
        else:  # revenue
            df = self.get_all_revenue()
            categories = self.revenue_categories
            title = 'Revenue'
            color = '#72b58e'
            
        if df.empty:
            st.warning(f"No {transaction_type} data available.")
            return None
            
        # Convert date and filter by year
        df['date'] = pd.to_datetime(df['date'])
        year_data = df[df['date'].dt.year == year]
        
        if year_data.empty:
            st.warning(f"No {transaction_type} data available for {year}.")
            return None
            
        # Group by category
        category_totals = year_data.groupby('category')['amount'].sum().reset_index()
        
        # Sort by amount descending
        category_totals = category_totals.sort_values('amount', ascending=False)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Create bar chart
        bars = ax.bar(category_totals['category'], category_totals['amount'], color=color)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{currency_symbol}{height:,.2f}',
                   ha='center', va='bottom', fontsize=11)
        
        ax.set_title(f'{title} Breakdown by Category for {year}', fontsize=16)
        ax.set_xlabel('Category')
        ax.set_ylabel('Total Amount')
        plt.xticks(rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        return fig
        
    def plot_assets_breakdown(self):
        """Plot assets breakdown pie chart"""
        assets_df = self.get_all_assets()
        
        # Get currency symbol
        currency = st.session_state.get('currency', '€')  # Default to Euro if not set
        currency_symbol = '€' if currency == 'EUR' else 'KSh'
        
        if assets_df.empty:
            st.warning("No assets data available.")
            return None
            
        # Group by type
        asset_by_type = assets_df.groupby('type')['current_value'].sum().reset_index()
        
        # Calculate cash assets
        cash_data = self.get_cash_position()
        cash_total = cash_data['in_hand'] + cash_data['in_bank']
        
        # Add cash if not already included in assets
        if len(assets_df[assets_df['type'] == 'Cash']) == 0:
            # Cash is already in assets, we'll use the value from there
            # Add cash to the breakdown if it's not zero
            if cash_total > 0:
                new_row = pd.DataFrame({'type': ['Cash'], 'current_value': [cash_total]})
                asset_by_type = pd.concat([asset_by_type, new_row], ignore_index=True)
        
        # Sort by value
        asset_by_type = asset_by_type.sort_values('current_value', ascending=False)
        
        # Calculate total assets value
        total_assets = asset_by_type['current_value'].sum()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Calculate percentages
        asset_by_type['percentage'] = asset_by_type['current_value'] / total_assets * 100
        
        # Create labels with percentages
        labels = [f'{row["type"]} ({currency_symbol}{row["current_value"]:,.2f}, {row["percentage"]:.1f}%)' 
                for _, row in asset_by_type.iterrows()]
        
        # Create pie chart
        ax.pie(asset_by_type['current_value'], labels=labels, autopct='', 
              startangle=90, shadow=False)
        
        ax.set_title(f'Assets Breakdown (Total: {currency_symbol}{total_assets:,.2f})', fontsize=16)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.tight_layout()
        return fig