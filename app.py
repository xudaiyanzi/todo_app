#############################################################################
# ##### this flask and db are 'model' in MCV


##### now try to read data from database
# the abort in flask is to cancel the route handler
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__) #create the application named as 'app'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# connect this app to postsql
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yanxu@localhost:5432/todoapp'

# use SQLAlchemy to create db
db = SQLAlchemy(app)

# use migrate
migrate = Migrate(app, db)

# create db schema
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id}{self.description}>'


# db.create_all()

# present info via index.html
############################################################################
##### this route and index is a 'controller' in MCV

# create a route that listen to the html todo_create
@app.route('/todos/create', methods=['POST'])
def create_todo():
    # start with no error
    error = False
    # set jsonfiy object in a body
    body = {}
    # use try-except-close to control the session controller
    ## this could help handle errors
    try:
        # use the request to get the data from html
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        # add body here
        body['description'] = todo.description

    except:
        db.session.rollback()
        error=True
        print(sys.exc.info())
    finally:
        db.session.close()
    
    if error:
        abort(400)
    else:
        # do not access "todo" after a session close
        # instead use a body to store "todo" value
        return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()

    except:
        db.session.rollback()

    finally:
        db.session.close()
    
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def deleted_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()

    except:
        db.session.rollback()

    finally:
        db.session.close()
    
    return jsonify({'success':True})



@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.order_by('id').all())
