from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import traceback
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family_tree.db'
db = SQLAlchemy(app)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date)

class Relationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person1_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    person2_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    relationship_type = db.Column(db.String(50), nullable=False)

with app.app_context():
    # Drop all tables first
    db.drop_all()
    # Create all tables
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_person', methods=['POST'])
def add_person():
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400

        birthday = None
        if data.get('birthday'):
            try:
                birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid birthday format. Use YYYY-MM-DD'}), 400

        new_person = Person(name=data['name'], birthday=birthday)
        db.session.add(new_person)
        db.session.commit()

        return jsonify({
            'id': new_person.id,
            'name': new_person.name,
            'birthday': new_person.birthday.strftime('%Y-%m-%d') if new_person.birthday else None
        })
    except Exception as e:
        db.session.rollback()
        print('Error adding person:', str(e))
        traceback.print_exc()
        return jsonify({'error': 'Server error while adding person'}), 500

@app.route('/api/add_relationship', methods=['POST'])
def add_relationship():
    try:
        data = request.json
        if not data or 'person1_id' not in data or 'person2_id' not in data or 'relationship_type' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        new_relationship = Relationship(
            person1_id=data['person1_id'],
            person2_id=data['person2_id'],
            relationship_type=data['relationship_type']
        )
        db.session.add(new_relationship)
        db.session.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        print('Error adding relationship:', str(e))
        traceback.print_exc()
        return jsonify({'error': 'Server error while adding relationship'}), 500

@app.route('/api/get_family_tree', methods=['GET'])
def get_family_tree():
    try:
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
        
        people_data = [{
            'id': person.id,
            'name': person.name,
            'birthday': person.birthday.strftime('%Y-%m-%d') if person.birthday else None,
            'generation': generation_levels.get(person.id, 0)
        } for person in people]
        
        relationship_data = [{
            'person1_id': rel.person1_id,
            'person2_id': rel.person2_id,
            'relationship_type': rel.relationship_type
        } for rel in relationships]
        
        return jsonify({
            'people': people_data,
            'relationships': relationship_data
        })
    except Exception as e:
        print('Error getting family tree:', str(e))
        traceback.print_exc()
        return jsonify({'error': 'Server error while getting family tree'}), 500

@app.route('/api/check_relationship', methods=['GET'])
def check_relationship():
    try:
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
    except Exception as e:
        print('Error checking relationship:', str(e))
        traceback.print_exc()
        return jsonify({'error': 'Server error while checking relationship'}), 500

@app.route('/api/delete_person/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    try:
        # First delete all relationships involving this person
        Relationship.query.filter(
            (Relationship.person1_id == person_id) | 
            (Relationship.person2_id == person_id)
        ).delete()
        
        # Then delete the person
        person = Person.query.get(person_id)
        if person:
            db.session.delete(person)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Person not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update_person/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    try:
        person = Person.query.get(person_id)
        if not person:
            return jsonify({'success': False, 'error': 'Person not found'}), 404

        data = request.get_json()
        if 'name' in data:
            person.name = data['name']
        if 'birthday' in data:
            person.birthday = data['birthday']

        db.session.commit()
        return jsonify({
            'success': True, 
            'person': {
                'id': person.id,
                'name': person.name,
                'birthday': person.birthday
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3333)
