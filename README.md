Here’s the updated `README.md` without the clone instructions:

---

# Flask App with Supabase PostgreSQL Database

This application connects to a managed PostgreSQL database on Supabase. The database schema and connection details are configured using environment variables.

## Setup and Running the App

### Step 1: Set Environment Variables

Before running the Flask application, you need to define two environment variables in your PowerShell terminal.

1. **DB_SCHEMA**: This variable defines the schema you're using in your Supabase PostgreSQL database (e.g., `students_management`).
2. **DATABASE_URL**: This variable holds the connection string to your Supabase PostgreSQL database, including the password.

Run the following commands in your PowerShell terminal to set these environment variables:

```powershell
$ENV:DB_SCHEMA="students_management"
$ENV:DATABASE_URL="postgresql://postgres:EP!hulul1234@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
```

Make sure to replace the `DATABASE_URL` with your actual connection string, including the correct credentials.

### Step 2: Run the Flask Application

After setting the environment variables, you can run the Flask app with the following command:

```powershell
flask run --host=0.0.0.0 --port=5000
```

This will start the Flask app and make it accessible on `http://localhost:5000`.

## Supabase Project Details

- **Project URL**: [Supabase Project Dashboard](https://supabase.com/dashboard/project/ilglipfpynklqtsuezfv)
- **User**: `yazandac@hotmail.com`
- **Password**: `Public12345!`

Your project on Supabase will handle the database management. You can view and edit your schema and tables from the Supabase dashboard.

## Troubleshooting

- **Connection Issues**: Verify that your `DATABASE_URL` is correct. Ensure it contains the proper credentials (username, password, host, port).
- **Environment Variables**: If you're unsure if the environment variables are set correctly, you can check them by running the following in PowerShell:

  ```powershell
  echo $env:DB_SCHEMA
  echo $env:DATABASE_URL
  ```

This should return the values you set for the schema and the database URL.

## License

MIT License (or any other license you prefer).

---

This `README.md` focuses only on the steps to set the environment variables and run the app with Supabase. Let me know if you need any further modifications!