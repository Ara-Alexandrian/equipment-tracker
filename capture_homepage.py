#!/usr/bin/env python3
from app import app

with app.test_client() as client:
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Write the HTML to a file for inspection
    with open('homepage_output.html', 'w') as f:
        f.write(html)
    
    print("Homepage HTML has been saved to homepage_output.html")
    
    # Check for content after </html>
    html_end_pos = html.find('</html>')
    if html_end_pos != -1 and html_end_pos < len(html) - 7:  # 7 is length of </html>
        leftover = html[html_end_pos+7:]
        print("\nContent after </html> tag found:")
        print(leftover)