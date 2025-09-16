# Django Migration Instructions

Since we added new models to the `data_sources` app, you'll need to create and run migrations.

## Create Migration

```bash
python manage.py makemigrations data_sources
```

This will create a migration file for the new `DocumentImport` model.

## Apply Migration

```bash
python manage.py migrate
```

This will create the database tables for the import functionality.

## Expected Migration

The migration should create a table similar to:

```sql
CREATE TABLE "data_sources_documentimport" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "created" datetime NOT NULL,
    "modified" datetime NOT NULL,
    "user_id" bigint NOT NULL,
    "document_type" varchar(50) NOT NULL,
    "original_filename" varchar(255) NOT NULL,
    "file_path" varchar(500) NOT NULL,
    "status" varchar(20) NOT NULL,
    "error_message" text NOT NULL,
    "imported_transactions_count" integer NOT NULL,
    "processing_log" text NOT NULL,
    FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") DEFERRABLE INITIALLY DEFERRED
);
```

With indexes on:
- `user_id`, `status`
- `document_type`
