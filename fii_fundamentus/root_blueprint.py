from flask import Blueprint

root_blueprint = Blueprint('root_blueprint', __name__)

@root_blueprint.route('/')
def root():
    return 'This is the / endpoint... there is nothing to do here...'
