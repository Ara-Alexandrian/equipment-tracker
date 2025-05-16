#!/usr/bin/env python3
from app import app

with app.test_client() as client:
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Get base directory
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_path = os.path.join(base_dir, 'output', 'homepage_output.html')

    # Write the HTML to a file for inspection
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Homepage HTML has been saved to {output_path}")
    
    # Check for content after </html>
    html_end_pos = html.find('</html>')
    if html_end_pos != -1 and html_end_pos < len(html) - 7:  # 7 is length of </html>
        leftover = html[html_end_pos+7:]
        print("\nContent after </html> tag found:")
        print(leftover)