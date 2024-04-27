from flask import *
import pyrebase
import uuid, os, time
from werkzeug.utils import secure_filename
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

config = {
  "apiKey": "AIzaSyAk0fgnZDbOxpCxhoGbKQ83aUJ2D-bj-Mg",
  "authDomain": "bale-house-rental.firebaseapp.com",
  "projectId": "bale-house-rental",
  "storageBucket": "bale-house-rental.appspot.com",
  "messagingSenderId": "964518277159",
  "appId": "1:964518277159:web:ba653f98b873ea9d961e02",
  "measurementId": "G-T9899TTSBL",
  "databaseURL":"https://bale-house-rental-default-rtdb.firebaseio.com"
}

firebase = pyrebase.initialize_app(config)

cred = credentials.Certificate("bale-house-rental-firebase-adminsdk-b9crh-7da5e2aded.json")
firebase_admin.initialize_app(cred, {"databaseURL":"https://bale-house-rental-default-rtdb.firebaseio.com"})

real_db = firebase.database()
fire_storage = firebase.storage()
app = Flask(__name__)
app.secret_key='ambe@1221'

ALLOWED_IMAGE = {'png','jpeg','jpg','apk','jfif'}

app.config['UPLOAD_FOLDER'] = 'sends'
app.config['MAX_CONTENT_LENGTH']  = 128*1024*1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_IMAGE


@app.route('/')
def index():
    houses_data = real_db.child('House').get().val()
    houses = []
    if houses_data:
         for house_id, house_data in houses_data.items():
                image_urls = [house_data['house_images'].get(f'image_{i}', '') for i in range(1, 4)]
                # Append each house data to the list
                houses.append({
                    'id': house_id,
                    'rent': house_data.get('type_of_property',''),  # Assuming all houses are for rent
                    'price': house_data.get('house_price', ''),
                    'building-name': house_data.get('building_name',''),
                    'propertyType': house_data.get('property_type',''),
                    'title': house_data.get('description', ''),
                    'owner':house_data.get('user_name',''),
                    'location': house_data.get('house_street', ''),
                    'beds': house_data.get('bed_number', ''),
                    'baths': house_data.get('toilet_number', ''),
                    'area': house_data.get('area', ''),
                    'image_urls': image_urls
                })
    return render_template('index.html', houses=houses)
 
