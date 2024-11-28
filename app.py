from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family_tree.db'
db = SQLAlchemy(app)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
class Relationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person1_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    person2_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    relationship_type = db.Column(db.String(50), nullable=False)  # parent, child, spouse, in-law

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_person', methods=['POST'])
def add_person():
    data = request.json
    new_person = Person(name=data['name'])
    db.session.add(new_person)
    db.session.commit()
    return jsonify({'id': new_person.id, 'name': new_person.name})

@app.route('/api/add_relationship', methods=['POST'])
def add_relationship():
    data = request.json
    new_relationship = Relationship(
        person1_id=data['person1_id'],
        person2_id=data['person2_id'],
        relationship_type=data['relationship_type']
    )
    db.session.add(new_relationship)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/get_family_tree', methods=['GET'])
def get_family_tree():
    people = Person.query.all()
    relationships = Relationship.query.all()
    
    # Calculate generation levels
    generation_levels = {}
    
    def find_parents(person_id):
        return [r.person1_id for r in relationships if r.person2_id == person_id and r.relationship_type == 'parent']
        
    def find_children(person_id):
        return [r.person2_id for r in relationships if r.person1_id == person_id and r.relationship_type == 'parent']
    
    def calculate_generation(person_id, current_gen=0, visited=None):
        if visited is None:
            visited = set()
            
        if person_id in visited:
            return generation_levels.get(person_id, current_gen)
            
        visited.add(person_id)
        
        # Get all parents
        parents = find_parents(person_id)
        
        if parents:
            # If has parents, set them one level up
            for parent_id in parents:
                if parent_id not in generation_levels:
                    calculate_generation(parent_id, current_gen + 1, visited)
                elif generation_levels[parent_id] <= current_gen:
                    # Ensure parent is always above current person
                    generation_levels[parent_id] = current_gen + 1
        
        # Set current person's generation
        generation_levels[person_id] = current_gen
        
        # Process children to ensure they're below current person
        children = find_children(person_id)
        for child_id in children:
            if child_id not in generation_levels:
                calculate_generation(child_id, current_gen - 1, visited)
            elif generation_levels[child_id] >= current_gen:
                # Ensure child is always below current person
                generation_levels[child_id] = current_gen - 1
        
        return current_gen
    
    # First, process all people with no parents (root nodes)
    root_nodes = []
    for person in people:
        if not find_parents(person.id):
            root_nodes.append(person.id)
    
    # Calculate generations starting from root nodes
    for root_id in root_nodes:
        if root_id not in generation_levels:
            calculate_generation(root_id, 10)  # Start from a high number
    
    # Process remaining nodes
    for person in people:
        if person.id not in generation_levels:
            calculate_generation(person.id, 5)  # Start from middle
    
    return jsonify({
        'people': [{
            'id': p.id,
            'name': p.name,
            'generation': generation_levels.get(p.id, 0)
        } for p in people],
        'relationships': [{
            'person1_id': r.person1_id,
            'person2_id': r.person2_id,
            'type': r.relationship_type
        } for r in relationships]
    })

@app.route('/api/check_relationship', methods=['GET'])
def check_relationship():
    # Find Jeff and Douglas
    jeff = Person.query.filter_by(name='Jeff').first()
    douglas = Person.query.filter_by(name='Douglas').first()
    
    if not jeff or not douglas:
        return jsonify({'error': 'One or both persons not found'})
    
    # Check relationship
    relationship = Relationship.query.filter(
        ((Relationship.person1_id == jeff.id) & (Relationship.person2_id == douglas.id)) |
        ((Relationship.person1_id == douglas.id) & (Relationship.person2_id == jeff.id))
    ).first()
    
    if relationship:
        return jsonify({
            'person1': {'id': relationship.person1_id, 'name': Person.query.get(relationship.person1_id).name},
            'person2': {'id': relationship.person2_id, 'name': Person.query.get(relationship.person2_id).name},
            'relationship': relationship.relationship_type
        })
    else:
        return jsonify({'error': 'No direct relationship found'})

if __name__ == '__main__':
    app.run(debug=True, port=3333)
