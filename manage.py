# -*- coding: utf-8 -*-


import os
from app import create_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from ext import db


app = create_app(os.getenv('setting') or 'test')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
