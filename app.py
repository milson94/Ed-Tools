from flask import Flask, render_template, redirect, url_for, request, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from report_to_footer_logic import add_footer_to_pdfs  # Import the logic function
from pdf_merger_logic import merge_pdfs  # Import the PDF Merger logic function

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Tool Routes
@app.route('/report-to-footer', methods=['GET', 'POST'])
def report_to_footer():
    if request.method == 'POST':
        # Check if files are uploaded
        if 'pdf_files' not in request.files or 'footer_image' not in request.files:
            flash('No files uploaded!', 'danger')
            return redirect(url_for('report_to_footer'))

        pdf_files = request.files.getlist('pdf_files')
        footer_image = request.files['footer_image']

        # Validate files
        if not pdf_files or not footer_image.filename.endswith('.png'):
            flash('Invalid files uploaded!', 'danger')
            return redirect(url_for('report_to_footer'))

        # Call the logic function to process the files
        try:
            final_output_path = add_footer_to_pdfs(pdf_files, footer_image, app.config['UPLOAD_FOLDER'])
            flash('PDFs modified successfully!', 'success')
            return send_file(final_output_path, as_attachment=True)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('report_to_footer'))

    return render_template('report_to_footer.html')

@app.route('/pdf-merger', methods=['GET', 'POST'])
def pdf_merger():
    if request.method == 'POST':
        # Check if files are uploaded
        if 'pdf_files' not in request.files:
            flash('No files uploaded!', 'danger')
            return redirect(url_for('pdf_merger'))

        pdf_files = request.files.getlist('pdf_files')

        # Validate files
        if not pdf_files:
            flash('Invalid files uploaded!', 'danger')
            return redirect(url_for('pdf_merger'))

        # Get the output filename or use a default name
        output_filename = request.form.get('output_filename', 'merged.pdf')

        # Call the logic function to merge the PDFs
        try:
            final_output_path = merge_pdfs(pdf_files, output_filename, app.config['UPLOAD_FOLDER'])
            flash('PDFs merged successfully!', 'success')
            return send_file(final_output_path, as_attachment=True)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('pdf_merger'))

    return render_template('pdf_merger.html')

@app.route('/image-to-pdf')
def image_to_pdf():
    return render_template('image_to_pdf.html')

@app.route('/pdf-to-jpg')
def pdf_to_jpg():
    return render_template('pdf_to_jpg.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT if set, otherwise default to 5000
    app.run(host='0.0.0.0', port=port)