# main.py
import logging
from app import create_app
from flask_migrate import upgrade
from app.models import Keyword, User, Group, GroupMember, Friendship, Notification, Post, Reaction, Comment, db


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Group=Group, GroupMember=GroupMember, Keyword=Keyword, 
                Friendship=Friendship, Notification=Notification, Post=Post, Reaction=Reaction, Comment=Comment)

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database."""
    with app.app_context():
        init_db(app)
    logger.info("Initialized the database.")

@app.cli.command("verify-db")
def verify_db_command():
    """Verify the database content."""
    with app.app_context():
        users = User.query.all()
        logger.info(f"Users in database: {[(user.id, user.username, user.email) for user in users]}")


def run_migrations():
    try:
        with app.app_context():
            upgrade()
        logger.info("Database migrations completed successfully.")
    except Exception as e:
        logger.error(f"Error running database migrations: {str(e)}")

if __name__ == '__main__':
    run_migrations()
    with app.app_context():
        try:
            user = User.query.all()
            logger.info(f"Users in database: {[(user.id, user.username, user.email) for user in users]}")

        except Exception as e:
            logger.error(f"Error querying users: {str(e)}")

    app.run(debug=True)