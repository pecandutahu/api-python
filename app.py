#import library
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from functools import wraps

#library pendukung
import jwt
import os
import datetime

# inisialisasi object
app = Flask(__name__)
api = Api(app)
CORS(app)

#konfig db
filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///db.sqlite' 
app.config['SQLALCHEMY_DATABASE_URI'] = database
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'indonesiajuara'

#model DB auth
class AuthModel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(200))

#model Menu
class MenuModel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    parent_id = db.Column(db.Integer)
    menu_name = db.Column(db.String(100))
    link = db.Column(db.String(200))

#model ListBacth
class ListBacthModel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    batch = db.Column(db.String(100))
    microscope = db.Column(db.String(100))
    tanggal = db.Column(db.DateTime)
    operator = db.Column(db.String(100))
    status = db.Column(db.String(100))


#create model database ke db.sqlite
with app.app_context():
    db.create_all()

#decorator
def auth_token(f) :
    @wraps(f)
    def decorator(*args, **kwrgs) : 
        token = request.args.get('token')
        if not token :
            return make_response(jsonify({'msg' : 'Token is missing' }), 401)
        try : 
            jwt.decode(token, app.config['SECRET_KEY'], algorithms = ['HS256'])
        except : 
            return make_response(jsonify({'error' : 'Invalid token' }), 401)
        return f(*args, **kwrgs)
    return decorator

class Register(Resource) :

    def post(self) :
        dataUsername = request.json.get('username')
        dataPassword = request.json.get('password')

        if dataUsername and dataPassword :
            
            user = AuthModel.query.filter_by(username = dataUsername).first()

            if user : 
                return make_response(jsonify({"error": "Username exist"}), 401)
            data = AuthModel(username=dataUsername, password = generate_password_hash(dataPassword, method = 'sha256'))
            db.session.add(data)
            db.session.commit()
            return make_response(jsonify({"msg": "Registration Success"}), 200)
        return make_response(jsonify({"error": "Registration failed"}), 401)
        
#class routing login
class Login(Resource) :
    def post(self) :
        dataUsername = request.json.get('username')
        dataPassword = request.json.get('password')
        user = AuthModel.query.filter_by(username = dataUsername).first()

        if user :
            if check_password_hash(user.password, dataPassword) :
                token = jwt.encode({'username' : dataUsername, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours = 8)}, app.config['SECRET_KEY'], algorithm="HS256")
                return jsonify({"msg": "Login Succesfull", 'token' : token, 'email' : dataUsername,  'id' : user.id, 'response' : []})
        return make_response(jsonify({"msg": "Login Failed"}))

class Menus(Resource) :
    @auth_token
    def post(self) :
        menu_name = request.form.get('menu_name')
        link = request.form.get('link')
        data = MenuModel(menu_name=menu_name, link = link)
        db.session.add(data)
        db.session.commit()
        return jsonify({"msg": "Input menu Succesfull"})
    
    @auth_token
    def get(self) : 
        menus = MenuModel.query.all()
        result = [{
            'menu_name' : data.menu_name,
            'link' : data.link,
        } for data in menus]
        return make_response(jsonify(result), 200)
        
class ListBatch(Resource) :
    @auth_token
    def get(self) : 

        result = [
            {
                'batch' : 30849344545,
                'microscope' : 1.2,
                'tanggal' : '04/04/2023 14:30:30',
                'operator' : 'jhondoe',
                'status' : 'Terjadwal'
            },
            {
                'batch' : 43744484774,
                'microscope' : 1,
                'tanggal' : '04/04/2023 14:30:29',
                'operator' : 'jhon doe',
                'status' : 'on Going'
            },
            {
                'batch' : 54657767677,
                'microscope' : 2,
                'tanggal' : '04/04/2023 12:30:30',
                'operator' : 'Asep',
                'status' : 'CPE 1'
            },
            {
                'batch' : 6765656645,
                'microscope' : 2,
                'tanggal' : '04/04/2023 08:30:30',
                'operator' : 'Chandra',
                'status' : 'CPE 4'
            },
            {
                'batch' : 4334344334,
                'microscope' : 1,
                'tanggal' : '04/04/2023 07:30:30',
                'operator' : 'Steven',
                'status' : 'Selesai'
            },
        ]
        return make_response(jsonify(result), 200)
    
class ErrorReport(Resource) : 
    @auth_token
    def get(self) :
        data = [
            {
                'microscope' : 1,
                'tanggal' : 'February 2023',
                'error_count' : '2',
            },

        ]
        return make_response(jsonify(data), 200)
