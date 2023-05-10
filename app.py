import os
import openai
from flask import Flask,flash, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
import PyPDF2


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = { 'pdf'}


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "super secret key"


openai.api_key = os.getenv("OPENAI_API_KEY")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)            
            file.save(os.path.join(os.path.sep, os.getcwd(),app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('upload.html')


	
      
   
@app.route('/upload/<name>')
def download_file(name):
    filepath = os.path.join(os.path.sep,os.getcwd(),app.config['UPLOAD_FOLDER'], name)
    #print(filepath)

    fhandle = open(r''+filepath+'', 'rb')
    pdfReader = PyPDF2.PdfReader(fhandle)
    
    pagehandle = pdfReader.pages[0]
    #result = pagehandle.extract_text()
    result =""
    for i in range(len(pdfReader.pages)):
        current_page = pdfReader.pages[i]
        result+="Content on page:" + str(i + 1)+"===\r\n"
        result+=current_page.extract_text()
        result+="\r\n\n===="

    #result =filepath
    #return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    fhandle.close()
    os.remove(filepath)
    return render_template("preview.html",result = result)
    #return ''


@app.route('/chatgpt',methods=['POST'])
def chatgpt():
    if request.method == "POST":
        question = request.form["prompt"]
        model="gpt-3.5-turbo"
        messages = [
            {'role': 'user', 'content': question}
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages = messages,
            temperature=0,
            max_tokens=200,
        )
        result = response.choices[0].message["content"]
        return render_template("preview.html",result = result)

    return render_template("preview.html",result = 'Nome')


		
if __name__ == '__main__':
   app.run(debug = True)
