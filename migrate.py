from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import db
from utilities.config import Configuration
from run import create_app
import sys


print('You are migrating the application in production database')
app = create_app(Configuration)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)



if __name__ == '__main__':
    manager.run()