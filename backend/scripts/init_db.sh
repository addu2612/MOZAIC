#!/bin/bash

# Wait for postgres
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
alembic upgrade head

echo "Database initialized"
```

**.gitignore**
```
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
*.db
*.log
.DS_Store
alembic/versions/*.pyc
celerybeat-schedule