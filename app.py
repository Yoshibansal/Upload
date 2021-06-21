import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from os import listdir
from os.path import isfile, join
import zipfile

UPLOAD_FOLDER = 'static/uploaded_files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png',
                      'jpg', 'jpeg', 'gif', 'pptx', 'css', 'html'}

app = Flask(__name__)
app.secret_key = "qazxswedcvfrplmnko"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def tree_printer(root):
#     all_files = []
#     for root, dirs, files in os.walk(root):
#         for d in dirs:
#             all_files.append(root + '/' + d)
#         for f in files:
#             all_files.append(root + '/' + f)

#     print(all_files)
#     return all_files


def files_already_uploaded(mypath):
    # onlyfiles = []
    # for f in listdir(mypath):
    #     if isfile(join(mypath, f)):
    #         onlyfiles.append(f)
    #     else:
    #         for subf in listdir(join(mypath, f)):
    #             if isfile(join(mypath, subf)):
    #                 onlyfiles.append(subf)
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return onlyfiles


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


existing_files = files_already_uploaded(UPLOAD_FOLDER)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        # if file.filename == '':
        #     message = 'No file Selected'
        #     # return redirect(request.url)
        for file in files:
            if file and allowed_file(file.filename):
                # filename = secure_filename(file.filename)
                filename = file.filename
                direct = os.path.dirname(filename)
                if direct != '':
                    try:
                        os.mkdir(app.config['UPLOAD_FOLDER'] + '/' + direct)
                        file.save(app.config['UPLOAD_FOLDER'] + '/' + filename)
                    except:
                        file.save(app.config['UPLOAD_FOLDER'] + '/' + filename)
                else:
                    file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], filename))
            else:
                return render_template('index.html', message="File format is not supported")
        # print(direct)

        if direct != '':
            zip_path = os.path.join(
                app.config['UPLOAD_FOLDER'], direct.split('/')[0])
            zipf = zipfile.ZipFile('{}.zip'.format(
                zip_path), 'w', zipfile.ZIP_DEFLATED)
            zipdir(zip_path, zipf)
            # print("\n\n\n\n", direct.split('/')[0])
            zipf.close()

        return render_template('index.html', message="All files uploaded successfully")
    return render_template('index.html', message=message)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route('/d', methods=['GET', 'POST'])
def down():
    existing_files = files_already_uploaded(UPLOAD_FOLDER)
    return render_template('download.html', existing_files=existing_files)


@app.route('/static/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(
        debug=True,
        host="192.168.1.5",
        port=5000)
