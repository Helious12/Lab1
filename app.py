from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from hashlib import sha3_256

app = Flask(__name__)

# Lấy thông tin biến thể
study_group = "your_group_number"  # Điền số nhóm của bạn
fio = "Your Full Name"  # Điền họ và tên của bạn
suffix = "Высоконагруженные системы. Лабораторная работа 1"
variant = int(sha3_256(f" {study_group} {fio} {suffix}".encode('utf-8')).hexdigest(), 16) % 3 + 1
print(f"Your variant is: {variant}")

# Cấu hình cơ sở dữ liệu
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://user:password@db:5432/mydb'  # Sử dụng biến môi trường hoặc giá trị mặc định
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Tắt cảnh báo
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Định nghĩa model Task
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'description': self.description}

# Endpoint GET /tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

# Endpoint POST /tasks
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    new_task = Task(title=data['title'], description=data.get('description'))
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

# Endpoint DELETE /tasks/<id>
@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})

# (Tùy chọn) Endpoint GET /health
@app.route('/health', methods=['GET'])
def get_health():
    return jsonify({'status': 'OK'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)