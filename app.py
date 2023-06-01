from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 
db = SQLAlchemy(app)

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    rma = db.Column(db.String(50))
    sha256_hash = db.Column(db.String(64))


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['image']
        rma = request.form['rma']

        if file and allowed_file(file.filename):
            # Read the contents of the file
            file_contents = file.read()

            # Generate SHA256 hash of the file contents
            sha256_hash = hashlib.sha256(file_contents).hexdigest()

            # Check DB for previous uploads
            match = Image.query.filter_by(sha256_hash=sha256_hash).first()
            if match:
                 return f'<h1>Duplicate file. This file has already been uploaded with RMA: {match.rma}</h1>'

            # Save the data to the database
            image = Image(rma=rma, sha256_hash=sha256_hash)
            db.session.add(image)
            db.session.commit()

            return f'<h1>Success! SHA256 hash: {sha256_hash}<br>RMA: {rma}</h1>'

        return '<h1>No file uploaded.</h1>'

    return render_template('upload.html')

if __name__ == '__main__':

    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
