from flask import Blueprint, render_template

events_bp = Blueprint('events', __name__)

@events_bp.route('/')
def index():
    return render_template('events/index.html')