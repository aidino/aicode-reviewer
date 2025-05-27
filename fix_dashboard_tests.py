#!/usr/bin/env python3

import re

# Read the test file
with open('tests/webapp/backend/services/test_dashboard_service.py', 'r') as f:
    content = f.read()

# Fix all test methods to be async where needed
patterns = [
    # Fix get_dashboard_summary calls
    (r'def (test_[^(]*\([^)]*\)):\s*"""[^"]*"""[^}]*service\.get_dashboard_summary\([^)]*,\s*mock_db_session\)', 
     r'async def \1:\n        """\g<2>"""\g<3>await service.get_dashboard_summary(\g<4>)'),
    
    # Fix get_health_check calls  
    (r'def (test_[^(]*\([^)]*\)):\s*"""[^"]*"""[^}]*service\.get_health_check\([^)]*mock_db_session\)',
     r'async def \1:\n        """\g<2>"""\g<3>await service.get_health_check()'),
     
    # Remove mock_db_session parameters from get_dashboard_summary calls
    (r'service\.get_dashboard_summary\(([^,)]+),\s*mock_db_session\)',
     r'await service.get_dashboard_summary(\1)'),
     
    # Remove mock_db_session parameters from get_health_check calls
    (r'service\.get_health_check\(mock_db_session\)',
     r'await service.get_health_check()'),
     
    # Fix remaining test methods that need async
    (r'def (test_[^(]*\([^)]*\)):\s*("""[^"]*"""[^}]*(?:get_dashboard_summary|get_health_check))',
     r'async def \1:\n        \2'),
]

# Apply patterns
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.MULTILINE)

# Write back
with open('tests/webapp/backend/services/test_dashboard_service.py', 'w') as f:
    f.write(content)

print("Fixed dashboard tests!") 