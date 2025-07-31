from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# MongoDB configuration - Fixed SSL issue
app.config["MONGO_URI"] = "mongodb+srv://vishwadilshara21:vishwa2001@cluster0.ccvm19g.mongodb.net/employees_db?retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsAllowInvalidCertificates=true"

mongo = PyMongo(app)

@app.route('/')
def home():
    # Serve the HTML file from the parent directory
    return app.send_static_file('../template/test_view.html')

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc

@app.route('/api/employees', methods=['POST'])
def create_employee():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('nic') or not data.get('name'):
            return jsonify({'error': 'NIC and Name are required fields'}), 400
        
        # Prepare employee document
        employee = {
            'nic': data.get('nic'),
            'name': {
                'firstName': data.get('name', {}).get('firstName', ''),
                'lastName': data.get('name', {}).get('lastName', '')
            },
            'address': {
                'street': data.get('address', {}).get('street', ''),
                'city': data.get('address', {}).get('city', ''),
                'state': data.get('address', {}).get('state', ''),
                'zipCode': data.get('address', {}).get('zipCode', ''),
                'country': data.get('address', {}).get('country', '')
            }
        }
        
        # Handle educational qualifications dynamically
        qualifications = data.get('educationalQualifications', [])
        if qualifications:
            # Group qualifications by type
            education_items = []
            certification_items = []
            experience_items = []
            
            for qual in qualifications:
                qual_type = qual.get('type', '').lower()
                qual_data = {
                    'degree': qual.get('degree', ''),
                    'institution': qual.get('institution', ''),
                    'year': qual.get('year', '')
                }
                
                # Convert year to int if it's a valid number
                try:
                    if qual_data['year']:
                        qual_data['year'] = int(qual_data['year'])
                except (ValueError, TypeError):
                    pass  # Keep as string if conversion fails
                
                if qual_type == 'education':
                    education_items.append(qual_data)
                elif qual_type == 'certification':
                    certification_items.append(qual_data)
                elif qual_type == 'experience':
                    experience_items.append(qual_data)
            
            # Only add non-empty arrays to the document
            educational_qualifications = {}
            if education_items:
                educational_qualifications['education'] = education_items
            if certification_items:
                educational_qualifications['certification'] = certification_items
            if experience_items:
                educational_qualifications['experience'] = experience_items
            
            # Only add educationalQualifications if there's at least one type
            if educational_qualifications:
                employee['educationalQualifications'] = educational_qualifications
        
        # Insert into MongoDB
        result = mongo.db.employees.insert_one(employee)
        
        # Return success response
        return jsonify({
            'message': 'Employee created successfully',
            'employee_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"Error creating employee: {str(e)}")
        return jsonify({'error': f'Failed to create employee: {str(e)}'}), 500

@app.route('/api/employees/<employee_id>', methods=['GET'])
def get_employee(employee_id):
    try:
        employee = mongo.db.employees.find_one({'_id': ObjectId(employee_id)})
        if employee:
            return jsonify(serialize_doc(employee)), 200
        else:
            return jsonify({'error': 'Employee not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to fetch employee: {str(e)}'}), 500

@app.route('/api/employees', methods=['GET'])
def get_all_employees():
    try:
        employees = list(mongo.db.employees.find())
        serialized_employees = [serialize_doc(emp) for emp in employees]
        return jsonify(serialized_employees), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch employees: {str(e)}'}), 500

@app.route('/api/employees/<employee_id>', methods=['PUT'])
def update_employee(employee_id):
    try:
        data = request.get_json()
        
        # Prepare update document (same logic as create)
        update_doc = {
            'nic': data.get('nic'),
            'name': {
                'firstName': data.get('name', {}).get('firstName', ''),
                'lastName': data.get('name', {}).get('lastName', '')
            },
            'address': {
                'street': data.get('address', {}).get('street', ''),
                'city': data.get('address', {}).get('city', ''),
                'state': data.get('address', {}).get('state', ''),
                'zipCode': data.get('address', {}).get('zipCode', ''),
                'country': data.get('address', {}).get('country', '')
            }
        }
        
        # Handle educational qualifications
        qualifications = data.get('educationalQualifications', [])
        if qualifications:
            education_items = []
            certification_items = []
            experience_items = []
            
            for qual in qualifications:
                qual_type = qual.get('type', '').lower()
                qual_data = {
                    'degree': qual.get('degree', ''),
                    'institution': qual.get('institution', ''),
                    'year': qual.get('year', '')
                }
                
                try:
                    if qual_data['year']:
                        qual_data['year'] = int(qual_data['year'])
                except (ValueError, TypeError):
                    pass
                
                if qual_type == 'education':
                    education_items.append(qual_data)
                elif qual_type == 'certification':
                    certification_items.append(qual_data)
                elif qual_type == 'experience':
                    experience_items.append(qual_data)
            
            educational_qualifications = {}
            if education_items:
                educational_qualifications['education'] = education_items
            if certification_items:
                educational_qualifications['certification'] = certification_items
            if experience_items:
                educational_qualifications['experience'] = experience_items
            
            if educational_qualifications:
                update_doc['educationalQualifications'] = educational_qualifications
        
        # Update in MongoDB
        result = mongo.db.employees.update_one(
            {'_id': ObjectId(employee_id)},
            {'$set': update_doc}
        )
        
        if result.matched_count:
            return jsonify({'message': 'Employee updated successfully'}), 200
        else:
            return jsonify({'error': 'Employee not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to update employee: {str(e)}'}), 500

@app.route('/api/employees/<employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        result = mongo.db.employees.delete_one({'_id': ObjectId(employee_id)})
        if result.deleted_count:
            return jsonify({'message': 'Employee deleted successfully'}), 200
        else:
            return jsonify({'error': 'Employee not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete employee: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        mongo.db.admin.command('ping')
        return jsonify({'status': 'API is running successfully', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'API running but database issue', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)