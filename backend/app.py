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
        
        # Handle education data (degree, institution, year)
        education_data = data.get('education', [])
        if education_data:
            processed_education = []
            for edu in education_data:
                edu_item = {
                    'degree': edu.get('degree', ''),
                    'institution': edu.get('institution', ''),
                    'year': edu.get('year', '')
                }
                # Convert year to int if it's a valid number
                try:
                    if edu_item['year']:
                        edu_item['year'] = int(edu_item['year'])
                except (ValueError, TypeError):
                    pass  # Keep as string if conversion fails
                
                processed_education.append(edu_item)
            
            employee['education'] = processed_education
        
        # Handle certification data (certificationName, certificationYear)
        certification_data = data.get('certification', [])
        if certification_data:
            processed_certification = []
            for cert in certification_data:
                cert_item = {
                    'certificationName': cert.get('certificationName', ''),
                    'certificationYear': cert.get('certificationYear', '')
                }
                # Convert year to int if it's a valid number
                try:
                    if cert_item['certificationYear']:
                        cert_item['certificationYear'] = int(cert_item['certificationYear'])
                except (ValueError, TypeError):
                    pass
                
                processed_certification.append(cert_item)
            
            employee['certification'] = processed_certification
        
        # Handle experience data (position, officeName, place, year)
        experience_data = data.get('experience', [])
        if experience_data:
            processed_experience = []
            for exp in experience_data:
                exp_item = {
                    'position': exp.get('position', ''),
                    'officeName': exp.get('officeName', ''),
                    'place': exp.get('place', ''),
                    'year': exp.get('year', '')
                }
                # Convert year to int if it's a valid number
                try:
                    if exp_item['year']:
                        exp_item['year'] = int(exp_item['year'])
                except (ValueError, TypeError):
                    pass
                
                processed_experience.append(exp_item)
            
            employee['experience'] = processed_experience
        
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
        
        # Prepare update document
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
        
        # Handle education data
        education_data = data.get('education', [])
        if education_data:
            processed_education = []
            for edu in education_data:
                edu_item = {
                    'degree': edu.get('degree', ''),
                    'institution': edu.get('institution', ''),
                    'year': edu.get('year', '')
                }
                try:
                    if edu_item['year']:
                        edu_item['year'] = int(edu_item['year'])
                except (ValueError, TypeError):
                    pass
                processed_education.append(edu_item)
            update_doc['education'] = processed_education
        
        # Handle certification data
        certification_data = data.get('certification', [])
        if certification_data:
            processed_certification = []
            for cert in certification_data:
                cert_item = {
                    'certificationName': cert.get('certificationName', ''),
                    'certificationYear': cert.get('certificationYear', '')
                }
                try:
                    if cert_item['certificationYear']:
                        cert_item['certificationYear'] = int(cert_item['certificationYear'])
                except (ValueError, TypeError):
                    pass
                processed_certification.append(cert_item)
            update_doc['certification'] = processed_certification
        
        # Handle experience data
        experience_data = data.get('experience', [])
        if experience_data:
            processed_experience = []
            for exp in experience_data:
                exp_item = {
                    'position': exp.get('position', ''),
                    'officeName': exp.get('officeName', ''),
                    'place': exp.get('place', ''),
                    'year': exp.get('year', '')
                }
                try:
                    if exp_item['year']:
                        exp_item['year'] = int(exp_item['year'])
                except (ValueError, TypeError):
                    pass
                processed_experience.append(exp_item)
            update_doc['experience'] = processed_experience
        
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