class Summary(Resource) : 
    @auth_token
    def get(self) :
        data = [
            {
                'date' : 'February 2023',
                'microscope' : 1,
                'all_report' : 41,
                'approve' : 50,
                'reject' : 45
            }
        ]
        return make_response(jsonify(data), 200)
    
class Captures (Resource) :
    @auth_token
    def get(self) :
        data = [
            {
                'microscope' : 1,
                'captures' : [
                    {
                        'batch' : '4384474947',
                        'region' : 'Region 2',
                        'status' : 'CPE 4 90%',
                        'tanggal' : '04 Apr 2023 14:30'
                    },
                    {
                        'batch' : '3493484848',
                        'region' : 'Region 1',
                        'status' : 'CPE 3 90%',
                        'tanggal' : '03 Apr 2023 14:30'
                    },
                    {
                        'batch' : '3545466666',
                        'region' : 'Region 2',
                        'status' : 'CPE 4 90%',
                        'tanggal' : '02 Apr 2023 14:30'
                    },
                    {
                        'batch' : '7555655666',
                        'region' : 'Region 2',
                        'status' : 'CPE 4 80%',
                        'tanggal' : '01 Apr 2023 14:30'
                    },
                    {
                        'batch' : '4584855588',
                        'region' : 'Region 1',
                        'status' : 'CPE 3 70%',
                        'tanggal' : '30 Mar 2023 14:30'
                    },
                ]
            }
        ]
        return make_response(jsonify(data), 200)

class ServerStatus (Resource) : 
    @auth_token
    def get(self) : 
        data = [
            {
                'server_name' : 'GCP / Engine AI',
                'status' : 'Online'
            },
            {
                'server_name' : 'AI',
                'status' : 'Offline'
            },
            {
                'server_name' : 'Mini Pc',
                'status' : 'Online'
            },
            {
                'server_name' : 'Auto Fokus',
                'status' : 'Online'
            },
            {
                'server_name' : 'Sliders',
                'status' : 'Online'
            },
        ]
        return make_response(jsonify(data), 200)

class LatestReport(Resource) : 
    @auth_token
    def get(self) : 
        data = [
            {
                'ID' : 1,
                'kategori_cpe' : 'CPE 4 - CPE 1',
                'date' : '04 Apr 2023 14:30',
                'user' : 'johndoe',
                'desc' : 'Kemungkinan CPE ini bukan CPE 4 tetapi CPE ini adalah CPE 1'
            },
            {
                'ID' : 2,
                'kategori_cpe' :'CPE 4 - CPE 1',
                'date' : '04 Apr 2023 14:30',
                'user' : 'johndoe',
                'desc' : 'Kemungkinan CPE ini bukan CPE 4 tetapi CPE ini adalah CPE 1'
            },
        ]
        return make_response(jsonify(data), 200)
    
class AuditLog(Resource) :
    @auth_token
    def get(self) :
        data = [
            {
                'ID' : 1,
                'profile' : '#',
                'date' : '04 Apr 2023 14:30',
                'user' : 'johndoe',
                'activity' : 'Add new batch',
                'desc' : 'New Batch'
            },
            {
                'ID' : 2,
                'profile' : '#',
                'date' : '03 Apr 2023 14:30',
                'user' : 'johndoe',
                'activity' : 'Create Dataset',
                'desc' : 'Data set telah disiapkan sebanyak 10 buah, periode 12 September 2023 sd 13 September 2023'
            },
        ]
        return make_response(jsonify(data), 200)

#inisiasi resource api 
api.add_resource(Register,"/api/register", methods=['POST'])
api.add_resource(Login,"/api/login", methods=['POST'])
api.add_resource(Menus,"/api/menu", methods=['GET', 'POST'])
api.add_resource(ListBatch,"/api/listbatch", methods=['GET'])
api.add_resource(ErrorReport,"/api/errorreport", methods=['GET'])
api.add_resource(Summary,"/api/summary", methods=['GET'])
api.add_resource(Captures,"/api/captures", methods=['GET'])
api.add_resource(ServerStatus,"/api/serverstatus", methods=['GET'])
api.add_resource(LatestReport,"/api/latestreport", methods=['GET'])
api.add_resource(AuditLog,"/api/auditlog", methods=['GET'])

#run apps
if __name__ == "__main__" : 
    app.run(debug=True)
