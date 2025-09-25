# One-off migrate job (Leapcell)

Use Leapcell's one-off task runner to execute migrations after deploying a new image.

Example command in the Leapcell UI:

```bash
python manage.py migrate --noinput
```

If you want to run collectstatic as a one-off:

```bash
python manage.py collectstatic --noinput
```

It's safer to run migrations manually as a one-off rather than automatic migrations
on startup for major schema changes.
