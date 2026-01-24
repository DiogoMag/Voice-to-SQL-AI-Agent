# AWS Redshift RA3 Setup Guide

This guide walks you through setting up an Amazon Redshift RA3 cluster for the Voice-to-SQL AI Agent POC.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured (optional, for CLI-based setup)
- Python 3.8+ installed
- Network access to AWS Redshift (IP whitelisting required)

## Step 1: Create Redshift RA3 Cluster

### Option A: AWS Console

1. **Navigate to Redshift Console**
   - Go to [AWS Redshift Console](https://console.aws.amazon.com/redshift/)
   - Click "Create cluster"

2. **Cluster Configuration**
   - **Cluster identifier**: Choose a unique name (e.g., `voice-sql-poc`)
   - **Node type**: Select `ra3.xlplus` or `ra3.4xlarge` (RA3 node types)
   - **Number of nodes**: Start with 1 node for POC (can scale later)
   - **Database name**: `dev` (or your preferred name)
   - **Database port**: `5439` (default)
   - **Master username**: Choose a username (e.g., `admin`)
   - **Master user password**: Set a strong password (save this!)

3. **Network and Security**
   - **VPC**: Select your VPC
   - **Subnet group**: Create or select a subnet group
   - **Publicly accessible**: 
     - For POC: Set to **Yes** (easier to connect from local machine)
     - For production: Set to **No** (use VPC peering/VPN)
   - **Availability zone**: Select an AZ in your region
   - **Security groups**: Create a new security group or use existing

4. **Additional Configuration**
   - **Encryption**: Enable encryption at rest (recommended)
   - **Backup**: Enable automated backups (recommended)
   - **Maintenance window**: Set as needed

5. **Review and Create**
   - Review all settings
   - Click "Create cluster"
   - Wait 5-15 minutes for cluster to be available

### Option B: AWS CLI

```bash
aws redshift create-cluster \
  --cluster-identifier voice-sql-poc \
  --node-type ra3.xlplus \
  --number-of-nodes 1 \
  --master-username admin \
  --master-user-password YourSecurePassword123! \
  --db-name dev \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --cluster-subnet-group-name default \
  --publicly-accessible
```

## Step 2: Configure Security Group

The security group must allow inbound connections on port 5439 from your IP address.

1. **Find Your Security Group**
   - In Redshift console, click on your cluster
   - Note the security group ID (e.g., `sg-xxxxxxxxx`)

2. **Edit Inbound Rules**
   - Go to EC2 Console → Security Groups
   - Find your Redshift security group
   - Click "Edit inbound rules"
   - Add rule:
     - **Type**: Custom TCP
     - **Port**: 5439
     - **Source**: My IP (or specific IP/CIDR range)
     - **Description**: "Redshift POC access"

3. **Alternative: Allow from Anywhere (NOT RECOMMENDED FOR PRODUCTION)**
   - Source: `0.0.0.0/0` (only for testing/POC)

## Step 3: Get Cluster Endpoint

1. In Redshift console, select your cluster
2. Find the **Endpoint** in cluster details
   - Format: `your-cluster-name.xxxxxxxxx.region.redshift.amazonaws.com`
3. Copy this endpoint - you'll need it for the config file

## Step 4: Create Database Schema

Connect to your Redshift cluster and create the required tables.

### Using SQL Workbench/J or DBeaver

1. **Connection Details**:
   - Host: Your cluster endpoint
   - Port: 5439
   - Database: `dev` (or your database name)
   - Username: Your master username
   - Password: Your master password
   - SSL: Required

2. **Run Schema Creation Script**:

```sql
-- Shopping list table
CREATE TABLE shopping_list (
  id INTEGER IDENTITY(1,1) PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  item_name VARCHAR(200) NOT NULL,
  quantity VARCHAR(50),
  added_at TIMESTAMP DEFAULT GETDATE(),
  status VARCHAR(20) DEFAULT 'pending'
);

-- Todo list table
CREATE TABLE todos (
  id INTEGER IDENTITY(1,1) PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  task VARCHAR(MAX) NOT NULL,
  due_date TIMESTAMP,
  status VARCHAR(20) DEFAULT 'open',
  created_at TIMESTAMP DEFAULT GETDATE()
);

-- Optional: Insert sample data for testing
INSERT INTO shopping_list (user_id, item_name, quantity, status) VALUES
  ('user1', 'Milk', '1 gallon', 'pending'),
  ('user1', 'Bread', '2 loaves', 'pending'),
  ('user1', 'Eggs', '1 dozen', 'completed');

INSERT INTO todos (user_id, task, due_date, status) VALUES
  ('user1', 'Buy groceries', '2026-01-25 18:00:00', 'open'),
  ('user1', 'Review project plan', '2026-01-24 12:00:00', 'open'),
  ('user1', 'Call dentist', NULL, 'completed');
```

### Using psql (PostgreSQL client)

```bash
psql -h your-cluster-endpoint.region.redshift.amazonaws.com \
     -p 5439 \
     -U admin \
     -d dev \
     -f schema.sql
```

## Step 5: Install Python Dependencies

Choose one of the following options:

### Option A: redshift-connector (Recommended - AWS Official)

```bash
pip install redshift-connector
```

**Pros:**
- Official AWS library
- Native Redshift features
- Better performance
- Active maintenance

### Option B: psycopg2-binary (PostgreSQL-compatible)

```bash
pip install psycopg2-binary
```

**Pros:**
- Works with Redshift (PostgreSQL-compatible)
- Widely used
- Good for existing PostgreSQL codebases

**Note:** The POC script (`redshift_POC.py`) automatically detects which library is installed and uses it accordingly.

### Step 5.1: Freeze Requirements

After installing the Redshift connector (or psycopg2-binary), freeze your requirements to ensure reproducible installations:

**Option A: Install from existing requirements.txt**

The project includes a `requirements.txt` file with all necessary dependencies. Install everything at once:

```bash
pip install -r requirements.txt
```

**Option B: Freeze current environment**

If you've installed packages manually and want to capture your exact environment:

```bash
# Freeze all currently installed packages
pip freeze > requirements.txt
```

**Option C: Add Redshift dependency to existing requirements.txt**

If you prefer to manually manage dependencies, add one of these lines to `requirements.txt`:

```txt
# For redshift-connector (recommended)
redshift-connector>=2.1.0

# OR for psycopg2-binary (alternative)
psycopg2-binary>=2.9.0
```

Then install:
```bash
pip install -r requirements.txt
```

**Best Practice:** Always commit `requirements.txt` to version control so others can reproduce your environment.

## Step 6: Configure Connection

Update `config/config.ini` with your Redshift cluster details:

```ini
[redshift]
host = your-cluster-name.xxxxxxxxx.region.redshift.amazonaws.com
port = 5439
user = admin
password = YourSecurePassword123!
database = dev
cluster_identifier = voice-sql-poc
```

**Important:** 
- Replace placeholder values with your actual cluster details
- Never commit passwords to version control
- Consider using environment variables or AWS Secrets Manager for production

## Step 7: Test Connection

Run the POC script to test your connection:

```bash
cd "Working POCs"
python redshift_POC.py
```

Expected output:
```
====================================================================================================
Redshift RA3 POC - Querying Todos and Shopping Lists
====================================================================================================
✓ Connected to Redshift using redshift-connector

📝 Todos (3 records):
====================================================================================================
ID    User ID         Task                                      Due Date             Status       Created
----------------------------------------------------------------------------------------------------
3     user1           Call dentist                              N/A                  completed    2026-01-23 10:00:00
2     user1           Review project plan                       2026-01-24 12:00:00  open         2026-01-23 09:00:00
1     user1           Buy groceries                             2026-01-25 18:00:00  open         2026-01-23 08:00:00

🛒 Shopping List (3 records):
====================================================================================================
ID    User ID         Item Name                      Quantity         Status       Added
----------------------------------------------------------------------------------------------------
3     user1           Eggs                           1 dozen          completed    2026-01-23 11:00:00
2     user1           Bread                          2 loaves         pending      2026-01-23 10:30:00
1     user1           Milk                            1 gallon         pending      2026-01-23 10:00:00

====================================================================================================
✓ POC completed successfully!
✓ Connection closed
```

## Troubleshooting

### Connection Timeout

**Problem:** `Connection timeout` or `Unable to connect`

**Solutions:**
1. Verify security group allows inbound traffic on port 5439 from your IP
2. Check if cluster is paused (resume it in console)
3. Verify cluster endpoint is correct
4. Ensure cluster is in "available" state (not "creating" or "modifying")
5. Check VPC routing if using private subnet

### Authentication Failed

**Problem:** `authentication failed for user`

**Solutions:**
1. Verify username and password in config.ini
2. Check if password contains special characters (may need URL encoding)
3. Ensure you're using the master username, not a database user

### SSL Connection Error

**Problem:** `SSL connection required` or `certificate verify failed`

**Solutions:**
1. Ensure SSL is enabled (required for Redshift)
2. The script uses `ssl=True` (redshift-connector) or `sslmode='require'` (psycopg2)
3. If using psycopg2, ensure you have SSL certificates installed

### Table Not Found

**Problem:** `relation "todos" does not exist`

**Solutions:**
1. Verify you're connected to the correct database
2. Run the schema creation SQL (Step 4)
3. Check table names are correct (case-sensitive in some cases)
4. Verify you have SELECT permissions on the tables

### Cluster Paused

**Problem:** Cluster is in "paused" state

**Solutions:**
1. Go to Redshift console
2. Select your cluster
3. Click "Resume cluster"
4. Wait 2-5 minutes for cluster to resume

### Cost Optimization

**For POC/Testing:**
- Use smallest RA3 node type (`ra3.xlplus`)
- Use 1 node only
- Pause cluster when not in use (saves compute costs)
- Use scheduled actions to auto-pause/resume

**Cost Estimate (US East, ra3.xlplus, 1 node):**
- Running: ~$0.85/hour (~$612/month if running 24/7)
- Paused: Storage only (~$0.024/GB/month)

## Connection String Format

### redshift-connector
```python
conn = redshift_connector.connect(
    host='your-cluster.region.redshift.amazonaws.com',
    port=5439,
    database='dev',
    user='admin',
    password='password',
    ssl=True
)
```

### psycopg2
```python
conn = psycopg2.connect(
    host='your-cluster.region.redshift.amazonaws.com',
    port=5439,
    database='dev',
    user='admin',
    password='password',
    sslmode='require'
)
```

## Next Steps

- Integrate Redshift queries into the Telegram bot pipeline
- Add connection pooling for better performance
- Implement query result caching
- Set up monitoring and alerts
- Configure automated backups
- Implement IAM authentication (more secure than password)

## Additional Resources

- [AWS Redshift Documentation](https://docs.aws.amazon.com/redshift/)
- [Redshift Connector Python Library](https://github.com/aws/amazon-redshift-python-driver)
- [Redshift Best Practices](https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices.html)
- [Redshift Security](https://docs.aws.amazon.com/redshift/latest/dg/security.html)