# ======================================= register ======================================================
@app.route('/register.html', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        developer_name = request.form['developer_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
             developer_data ={
               "name":developer_name,
               "email":email,
               "phone_number":phone_number,
               "address":address,
               "password":password
            }
             email_key = email.replace('.','_dot_')
             real_db.child('Users').child(phone_number).set(developer_data)
             return redirect(url_for('login'))
        else:
            return redirect(url_for('register'))
    return render_template('register.html')

# =============================== login =================================
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        password = request.form['password']
        is_admin = request.form.get('admin')
        
      
        user = real_db.child('Users').child(phone_number).get().val()

        if user:
            if password == user.get('password'):
                    session['user_name'] = user.get('name')
                    session['user_phone'] = phone_number
                    session['user_email'] = user.get('email')
                    return redirect(url_for('index'))
            else:
                    return 'Incorrect password for user'
        else:
                return 'User not found. Please register first'
    
    return render_template('login.html')


#================================ add property ===========================
@app.route("/addProperty.html", methods=['GET', 'POST'])
def addProperty():
    user_name = ""
    user_email=""
    user_phone=""

    user_name = session.get('user_name','')
    user_phone = session.get('user_phone','')
    user_email = session.get('user_email','')

    if user_phone != "":

        if request.method == 'POST':
            location = request.form['location']
            price = request.form['price']
            house_street  = request.form.get('house_street')
            area = request.form['area']
            description = request.form['description']
            property_type = request.form.get('property_type')
            type_of_property = request.form.get('type_of_property')

            house_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%m-%d-%y %H:%M:%S")

            if property_type == 'living':
                  bed_number = request.form.get('bed_number')
                  kitchen_number = request.form.get('kitchen_number')
                  property_subtype = request.form.get('property_subtype')
                  real_db.child('Waiting').child(house_id).set({
                    "user_name": user_name,
                    "user_phone":user_phone,
                    "user_email":user_email,
                    "location": location,
                    "house_street":house_street,
                    "house_price":price,
                    "area":area,
                    "property_type": property_type,
                    "description":description,
                    "timestamp":timestamp,
                    "house_id":house_id,
                    "bed_number": bed_number,
                    "kitchen_number":kitchen_number,
                    "property_subtype": property_subtype,
                    "type_of_property": type_of_property
                 }) 
            elif property_type == 'business' or property_type == 'office':
                 floor_number = request.form.get('floor_number')
                 building_name = request.form.get('building_name')  
                 real_db.child('Waiting').child(house_id).set({
                        "floor_number": floor_number,
                        "building_name":building_name,
                        "user_name": user_name,
                        "user_phone":user_phone,
                        "user_email":user_email,
                        "location": location,
                        "house_street":house_street,
                        "house_price":price,
                        "area":area,
                        "property_type": property_type,
                        "description":description,
                        "timestamp":timestamp,
                        "house_id":house_id,
                        "floor_number":floor_number,
                        "building_name": building_name,
                       "type_of_property": type_of_property
                 })          
           

            house_image = request.files.getlist('house_image')
            for idx, image in enumerate(house_image):
                if allowed_file(image.filename):
                    image_filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"image_{idx+1}_{house_id}.jpg")
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    image.save(image_path)

                    image_storage_path  = f"{house_id}/house_Images/{image_filename}"
                    fire_storage.child(image_storage_path).put(image_path)
                    image_url = fire_storage.child(image_storage_path).get_url(None)


                    real_db.child("Waiting").child(house_id).child("house_images").child(f"image_{idx+1}").set(image_url)
                    time.sleep(1)
                    os.remove(image_path)
            # image = real_db.child("waiting").child(house_id).child("house_images").get().val()
            # real_db.child("waiting").child(house_id).child("house_images").set(image)
    else:
       return redirect(url_for('login'))
    return render_template('addProperty.html')

#============================================== end of add property ==================================================

# ============================================= fetching houses from the waiting node in the admin page =============================
@app.route('/modals.html')
def admin():
      response = real_db.child('Waiting').get()

      houses = {}
      if response:
           data = response.val()
           if data:
                for house_id, house_data in data.items():
                        house_data['additional_images'] = list(house_data.get('house_images', {}).values())
                        houses[house_id] = house_data

      return render_template('modals.html', houses=houses)
# ============================================= end of fetching houses from the waiting node in the admin page =============================

# ============================================= Approval logic ===============================================================
@app.route('/approve-house', methods=['GET','POST'])
def approve_house():
     if request.method == 'POST':
        house_id =  request.form['house_id']
        house_data = real_db.child('Waiting').child(house_id).get().val()
        real_db.child('House').child(house_id).set(house_data)
        real_db.child('Waiting').child(house_id).remove()
        return redirect(url_for('admin'))



#============================================== Admin login start ====================================================

@app.route('/adminLogin.html', methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'POST':
        admin_phone = request.form['phone_number']
        password = request.form['password']
        admin = real_db.child('Admin').child(admin_phone).get().val()
        if admin:
                if password == admin.get('password'):
                    session['admin_name'] = admin.get('name')
                    session['admin_phone'] = admin.get('phone')
                    # session['user_email'] = admin.get('email')
                    return redirect(url_for('DashBoard'))
                else:
                    return 'Incorrect password for admin'
        else:
            return 'Admin not found'
       
    
    return render_template('adminLogin.html')

@app.route('/allProperties.html', methods=['GET','POST'])
def allProperties():
     houses_data = real_db.child('House').get().val()
     houses = []
     if houses_data:
         for house_id, house_data in houses_data.items():
                image_urls = [house_data['house_images'].get(f'image_{i}', '') for i in range(1, 4)]
                # Append each house data to the list
                houses.append({
                    'id': house_id,
                    'rent': 'For Rent',  # Assuming all houses are for rent
                    'price': house_data.get('house_price', ''),
                    'propertyType': house_data.get('property_type', ''),
                    'owner':house_data.get('user_name',''),
                    'location': house_data.get('house_street', ''),
                    'beds': house_data.get('bed_number', ''),
                    'baths': house_data.get('toilet_number', ''),
                    'area': house_data.get('square_area', ''),
                    'image_urls': image_urls
                })
     return render_template('allProperties.html', houses=houses)
 
          
#====================================== detail property =================================================


@app.route('/detailProperty.html', methods=['GET', 'POST'])
def detailProperty():
    house_id = request.args.get('house_id')
    if house_id:
        response = real_db.child('House').child(house_id).get()
        house_data = response.val()
        if house_data:
             return render_template('detailProperty.html', house=house_data)
    return redirect(url_for('error-404.html'))
        

@app.route('/DashBoard.html', methods=['GET','POST'])
def DashBoard():
    
     ref = db.reference('/')

     users_snapshot = ref.child('Users').get()  
     houses_snapshot = ref.child('House').get()  
     pending_houses_snapshot = ref.child('Waiting').get()


     user_num  = len(users_snapshot.keys()) if users_snapshot else 0
     house_num = len(houses_snapshot.keys()) if houses_snapshot else 0
     waiting  = len(pending_houses_snapshot.keys()) if pending_houses_snapshot else 0

     if request.method == 'POST':
          phone_number = request.form.get("phone_number",'')
          users = real_db.child("Users").order_by_child("phone_number").equal_to(phone_number).get().val()
          userList = []
          if users:
               
               for user_id,  user_info in users.items():
                    client_name = user_info.get("name","")
                    user_email = user_info.get("email","")
                    user_phone = user_info.get("phone_number","")
                    user_address = user_info.get("address","")

                    userList.append({
                        "client_name" : client_name,
                        "user_email" : user_email,
                        "user_phone": user_phone,
                        "user_address": user_address
                    })
          return render_template('DashBoard.html', users = userList, user_num = user_num, house_num = house_num, waiting = waiting)


     users = real_db.child('Users').get().val()

     user_list = []

     for user_id, user_data  in users.items():
          client_name = user_data.get("name","")
          user_email = user_data.get("email","")
          user_phone = user_data.get("phone_number","")
          user_address = user_data.get("address","")

          user_list.append({
               "client_name" : client_name,
               "user_email" : user_email,
               "user_phone": user_phone,
               "user_address": user_address
          })

     return render_template('DashBoard.html', user_num = user_num, house_num = house_num, waiting = waiting, users= user_list)


@app.route('/modals.html', methods=['GET', 'POST'])
def modals():
    if request.method == 'POST':
          phone_number = request.form.get("phone_number",'')
          users = real_db.child("Users").order_by_child("phone_number").equal_to(phone_number).get().val()
          userList = []
          if users:
               
               for user_id,  user_info in users.items():
                    client_name = user_info.get("name","")
                    user_email = user_info.get("email","")
                    user_phone = user_info.get("phone_number","")
                    user_address = user_info.get("address","")

                    userList.append({
                        "client_name" : client_name,
                        "user_email" : user_email,
                        "user_phone": user_phone,
                        "user_address": user_address
                    })
          return render_template('DashBoard.html', users = userList)
    render_template

if __name__== '__main__':
    app.run(debug=True)