#!/usr/bin/env python3
"""
Test script to debug Internshala scraping
"""

import requests
from bs4 import BeautifulSoup
import logging

# Test scraping Internshala directly
url = 'https://internshala.com/internships/programming-internship'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    print(f"Testing URL: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f'Response status: {response.status_code}')
    print(f'Content length: {len(response.content)}')
    
    # Look for various selectors
    selectors = [
        'div.internship_meta',
        'div.individual_internship', 
        'div.container-fluid.individual_internship',
        '.internship_meta',
        'div[class*="internship"]',
        'div[class*="individual"]',
        'h3',
        'h4',
        '.company-name'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        print(f'{selector}: {len(elements)} elements found')
        if elements and len(elements) > 0:
            print(f'  First element text: {elements[0].get_text()[:100].strip()[:50]}...')
    
    # Check if the page has any internship-like content
    text = soup.get_text().lower()
    internship_keywords = ['internship', 'stipend', 'apply', 'company']
    found_keywords = [kw for kw in internship_keywords if kw in text]
    print(f'Keywords found: {found_keywords}')
    
    # Let's also check what the actual HTML structure looks like
    print("\n--- Sample HTML structure ---")
    main_content = soup.find('main') or soup.find('div', class_='main-content') or soup.find('body')
    if main_content:
        # Find first few divs that might contain internships
        potential_cards = main_content.find_all('div')[:10]
        for i, div in enumerate(potential_cards):
            classes = div.get('class', [])
            if any('internship' in str(cls).lower() or 'individual' in str(cls).lower() for cls in classes):
                print(f"Div {i} classes: {classes}")
                print(f"Div {i} text preview: {div.get_text()[:100].strip()}")
                print("---")
    
except Exception as e:
    print(f'Error: {str(e)}')
