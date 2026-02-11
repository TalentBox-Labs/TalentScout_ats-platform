# Database

This folder contains database-related files for the ATS Platform.

## Files

- **schema.sql** - PostgreSQL database schema with all tables, indexes, and triggers

## Setup

### Create Database

```bash
psql -U postgres -c "CREATE DATABASE ats_platform;"
```

### Run Schema

```bash
psql -U postgres -d ats_platform -f schema.sql
```

## Database Structure

### Tables

1. **users** - All user accounts (employers and candidates)
2. **jobs** - Job postings
3. **applications** - Job applications linking candidates to jobs
4. **candidates** - Extended candidate profile information

### Relationships

- A user can post multiple jobs (employer)
- A user can have multiple applications (candidate)
- A job can have multiple applications
- Each candidate profile is linked to a user

## Migrations

For future migrations, consider using a migration tool:
- [node-pg-migrate](https://www.npmjs.com/package/node-pg-migrate)
- [Prisma Migrate](https://www.prisma.io/docs/concepts/components/prisma-migrate)
- [TypeORM Migrations](https://typeorm.io/migrations)

## Seeds

To add seed data (sample data for development), create a `seeds.sql` file:

```sql
-- Example seed data
INSERT INTO users (email, password_hash, first_name, last_name, role)
VALUES 
  ('employer@example.com', '$2b$10$...', 'John', 'Doe', 'employer'),
  ('candidate@example.com', '$2b$10$...', 'Jane', 'Smith', 'candidate');
```

Then run:
```bash
psql -U postgres -d ats_platform -f seeds.sql
```
