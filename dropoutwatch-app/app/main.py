from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('landing.html')

@main.route('/features')
def features():
    """Features page - showcase all system capabilities"""
    return render_template('features.html')

@main.route('/how-it-works')
def how_it_works():
    """How It Works page - explain the ML process"""
    return render_template('how_it_works.html')

@main.route('/technology')
def technology():
    """Technology page - tech stack and architecture"""
    return render_template('technology.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    """Contact page - same as about for now"""
    return render_template('about.html')
