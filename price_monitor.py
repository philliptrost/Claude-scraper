#!/usr/bin/env python3
"""
Product Price Monitoring Tool
Scrapes product information from fitness equipment websites
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin
import sys
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PriceMonitor:
    """Main class for monitoring product prices across multiple websites"""

    def __init__(self):
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # More realistic headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

        self.categories = [
            'Treadmills',
            'Indoor Cycling Bikes',
            'Home Gyms',
            'Ellipticals and Max Trainer',
            'Adjustable Dumbbells'
        ]
        self.products = []

    def fetch_page(self, url: str, delay: float = 2.0) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page with retry logic"""
        try:
            if not url.startswith('http'):
                url = 'https://' + url

            # Add delay to avoid rate limiting
            time.sleep(delay)

            response = self.session.get(url, headers=self.headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"Access denied (403) for {url}. Website may have bot protection.", file=sys.stderr)
            else:
                print(f"HTTP error fetching {url}: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            return None

    def extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None

        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', price_text.replace(',', ''))
        if price_match:
            return float(price_match.group(1).replace(',', ''))
        return None

    def scrape_bowflex(self):
        """Scrape product information from Bowflex website"""
        print("Scraping Bowflex.com...")
        base_url = "https://www.bowflex.com"

        # Try to find category pages
        category_urls = {
            'Treadmills': f"{base_url}/treadmills/",
            'Indoor Cycling Bikes': f"{base_url}/bikes/",
            'Home Gyms': f"{base_url}/strength/",
            'Adjustable Dumbbells': f"{base_url}/selecttech/",
            'Ellipticals and Max Trainer': f"{base_url}/max-trainer/"
        }

        for category, url in category_urls.items():
            soup = self.fetch_page(url)
            if not soup:
                continue

            # Look for product listings - common patterns
            products = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card', re.I))

            for product in products[:10]:  # Limit to first 10 products per category
                try:
                    # Extract product name
                    name_elem = product.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|product', re.I))
                    if not name_elem:
                        name_elem = product.find('a')

                    if not name_elem:
                        continue

                    product_name = name_elem.get_text(strip=True)

                    # Extract prices
                    price_elems = product.find_all(['span', 'div', 'p'], class_=re.compile(r'price', re.I))
                    prices = []

                    for price_elem in price_elems:
                        price_text = price_elem.get_text(strip=True)
                        price = self.extract_price(price_text)
                        if price:
                            prices.append(price)

                    if prices:
                        msrp = max(prices)
                        sale_price = min(prices)

                        self.products.append({
                            'Product': product_name,
                            'Brand': 'Bowflex',
                            'Category': category,
                            'MSRP': msrp if len(prices) > 1 else msrp,
                            'Sale Price': sale_price if len(prices) > 1 else None
                        })
                except Exception as e:
                    continue

    def scrape_horizon(self):
        """Scrape product information from Horizon Fitness website"""
        print("Scraping HorizonFitness.com...")
        base_url = "https://www.horizonfitness.com"

        category_urls = {
            'Treadmills': f"{base_url}/treadmills",
            'Indoor Cycling Bikes': f"{base_url}/bikes",
            'Ellipticals and Max Trainer': f"{base_url}/ellipticals"
        }

        for category, url in category_urls.items():
            soup = self.fetch_page(url)
            if not soup:
                continue

            products = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card', re.I))

            for product in products[:10]:
                try:
                    name_elem = product.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|product', re.I))
                    if not name_elem:
                        name_elem = product.find('a')

                    if not name_elem:
                        continue

                    product_name = name_elem.get_text(strip=True)

                    price_elems = product.find_all(['span', 'div', 'p'], class_=re.compile(r'price', re.I))
                    prices = []

                    for price_elem in price_elems:
                        price_text = price_elem.get_text(strip=True)
                        price = self.extract_price(price_text)
                        if price:
                            prices.append(price)

                    if prices:
                        msrp = max(prices)
                        sale_price = min(prices)

                        self.products.append({
                            'Product': product_name,
                            'Brand': 'Horizon Fitness',
                            'Category': category,
                            'MSRP': msrp if len(prices) > 1 else msrp,
                            'Sale Price': sale_price if len(prices) > 1 else None
                        })
                except Exception as e:
                    continue

    def scrape_schwinn(self):
        """Scrape product information from Schwinn Fitness website"""
        print("Scraping SchwinnFitness.com...")
        base_url = "https://www.schwinnfitness.com"

        category_urls = {
            'Treadmills': f"{base_url}/treadmills",
            'Indoor Cycling Bikes': f"{base_url}/bikes",
            'Ellipticals and Max Trainer': f"{base_url}/ellipticals"
        }

        for category, url in category_urls.items():
            soup = self.fetch_page(url)
            if not soup:
                continue

            products = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card', re.I))

            for product in products[:10]:
                try:
                    name_elem = product.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|product', re.I))
                    if not name_elem:
                        name_elem = product.find('a')

                    if not name_elem:
                        continue

                    product_name = name_elem.get_text(strip=True)

                    price_elems = product.find_all(['span', 'div', 'p'], class_=re.compile(r'price', re.I))
                    prices = []

                    for price_elem in price_elems:
                        price_text = price_elem.get_text(strip=True)
                        price = self.extract_price(price_text)
                        if price:
                            prices.append(price)

                    if prices:
                        msrp = max(prices)
                        sale_price = min(prices)

                        self.products.append({
                            'Product': product_name,
                            'Brand': 'Schwinn',
                            'Category': category,
                            'MSRP': msrp if len(prices) > 1 else msrp,
                            'Sale Price': sale_price if len(prices) > 1 else None
                        })
                except Exception as e:
                    continue

    def load_from_file(self, filename: str = "sample_products.json"):
        """Load products from a JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.products.extend(data)
                print(f"Loaded {len(data)} products from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found")
        except Exception as e:
            print(f"Error loading from {filename}: {e}")

    def run(self, use_sample_data: bool = False):
        """Run the price monitor for all websites"""
        if use_sample_data:
            print("Loading sample data instead of scraping...")
            self.load_from_file("sample_products.json")
        else:
            self.scrape_bowflex()
            self.scrape_horizon()
            self.scrape_schwinn()

            # If no products found due to bot protection, suggest using sample data
            if not self.products:
                print("\n⚠️  No products were scraped (likely due to bot protection).")
                print("You can:")
                print("  1. Provide product data in 'sample_products.json'")
                print("  2. Use the '--sample' flag to load example data")
                print("  3. Manually browse the websites and add URLs to the script")

    def format_price(self, price: Optional[float]) -> str:
        """Format price for display"""
        if price is None:
            return "N/A"
        return f"${price:,.2f}"

    def display_results(self):
        """Display results in a formatted table"""
        if not self.products:
            print("\nNo products found.")
            return

        # Print table header
        print("\n" + "="*100)
        print(f"{'Product':<40} {'Brand':<20} {'Category':<25} {'MSRP':<12} {'Sale Price':<12}")
        print("="*100)

        # Print each product
        for product in self.products:
            product_name = product['Product'][:38] + '..' if len(product['Product']) > 40 else product['Product']
            brand = product['Brand']
            category = product['Category'][:23] + '..' if len(product['Category']) > 25 else product['Category']
            msrp = self.format_price(product['MSRP'])
            sale_price = self.format_price(product['Sale Price'])

            print(f"{product_name:<40} {brand:<20} {category:<25} {msrp:<12} {sale_price:<12}")

        print("="*100)
        print(f"\nTotal products found: {len(self.products)}")

    def save_to_json(self, filename: str = "products.json"):
        """Save products to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.products, f, indent=2)
        print(f"\nResults saved to {filename}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor fitness equipment prices')
    parser.add_argument('--sample', action='store_true',
                        help='Use sample data instead of scraping')
    args = parser.parse_args()

    monitor = PriceMonitor()
    print("Starting Product Price Monitor...")
    print("-" * 50)

    monitor.run(use_sample_data=args.sample)
    monitor.display_results()

    if monitor.products:
        monitor.save_to_json()


if __name__ == "__main__":
    main()
