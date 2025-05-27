import re

# Read file
with open('tests/webapp/backend/services/test_dashboard_service.py', 'r') as f:
    content = f.read()

# Replace ALL remaining service calls
content = re.sub(r'result = service\.get_dashboard_summary\(([^,)]+),\s*mock_db_session\)', r'result = await service.get_dashboard_summary(\1)', content)
content = re.sub(r'result = service\.get_health_check\(mock_db_session\)', r'result = await service.get_health_check()', content)

# Replace variable assignments
content = re.sub(r'(\w+_result) = service\.get_dashboard_summary\(([^,)]+),\s*mock_db_session\)', r'\1 = await service.get_dashboard_summary(\2)', content)

# Make ALL test methods async if they aren't already and contain await
lines = content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    if line.strip().startswith('def test_') and 'async def test_' not in line:
        # Check next 30 lines for await
        next_lines = '\n'.join(lines[i:i+30])
        if 'await service.' in next_lines:
            line = line.replace('def test_', 'async def test_')
    new_lines.append(line)

content = '\n'.join(new_lines)

# Write back
with open('tests/webapp/backend/services/test_dashboard_service.py', 'w') as f:
    f.write(content)

print('Fixed all remaining tests!') 