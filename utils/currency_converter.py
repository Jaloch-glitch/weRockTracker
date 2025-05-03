import requests
import json
import datetime
import os
import streamlit as st

# We'll use a free currency exchange API from fawazahmed0's exchange-api
# This API doesn't require authentication and has no rate limits

class CurrencyConverter:
    def __init__(self):
        # Base URL for the API
        self.base_url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/"
        
        # Cache exchange rates to avoid repeated API calls
        self.rates_cache = {}
        self.cache_expiry = datetime.timedelta(hours=1)  # Refresh rates every hour
        self.last_updated = {}
    
    def get_exchange_rate(self, from_currency, to_currency):
        """
        Get the exchange rate from one currency to another
        
        Args:
            from_currency: The source currency code (e.g., 'EUR')
            to_currency: The target currency code (e.g., 'KES')
            
        Returns:
            float: The exchange rate (from_currency to to_currency)
        """
        from_currency = from_currency.lower()
        to_currency = to_currency.lower()
        
        # Check if we have a cached rate that's still valid
        cache_key = f"{from_currency}_{to_currency}"
        now = datetime.datetime.now()
        
        if (cache_key in self.rates_cache and 
            cache_key in self.last_updated and 
            now - self.last_updated[cache_key] < self.cache_expiry):
            return self.rates_cache[cache_key]
        
        # If not in cache or expired, fetch from API
        try:
            # Construct the API URL
            url = f"{self.base_url}currencies/{from_currency}/{to_currency}.json"
            
            # Make the API request
            response = requests.get(url)
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                rate = data.get(to_currency)
                
                # Cache the result
                self.rates_cache[cache_key] = rate
                self.last_updated[cache_key] = now
                
                return rate
            else:
                # If API request fails, use fallback rates
                return self.get_fallback_rate(from_currency, to_currency)
                
        except Exception as e:
            # If any error occurs (network issues, etc.), use fallback rates
            return self.get_fallback_rate(from_currency, to_currency)
    
    def convert(self, amount, from_currency, to_currency):
        """
        Convert an amount from one currency to another
        
        Args:
            amount: The amount to convert
            from_currency: The source currency code (e.g., 'EUR')
            to_currency: The target currency code (e.g., 'KES')
            
        Returns:
            float: The converted amount
        """
        # If currencies are the same, return the original amount
        if from_currency.lower() == to_currency.lower():
            return amount
        
        # Get the exchange rate
        rate = self.get_exchange_rate(from_currency, to_currency)
        
        # Convert the amount
        converted_amount = amount * rate
        
        return converted_amount
    
    def get_fallback_rate(self, from_currency, to_currency):
        """
        Provides fallback exchange rates when API is unavailable
        
        Args:
            from_currency: The source currency code (e.g., 'EUR')
            to_currency: The target currency code (e.g., 'KES')
            
        Returns:
            float: A fallback exchange rate
        """
        # Fixed fallback rates for EUR to KES and KES to EUR
        # These are approximations and should be updated periodically
        fallback_rates = {
            "eur_kes": 140.0,  # 1 EUR = 140 KES (approximate)
            "kes_eur": 0.00714  # 1 KES = 0.00714 EUR (approximate)
        }
        
        # Normalize currencies to lowercase
        from_currency = from_currency.lower()
        to_currency = to_currency.lower()
        
        # Return the appropriate fallback rate
        if from_currency == "eur" and to_currency == "kes":
            return fallback_rates["eur_kes"]
        elif from_currency == "kes" and to_currency == "eur":
            return fallback_rates["kes_eur"]
        else:
            # For other currency pairs (which shouldn't occur in our app),
            # return 1.0 as a fallback (no conversion)
            return 1.0

# Initialize the currency converter
converter = CurrencyConverter()

def get_currency_symbol(currency_code):
    """
    Get the currency symbol for a currency code
    
    Args:
        currency_code: The currency code (e.g., 'EUR', 'KES')
        
    Returns:
        str: The currency symbol
    """
    symbols = {
        "EUR": "€",
        "KES": "KSh"
    }
    return symbols.get(currency_code, currency_code)

def format_currency(amount, currency_code):
    """
    Format a currency amount with the appropriate symbol
    
    Args:
        amount: The amount to format
        currency_code: The currency code (e.g., 'EUR', 'KES')
        
    Returns:
        str: The formatted currency string
    """
    symbol = get_currency_symbol(currency_code)
    return f"{symbol}{amount:,.2f}"

def convert_and_format(amount, from_currency, to_currency):
    """
    Convert an amount and format it with the appropriate currency symbol
    
    Args:
        amount: The amount to convert
        from_currency: The source currency code (e.g., 'EUR')
        to_currency: The target currency code (e.g., 'KES')
        
    Returns:
        str: The formatted converted amount
    """
    converted = converter.convert(amount, from_currency, to_currency)
    return format_currency(converted, to_currency)