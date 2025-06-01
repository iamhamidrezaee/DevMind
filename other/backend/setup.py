import os
import subprocess
import sys
import asyncio
import time # Ensure time is imported

def print_header(title):
    """Prints a formatted header to the console."""
    print("\n" + "="*60)
    print(f"🚀 {title.center(56)} 🚀")
    print("="*60)

def run_command(command, description, can_fail=False):
    """Runs a shell command and prints its status."""
    print(f"\n🔧 Running: {description}...")
    print(f"   Command: {' '.join(command)}")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print(f"✅ Success: {description}")
            if stdout.strip():
                print(f"   Output:\n{stdout.strip()}")
        else:
            print(f"❌ Error: {description} (Return Code: {process.returncode})")
            if stdout.strip():
                print(f"   Stdout:\n{stdout.strip()}")
            if stderr.strip():
                print(f"   Stderr:\n{stderr.strip()}")
            if not can_fail:
                # sys.exit(1) # Commented out to allow script to continue for some steps
                print("   Continuing despite error as can_fail is True or commented out...")
    except FileNotFoundError:
        print(f"❌ Error: Command not found - {command[0]}. Is it installed and in your PATH?")
        if not can_fail:
            # sys.exit(1)
            print("   Continuing despite error as can_fail is True or commented out...")
    except Exception as e:
        print(f"❌ An unexpected error occurred while running '{' '.join(command)}': {e}")
        if not can_fail:
            # sys.exit(1)
            print("   Continuing despite error as can_fail is True or commented out...")

def create_env_file():
    """Creates .env file from .env.example if it doesn't exist."""
    print_header("Environment File Setup")
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("📄 Copying .env.example to .env...")
            try:
                with open(".env.example", "r", encoding='utf-8') as example_file, \
                     open(".env", "w", encoding='utf-8') as env_file:
                    env_file.write(example_file.read())
                print("✅ .env file created. Please review and update it with your configurations.")
            except Exception as e:
                print(f"❌ Error copying .env.example: {e}")
        else:
            print("⚠️ .env.example not found. Please create .env manually with necessary configurations.")
    else:
        print("✅ .env file already exists. Skipping creation.")

def install_dependencies():
    """Installs Python dependencies from requirements.txt."""
    print_header("Installing Python Dependencies")
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found. Cannot install dependencies.")
        return
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], "Install Python packages")

def start_docker_services():
    """Starts Docker services defined in docker-compose.yml."""
    print_header("Starting Docker Services (PostgreSQL & Redis)")
    if not os.path.exists("docker-compose.yml"):
        print("❌ docker-compose.yml not found. Cannot start services.")
        return
    # Attempt to stop and remove existing containers first to avoid conflicts
    run_command(["docker-compose", "down", "--remove-orphans"], "Stop and remove existing containers (if any)", can_fail=True)
    run_command(["docker-compose", "up", "-d", "postgres", "redis"], "Start PostgreSQL and Redis containers")

async def initialize_database_async():
    """Initializes the database by creating tables."""
    print_header("Initializing Database Tables (Async)")
    print("Attempting to initialize database tables...")
    try:
        # This assumes your project structure allows direct import.
        # If you run this script from `backend/`, Python should find `models.database`.
        from models.database import init_db
        await init_db()
        print("✅ Database initialization process completed (or tables already exist).")
        print("   If this was the first time, tables should be created in your 'devmind_db' PostgreSQL database.")
    except ImportError as e:
        print(f"❌ ImportError: Could not import 'init_db' from 'models.database'. {e}")
        print("   Ensure your Python path is correct and you're running from the 'backend' directory.")
        print("   Make sure 'backend/models/database.py' exists and is correctly structured.")
    except Exception as e:
        print(f"❌ Error during async database initialization: {e}")
        print("   Ensure PostgreSQL is running (docker-compose up) and accessible via DATABASE_URL in .env.")

def main():
    """Main function to run the setup process."""
    print_header("DevMind Backend Setup Utility")
    print("This script will guide you through the initial setup of the DevMind backend.")

    create_env_file()
    install_dependencies()
    start_docker_services()

    print("\n⏳ Waiting a few seconds for Docker services to initialize fully...")
    time.sleep(15) # Increased wait time for services like Postgres to be ready

    # Run async database initialization
    if sys.platform == "win32" and sys.version_info >= (3, 8): # Fix for asyncio on Windows with Python 3.8+
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Conditional import and run for database initialization
    try:
        import models.database # Test import
        asyncio.run(initialize_database_async())
    except ImportError:
        print("⚠️ Skipping database initialization due to import errors. Please check your project structure.")
    except RuntimeError as e:
        if "Event loop is closed" in str(e) and sys.platform == "win32":
            print("ℹ️  Known issue with asyncio on Windows. Trying with a new event loop.")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(initialize_database_async())
        else:
            raise

    print_header("Setup Complete!")
    print("Next steps:")
    print("1. CRITICAL: Review and update `backend/.env` with your actual credentials and API keys.")
    print("   Especially check DATABASE_URL and REDIS_URL to match your Docker setup or local instances.")
    print("2. Start the backend server: `python main.py` (from the `backend` directory)")
    print("3. Start the frontend server (usually `npm run dev` or `yarn dev` from the project root directory)")
    print("4. Open your browser and navigate to the frontend (e.g., http://localhost:3000)")
    print("\nIf you encounter issues with database connection in `main.py`:")
    print("  - Ensure PostgreSQL container is running: `docker ps` (should list devmind_postgres)")
    print("  - Check logs of the container: `docker logs devmind_postgres`")
    print("  - Verify credentials in `.env` match `docker-compose.yml`.")

if __name__ == "__main__":
    # Ensure the script is run from the 'backend' directory for correct relative imports
    if os.path.basename(os.getcwd()) != "backend":
        print("❌ This script must be run from the 'backend' directory of your project.")
        print(f"   Currently in: {os.getcwd()}")
        # sys.exit(1) # Commented out to allow execution for inspection if needed
    main()