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
    completed = db.Column(db.Boolean, nullable = False, default=False)

    # for the children model using Foreign key
    ## the foreign key by default is non null, but we can be more specific
    ## therefore, we are using 'nullable = False'
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'),nullable=False)

    def __repr__(self):
        return f'<Todo {self.id}{self.description}>'

## create a parent model
class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    completed_list = db.Column(db.Boolean, nullable = False, default=False)
    ## backref is a custom name
    todos = db.relationship('Todo', backref='list',lazy=True)


db.create_all()
db.session.commit()


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
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, completed=False, list_id=list_id)

        db.session.add(todo)
        db.session.commit()
        # add body here
        body['description'] = todo.description
        body['id'] = todo.id
        body['completed'] = todo.completed

    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
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
        print('completed', completed)
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()

    except:
        db.session.rollback()

    finally:
        db.session.close()
    
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def deleted_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()

    except:
        db.session.rollback()

    finally:
        db.session.close()
    
    return jsonify({'success':True})


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    ## new redirect?
    return render_template('index.html',
    lists=TodoList.query.all(),
    active_list=TodoList.query.get(list_id),
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all()
    )

# create a route that listen to the html todo_create
@app.route('/lists/create', methods=['POST'])
def create_list():
    # start with no error
    error = False
    # set jsonfiy object in a body
    body = {}
    # use try-except-close to control the session controller
    ## this could help handle errors
    try:
        # use the request to get the data from html
        name = request.get_json()['name']
        todolist = TodoList(name=name)
        
        db.session.add(todolist)
        db.session.commit()
        # add body here
        body['name'] = todolist.name
        body['id'] = todolist.id

    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        abort(400)
    else:
        # do not access "todo" after a session close
        # instead use a body to store "todo" value
        return jsonify(body)

@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    try:
        completed = request.get_json()['completed']
        print('completed', completed)

        list = TodoList.query.get(list_id)
        list.completed_list = completed

        for todo in list.todos:
            todo.completed = completed

        db.session.commit()

    except:
        db.session.rollback()

    finally:
        db.session.close()
    
    return redirect(url_for('index'))

@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def deleted_list(list_id):
    try:
        list = TodoList.query.get(list_id)

        for todo in list.todos:
            db.session.delete(todo)

        db.session.delete(list)
        db.session.commit()

    except:
        db.session.rollback()
        error = True

    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return jsonify({'success':True})

@app.route('/')
def index():
    return redirect(url_for('get_list_todos',list_id=1))