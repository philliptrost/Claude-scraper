# Product Price Monitor

A web scraping tool to monitor prices of fitness equipment products across multiple websites.

## Features

- Monitors product information from:
  - Bowflex.com
  - HorizonFitness.com
  - SchwinnFitness.com

- Tracks products in categories:
  - Treadmills
  - Indoor Cycling Bikes
  - Home Gyms
  - Ellipticals and Max Trainer
  - Adjustable Dumbbells

- Extracts:
  - Product name
  - Brand
  - Category
  - MSRP (regular price)
  - Sale Price (lowest price if multiple prices present)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Using Sample Data (Recommended)

Due to bot protection on many e-commerce sites, you can use the included sample data:

```bash
python price_monitor.py --sample
```

This will load products from `sample_products.json` and display them in a formatted table.

### Attempting to Scrape Live Data

```bash
python price_monitor.py
```

**Note**: Many e-commerce websites have bot protection that may block automated scraping. If scraping fails, you can:

1. Use the `--sample` flag to see the tool in action
2. Manually gather product data and save it to `sample_products.json`
3. Explore using browser automation tools like Selenium (requires additional setup)
4. Check if the websites offer official APIs for product data

## Output

The tool displays a table with the following columns:
- **Product**: Product name
- **Brand**: Brand name (Bowflex, Horizon Fitness, Schwinn)
- **Category**: Product category
- **MSRP**: Regular/list price
- **Sale Price**: Current sale price (N/A if no sale)

## Adding More URLs

To monitor additional websites, you can extend the `PriceMonitor` class by adding new scraper methods following the pattern:

```python
def scrape_website_name(self):
    """Scrape product information from Website Name"""
    # Implementation here
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml

## Notes

- The tool respects standard web scraping practices
- Results are cached in `products.json` for later analysis
- Web scraping is subject to website structure changes
