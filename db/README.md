# Database Directory

This folder contains database setup files, configuration scripts, and migration files for the various databases used in the AI-driven multi-agent self-healing cloud infrastructure project.

## Overview

The system uses multiple databases to support different data storage needs:

- **PostgreSQL**: Relational database for structured data (user data, task logs, agent interactions)
- **MongoDB**: NoSQL database for unstructured data (event logs, agent behavior records)
- **Redis**: In-memory database for caching and session management

## PostgreSQL

PostgreSQL is used for storing structured relational data such as:

- User accounts and authentication data
- Task history and logs
- Agent interaction records
- System configuration data

### Setup

1. **Install PostgreSQL**:

   ```bash
   # Using Docker
   docker run -d \
     --name postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=agent_db \
     -p 5432:5432 \
     postgres:latest
   ```

2. **Configuration Files**:

   Configuration and setup scripts are located in `/db/postgresql/`:
   - `schema.sql`: Database schema definitions
   - `migrations/`: Database migration scripts
   - `init.sql`: Initialization scripts

3. **Connect to Database**:

   ```bash
   psql -h localhost -U postgres -d agent_db
   ```

### Schema

Key tables include:

- `users`: User accounts and authentication
- `tasks`: Task history and status
- `agent_logs`: Agent activity logs
- `system_config`: System configuration

### Usage Example

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="agent_db",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM tasks WHERE status = 'completed'")
results = cursor.fetchall()
```

## MongoDB

MongoDB is used for storing unstructured and semi-structured data such as:

- Event logs from agents
- Agent behavior records
- Real-time system events
- Unstructured task data

### Setup

1. **Install MongoDB**:

   ```bash
   # Using Docker
   docker run -d \
     --name mongodb \
     -e MONGO_INITDB_ROOT_USERNAME=admin \
     -e MONGO_INITDB_ROOT_PASSWORD=admin \
     -p 27017:27017 \
     mongo:latest
   ```

2. **Configuration Files**:

   Configuration files are located in `/db/mongodb/`:
   - `collections.json`: Collection definitions
   - `indexes.js`: Index creation scripts

3. **Connect to Database**:

   ```bash
   mongo mongodb://admin:admin@localhost:27017/
   ```

### Collections

Key collections include:

- `agent_events`: Real-time events from agents
- `system_metrics`: Performance metrics
- `error_logs`: Error and exception logs
- `user_sessions`: User session data

### Usage Example

```python
from pymongo import MongoClient

client = MongoClient('mongodb://admin:admin@localhost:27017/')
db = client['agent_db']
collection = db['agent_events']

# Insert a document
collection.insert_one({
    'agent_id': 'self-healing',
    'event_type': 'failure_detected',
    'timestamp': 'YYYY-MM-DDTHH:MM:SSZ'
})

# Query documents
events = collection.find({'agent_id': 'self-healing'})
```

## Redis

Redis is used for:

- Caching frequently accessed data
- Session management
- Message queue support
- Real-time data storage

### Setup

1. **Install Redis**:

   ```bash
   # Using Docker
   docker run -d \
     --name redis \
     -p 6379:6379 \
     redis:latest
   ```

2. **Configuration Files**:

   Configuration files are located in `/db/redis/`:
   - `redis.conf`: Redis configuration
   - `cache_keys.md`: Documentation of cache key patterns

3. **Connect to Redis**:

   ```bash
   redis-cli
   ```

### Usage Example

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Set a value
r.set('agent:status:self-healing', 'active')

# Get a value
status = r.get('agent:status:self-healing')

# Set with expiration
r.setex('session:user123', 3600, 'active')
```

## Docker Compose Setup

All databases can be started together using Docker Compose:

```bash
cd ../docker/docker-compose
docker-compose up -d postgres mongodb redis
```

## Database Migrations

### PostgreSQL Migrations

Migrations are located in `/db/postgresql/migrations/`. To run migrations:

```bash
cd db/postgresql
psql -h localhost -U postgres -d agent_db -f migrations/001_initial_schema.sql
```

### MongoDB Migrations

MongoDB migrations are typically handled through scripts in `/db/mongodb/scripts/`.

## Backup and Recovery

### PostgreSQL Backup

```bash
pg_dump -h localhost -U postgres agent_db > backup.sql
```

### MongoDB Backup

```bash
mongodump --uri="mongodb://admin:admin@localhost:27017/agent_db" --out=/backup
```

### Redis Backup

Redis automatically creates snapshots, but manual backups can be created:

```bash
redis-cli BGSAVE
```

## Performance Optimization

### PostgreSQL

- Create appropriate indexes on frequently queried columns
- Use connection pooling
- Optimize queries using EXPLAIN ANALYZE

### MongoDB

- Create indexes on frequently queried fields
- Use appropriate sharding strategies for large datasets
- Monitor query performance

### Redis

- Configure appropriate memory limits
- Use Redis persistence (RDB or AOF) for data durability
- Implement cache eviction policies

## Security Considerations

1. **Credentials**: Never commit database credentials to version control
2. **Encryption**: Use encrypted connections (SSL/TLS) for database connections
3. **Access Control**: Implement proper user roles and permissions
4. **Backup Encryption**: Encrypt database backups
5. **Network Security**: Restrict database access to authorized IPs only

## Monitoring

Monitor database performance using:

- **PostgreSQL**: pg_stat_statements, pgAdmin
- **MongoDB**: MongoDB Compass, mongostat
- **Redis**: redis-cli INFO, RedisInsight

## Related Documentation

- Docker setup: `/docker/README.md`
- Configuration: `/config/README.md`
- Monitoring: `/monitoring/README.md`

