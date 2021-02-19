from flask import Flask, render_template, request, redirect, flash, send_file, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import xlsxwriter
from io import BytesIO


#/private/var/mobile/Containers/Shared/AppGroup/F72DB166-711A-41BF-866B-8C5F7F3CF6BE/File Provider Storage/data.xlsx

adminuser = "admin"
adminpass = "admin"

app = Flask(__name__)
app.secret_key = "Secret Key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data'


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

def index_num(naam, query):
	emplist=[]
	d = f"data.{naam}"
	for data in query:
		emplist.append(eval(d))
	maxvalue = max(emplist, key=len)
	#max_index = emplist.index(maxvalue)
	return maxvalue
	
def gettodaydate():
	from nepali_date import NepaliDate
	a = str(NepaliDate.today())
	return a[3:7], a[8:10], a[11:13]


@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		user = request.form.get("username")
		password = request.form.get("password")
		print(user, password)
		if user == adminuser and password == adminpass:
			print("Authenticated")
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
	return render_template("createnewhume.html")

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
		return redirect(url_for('humepipelist'))
		
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
		return redirect(url_for('humepipelist'))
		
		
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
		
			
	return render_template("edithume.html", ext=ext, maindata=maindata, length=length)
	
	
@app.route("/export")
def export():
	if not sesscheck():
		return redirect("/login")
	output = BytesIO()
	maindata = Info.query.filter_by().all()
	nam = index_num("name",maindata)
	add = index_num("address", maindata)
	
	workbook = xlsxwriter.Workbook(output)
	
	worksheet = workbook.add_worksheet()
	work = workbook.add_format()
	work.set_border(10)
		
	list =["Challan No.", "Bill No.", "Name", "pan", "address", "total", "date"]
	bord = workbook.add_format({'border': 2})
	bld = workbook.add_format({'bold': True})
	
	worksheet.set_column('{0}:{0}'.format(chr(0 + ord('E'))), len(str(add)) + 2)
	worksheet.set_column('{0}:{0}'.format(chr(0 + ord('C'))), len(str(nam)) + 2)
	
	
	row = 0
	col = 0
	for li in list:
		worksheet.write(row, col, li, workbook.add_format({'border': 2, 'bold': True}))
		col += 1
	ro = 1
	c = 0
	for data in maindata:
		worksheet.write(ro, c, data.chanum, bord)
		worksheet.write(ro, c+1, data.billnum, bord)
		worksheet.write(ro, c+2, data.name, bord)
		worksheet.write(ro, c+3, data.pan, bord)
		worksheet.write(ro, c+4, data.address, bord)
		worksheet.write(ro, c+5, data.total, bord)
		worksheet.write(ro, c+6, data.date, bord)
		ro+=1
		
	
	
	
	workbook.close()
	output.seek(0)
	return send_file(output, attachment_filename="testing.xlsx", as_attachment=True)
	
