from flask import Flask, render_template, request, redirect, flash, send_file, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO


adminuser = "admin"
adminpass = "admin"

app = Flask(__name__)

app.secret_key = "uniquenepalhumepipeudhyogchitwanbharatpur"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;

pipeSizeList = ["150 MM", "200 MM", "250 MM", "300 MM", "400 MM", "450 MM", "500 MM", "600 MM", "700 MM", "750 MM", "800 MM", "900 MM", "1000 MM", "1200 MM"]

db = SQLAlchemy(app)

class Info(db.Model):
	sno = db.Column(db.Integer, primary_key=True)
	billnum = db.Column(db.Integer, nullable=True)
	chanum = db.Column(db.Integer, nullable=False)
	cid = db.Column(db.Integer, nullable=False)
	name = db.Column(db.String(100), nullable=False)
	pan = db.Column(db.String(20), nullable=False)
	address = db.Column(db.String(200), nullable=False)
	date = db.Column(db.String(12), nullable=False)
	phone = db.Column(db.String(12), nullable=False)
	total = db.Column(db.Integer, nullable=False)




class Extra(db.Model):
	sno = db.Column(db.Integer, primary_key=True)
	billnum = db.Column(db.Integer, nullable=False)
	chanum = db.Column(db.Integer, nullable=False)
	cid = db.Column(db.Integer, nullable=False)
	type = db.Column(db.String(100), nullable=False)
	size = db.Column(db.String(100), nullable=False)
	unit = db.Column(db.String(100), nullable=False)
	quantity = db.Column(db.Integer, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	amount = db.Column(db.Integer, nullable=False)
    
    
class Clients(db.Model):
	cid = db.Column(db.Integer, primary_key=True)
	pan = db.Column(db.String(), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	address = db.Column(db.String(100), nullable=False)
	phone = db.Column(db.String(100), nullable=False)
	
	def as_dict(self):
		return {'name':self.name}
	
def sesscheck():
	if 'user' in session and session["user"] == adminuser:
		return True
	else:
		return False
	



@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		user = request.form.get("username")
		password = request.form.get("password")
		print(user, password)
		if user == adminuser and password == adminpass:
			session["user"] = user
			return jsonify({"failed":False, "error":False});
		else:
			return jsonify({"failed":True, "error":"Wrong Username or Pass"});
	if 'user' in session and session["user"] == adminuser:
		return redirect("/")
	return render_template("login.html")

@app.route("/logout")
def logout():
	session.pop('user')
	return redirect("/login")

@app.route("/")
def humepipelist():
	if not sesscheck():
		return redirect("/login")		
	lists = Info.query.filter_by().all()
	return render_template("humepipelist.html", lists=lists)

@app.route("/addclient", methods=["POST", "GET"])
def addclient():
	if not sesscheck():
		return redirect("/login")
	if request.method == "POST":
		pan = request.form.get("pan")
		name = request.form.get("name")
		address = request.form.get("address")
		phone = request.form.get("phone")
		
		ins = Clients(pan=pan, name=name, address=address, phone=phone)
		db.session.add(ins)
		db.session.commit()
		flash('Added Client Successfully', 'success')
		return redirect("/clients")
		
	
@app.route("/clients")
def clients():
	if not sesscheck():
		return redirect("/login")
	lists = Clients.query.filter_by().all()
	return render_template("clients.html", lists=lists)
	
@app.route("/update", methods=["POST", "GET"])
def update():
	if not sesscheck():
		return redirect("/login")
	if request.method == "GET":
		cid = request.args.get("sno")
		data = Clients.query.filter_by(cid=cid).first()
		if(data):
			return jsonify({"name":data.name, "address":data.address, "phone":data.phone, "pan":data.pan})
			

	if request.method == "POST":
		cid = request.form.get("editsno")
		name = request.form.get("editname")
		pan = request.form.get("editpan")
		address = request.form.get("editaddress")
		phone = request.form.get("editphone")
		e_data = Clients.query.filter_by(cid=cid).first()
		e_data.name = name
		e_data.pan = pan
		e_data.address = address
		e_data.phone = phone
		db.session.commit()
		flash('Edited Client Data Successfully', 'success')
		return redirect("/clients")
		
		

		
@app.route("/create", methods=["POST", "GET"])
def create():
	if not sesscheck():
		return redirect("/login")
	if request.method == "POST":
		chanum = request.form.get("chanum")
		exist = Info.query.filter_by(chanum=chanum).all();
		if(not exist):
			print(request.form.get("size"))
			billnum = request.form.get("billnum")
			name = request.form.get("name")
			pan = request.form.get("pan")
			address = request.form.get("address")
			cid = request.form.get("cid")
			date = request.form.get("date")
			phone = request.form.get("phone")
			type = request.form.getlist("type")
			size = request.form.getlist("size")
			unit = request.form.getlist("unit")
			quantity = request.form.getlist("quantity")
			price = request.form.getlist("price")
			amount = request.form.getlist("amount")
			total = request.form.get("finaltotal")
			ins = Info(chanum=chanum, billnum=billnum, name=name, pan=pan, address=address, date=date, phone=phone, total=total, cid=cid)
			db.session.add(ins)
			db.session.commit()
			for t,s,u,q,p,a in zip(type,size,unit,quantity,price,amount):
				que = Extra(chanum=chanum, billnum=billnum,type=t,size=s,unit=u,quantity=q,price=p,amount=a, cid=cid)
				db.session.add(que)
				db.session.commit()
			flash('Data Created Successfully','success')
			return redirect("/")
		else:
			return "Bill Already Exists"
	return render_template("createnewhume.html", humePipeSize=pipeSizeList)

@app.route("/delete/<string:chnum>")
def delete(chnum):
	if not sesscheck():
		return redirect("/login")
	exist = Info.query.filter_by(chanum=chnum).first()
	if(exist):
		aexist = Extra.query.filter_by(chanum=chnum).delete()
		db.session.commit()
		db.session.delete(exist)
		db.session.commit()
		flash('Data Deleted Successfully','success')
		return redirect("/")
	else: 
		flash('Bill Doesnot Exist','error')
		return redirect('/')
		
@app.route("/client_delete/<string:chnum>")
def client_delete(chnum):
	if not sesscheck():
		return redirect("/login")
	exist = Clients.query.filter_by(cid=chnum).first()
	if(exist):
		aexist = Extra.query.filter_by(chanum=chnum).delete()
		db.session.commit()
		db.session.delete(exist)
		db.session.commit()
		axist = Info.query.filter_by(chanum=chnum).delete()
		db.session.commit()
		flash('Client Deleted Successfully','success')
		return redirect("/clients")
	else: 
		flash('Bill Doesnot Exist','error')
		return redirect('/')
		
		
@app.route("/view/<string:chnum>")
def view(chnum):
	if not sesscheck():
		return redirect("/login")
	maindata = Info.query.filter_by(chanum=chnum).first()
	ext = Extra.query.filter_by(chanum=chnum).all()
	length = len(ext)
	return render_template("view.html", ext=ext, maindata=maindata, length=length)
	
@app.route("/edit/<string:chanum>", methods=["POST", "GET"])
def edit(chanum):
	if not sesscheck():
		return redirect("/login")
	maindata = Info.query.filter_by(chanum=chanum).first()
	ext = Extra.query.filter_by(chanum=chanum).all()
	length = len(ext)
	if request.method == "POST":
		maindata.name = request.form.get("order_receiver_name")
		maindata.pan = request.form.get("pan")
		maindata.address = request.form.get("address")
		maindata.date = request.form.get("date")
		maindata.phone = request.form.get("phone")
		maindata.total = request.form.get("finaltotal")
		maindata.billnum = request.form.get("billnum")
		maindata.chanum = request.form.get("chanum")
		db.session.commit()
		chanum = request.form.get("chanum")
		bill = request.form.get("billnum")
		type = request.form.getlist("type")
		size = request.form.getlist("size")
		unit = request.form.getlist("unit")
		quantity = request.form.getlist("quantity")
		price = request.form.getlist("price")
		amount = request.form.getlist("amount")
		for t,s,u,q,p,a,ex in zip(type,size,unit,quantity,price,amount,ext):
			ex.chanum = chanum
			ex.billnum = bill
			ex.type = t
			ex.size = s
			ex.unit = u
			ex.quantity = q
			ex.price = p
			ex.amount = a
			db.session.commit()
		flash('Changes Applied Sucessfully','success')
		return redirect("/")
		
			
	return render_template("edithume.html", ext=ext, maindata=maindata, pipeList=pipeSizeList, length=length)
	

@app.route('/client', methods=["POST", "GET"])
def countrydic():
	if request.method == "GET":
		res = Clients.query.all()
		list_client = [r.as_dict() for r in res]
	
		return jsonify(list_client)
	if request.method == "POST":
		data = Clients.query.filter_by(name=request.form.get("name")).first()
		return jsonify({"cid":data.cid, "address":data.address, "phone":data.phone, "pan":data.pan})

if __name__ == "__main__":
	app.run(debug=True)