@app.route("/export/<chnum>")
def exportchnum(chnum):
	if not sesscheck():
		return redirect("/login")
	maindata = Info.query.filter_by(chanum=chnum).first()
	if(maindata):
		output = BytesIO()
		workbook = xlsxwriter.Workbook(output)
		worksheet = workbook.add_worksheet()
		align_center = workbook.add_format({'align': 'center', 'border': 1})
		worksheet.merge_range('A1:F1', 'Unique Nepal Hume Pipe Udhyog', workbook.add_format({'align': 'center', 'bold': True, 'border': 1}))
		worksheet.merge_range('A2:F2', 'Sundar Chowk, Bharatpur-14, Chitwan', workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.merge_range('A3:F3', f"Name : {maindata.name}", workbook.add_format({'border': 1}))
		worksheet.merge_range('A4:F4', f"Address : {maindata.address}", workbook.add_format({'border': 1}))
		worksheet.merge_range('A5:F5', f"Challan No. : {maindata.chanum}", workbook.add_format({'border': 1}))
		worksheet.merge_range('A6:F6', f"Phone No. : {maindata.phone}", workbook.add_format({'border': 1}))
		lists = Extra.query.filter_by(chanum=chnum).all()
		
		
		
		worksheet.write(6, 0, "S.N.", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('A:A', 5)
		
		
		worksheet.write(6, 1, "Description", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('B:B', 20)
		
		worksheet.write(6, 2, "Unit", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('C:C', 5)
		
		worksheet.write(6, 3, "Quantity", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('D:D', 10)
		
		worksheet.write(6, 4, "Rate", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('E:E', 10)
		
		worksheet.write(6, 5, "Amount", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('F:F', 10)
		
		i = 1
		raw = 7
		col = 0
		for list in lists:
			worksheet.write(raw, col, i, workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write(raw, col+1, f"{list.size} {list.type}", workbook.add_format({'align': 'center', 'border': 1}))
			if(list.unit=="Running Meter"):
				u = "RM"
			else:
				u = "PCS"
			worksheet.write(raw, col+2, u, workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write(raw, col+3, list.quantity, workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write(raw, col+4, list.price, workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write(raw, col+5, list.amount, workbook.add_format({'align': 'center', 'border': 1}))
			raw+=1
			i+=1
		print(i)
			
		worksheet.merge_range("C"+str(raw+3)+":"+"E"+str(raw+3), "Sub Total", workbook.add_format({'border': 1}))
		worksheet.write("F"+str(raw+3), maindata.total, workbook.add_format({'align': 'center', 'border': 1}))
		f = 13 / 100 * maindata.total
		
		
		
		worksheet.merge_range("C"+str(raw+4)+":"+"E"+str(raw+4), "13% VAT", workbook.add_format({'border': 1}))
		worksheet.write("F"+str(raw+4), f, workbook.add_format({'align': 'center', 'border': 1}))
		
		
		worksheet.merge_range("C"+str(raw+5)+":"+"E"+str(raw+5), "Grand Total", workbook.add_format({'border': 1}))
		worksheet.write("F"+str(raw+5), maindata.total+f, workbook.add_format({'align': 'center', 'border': 1}))
		e = raw
		for d in range(1, 6):
			worksheet.write("B"+str(e+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write("A"+str(e+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			e+=1
		ew = raw
		for wew in range(1,3):
			worksheet.write("C"+str(ew+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write("D"+str(ew+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write("E"+str(ew+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write("F"+str(ew+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			ew+=1
		
		workbook.close()
		output.seek(0)
		return send_file(output, attachment_filename="testing.xlsx", as_attachment=True)
		
		
@app.route("/export/all")
def exportall():
	
	output = BytesIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet()
	maindata = Info.query.filter_by().order_by(Info.chanum.desc()).all()
	ind = 1
	for dta in maindata:
		
		
		align_center = workbook.add_format({'align': 'center', 'border': 1})
		#A1:F1
		worksheet.merge_range(f"A{ind}:F{ind}", 'Unique Nepal Hume Pipe Udhyog', workbook.add_format({'align': 'center', 'bold': True, 'border': 1, 'top': 1}))
		worksheet.merge_range(f"A{ind+1}:F{ind+1}", 'Sundar Chowk, Bharatpur-14, Chitwan', workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.merge_range(f"A{ind+2}:F{ind+2}", f"Name : {dta.name}", workbook.add_format({'border': 1}))
		worksheet.merge_range(f"A{ind+3}:F{ind+3}", f"Address : {dta.address}", workbook.add_format({'border': 1}))
		worksheet.merge_range(f"A{ind+4}:F{ind+4}", f"Challan No. : {dta.chanum}", workbook.add_format({'border': 1}))
		worksheet.merge_range(f"A{ind+5}:F{ind+5}", f"Phone No. : {dta.phone}", workbook.add_format({'border': 1}))
		lists = Extra.query.filter_by(chanum=dta.chanum).all()
		
		
		
		worksheet.write(5+ind, 0, "S.N.", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('A:A', 5)
		
		
		worksheet.write(5+ind, 1, "Description", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('B:B', 20)
		
		worksheet.write(5+ind, 2, "Unit", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('C:C', 5)
		
		worksheet.write(5+ind, 3, "Quantity", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('D:D', 10)
		
		worksheet.write(5+ind, 4, "Rate", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('E:E', 10)
		
		worksheet.write(5+ind, 5, "Amount", workbook.add_format({'align': 'center', 'border': 1}))
		worksheet.set_column('F:F', 10)
		
		i = 1
		raw = 6+ind
		col = 0
		for list in lists:
			worksheet.write(raw, col, i, workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write(raw, col+1, f"{list.size} {list.type}", workbook.add_format({'align': 'center', 'border': 1}))
			if(list.unit=="Running Meter"):
				u = "RM"
			else:
				u = "PCS"
			worksheet.write(raw, col+2, u, workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write(raw, col+3, list.quantity, workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write(raw, col+4, list.price, workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write(raw, col+5, list.amount, workbook.add_format({'align': 'center', 'border': 1}))
			raw+=1
			i+=1
		
			
		worksheet.merge_range("C"+str(raw+3)+":"+"E"+str(raw+3), "Sub Total", workbook.add_format({'border': 1}))
		worksheet.write("F"+str(raw+3), dta.total, workbook.add_format({'align': 'center', 'border': 1}))
		f = 13 / 100 * dta.total
		
		
		
		worksheet.merge_range("C"+str(raw+4)+":"+"E"+str(raw+4), "13% VAT", workbook.add_format({'border': 1}))
		worksheet.write("F"+str(raw+4), f, workbook.add_format({'align': 'center', 'border': 1}))
		
		
		worksheet.merge_range("C"+str(raw+5)+":"+"E"+str(raw+5), "Grand Total", workbook.add_format({'border': 1}))
		worksheet.write("F"+str(raw+5), dta.total+f, workbook.add_format({'align': 'center', 'border': 1}))
		e = raw
		for d in range(1, 6):
			worksheet.write("B"+str(e+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write("A"+str(e+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			e+=1
		ew = raw
		for wew in range(1,3):
			worksheet.write("C"+str(ew+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write("D"+str(ew+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write("E"+str(ew+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			worksheet.write("F"+str(ew+1), "", workbook.add_format({'align': 'center', 'border': 1}))
			ew+=1
		
		ind+=15+i-1
	workbook.close()
	output.seek(0)
	return send_file(output, attachment_filename="test.xlsx", as_attachment=True)
	


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
