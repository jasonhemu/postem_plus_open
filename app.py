from flask import Flask, render_template, request, redirect, url_for, Response, session, flash, stream_with_context
from pylti.flask import lti
import settings
import os
import json
import requests
import logging
from logging.handlers import RotatingFileHandler
from io import StringIO
import pandas as pd
import boto3
import csv
from werkzeug.datastructures import Headers

# ============================================
# Flask Init.
# ============================================
app = Flask(__name__)
app.secret_key = settings.secret_key
app.config['PYLTI_CONFIG'] = settings.PYLTI_CONFIG
app.config['DEBUG'] = True
app.config['TESTING'] = False

# ============================================
# AWS Init.
# ============================================
s3_client = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
s3_resource = boto3.resource('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

# ============================================
# Logging Init.
# ============================================
formatter = logging.Formatter(settings.LOG_FORMAT)
handler = RotatingFileHandler(
    settings.LOG_FILE,
    maxBytes=settings.LOG_MAX_BYTES,
    backupCount=settings.LOG_BACKUP_COUNT
)
handler.setLevel(logging.getLevelName(settings.LOG_LEVEL))
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# ============================================
# Utility Functions
# ============================================

# LTI Launch Error
def error(exception=None):
    app.logger.error("PyLTI error: {}".format(exception))
    return render_template('error.html',
                                alert_stay='Authentication error. No LTI session detected.',
                                alert_contact='Please launch this tool from Canvas. If this error persists, please contact support.')

# ============================================
# Web Views / Routes
# ============================================
@app.route('/', methods=['GET','POST'])
def index():
    if 'canvas_course_id' not in session:
        return redirect(url_for('launch'))

    # More information about roles on Canvas (https://community.canvaslms.com/thread/1985)
    try:
        postem_filename = str(session['canvas_course_id']) + '.csv'

        if 'Instructor' in session['user_role']:
            try:
                postem_file = s3_client.get_object(Bucket=settings.BUCKET, Key=postem_filename)
            except:
                return render_template('instructor.html',
                                            postem_table=None,
                                            alert_stay='No data available. Upload a valid CSV file.')

            postem_table_temp = postem_file['Body'].read().decode('utf-8')
            postem_table_dataframe = pd.read_csv(StringIO(postem_table_temp)).transpose()
            postem_table_dataframe = postem_table_dataframe.fillna('')
            postem_table_dataframe.reset_index(level=0, inplace=True)
            postem_table_header = postem_table_dataframe.iloc[0].tolist()
            postem_table_body = postem_table_dataframe.iloc[1:].values.tolist()

            return render_template('instructor.html',
                                        postem_table_header=postem_table_header,
                                        postem_table_body=postem_table_body,
                                        alert_stay='Click on the student name to view as that student.')

        elif 'Learner' in session['user_role']:
            try:
                postem_file = s3_client.get_object(Bucket=settings.BUCKET, Key=postem_filename)
            except:
                return render_template('student.html',
                                            postem_table_student=None,
                                            postem_table_display=None,
                                            alert_stay='No data available.')

            postem_table_temp = postem_file['Body'].read().decode('utf-8')
            postem_table_dataframe = pd.read_csv(StringIO(postem_table_temp))
            postem_table_dataframe = postem_table_dataframe.fillna('').transpose()
            postem_table_dataframe.reset_index(level=0, inplace=True)
            postem_table_header = postem_table_dataframe.iloc[:,0].tolist()
            postem_table_header = postem_table_header[2:]
            postem_table_body = postem_table_dataframe.transpose().iloc[1:].values.tolist()

            flag_no_data = True

            for item in postem_table_body:
                sisid = item[1]
                if sisid == str(session['canvas_user_login_id']):
                    flag_no_data = False
                    postem_table_body_student = item[2:]
                    break

            if len(postem_table_body_student) == 0:
                flag_no_data = True

            if flag_no_data is True:
            # No matching SISID in the CSV File
                return render_template('student.html',
                                            postem_table_student=None,
                                            postem_table_display=None,
                                            alert_stay='No data available.')

            postem_table_student = zip(postem_table_header, postem_table_body_student)
            return render_template('student.html',
                                        postem_table_student=postem_table_student,
                                        postem_table_display=True,
                                        alert_stay=None)

        # Designer Role
        elif 'ContentDeveloper' in session['user_role']:
            return render_template('error.html',
                                        alert_stay='You need to have a teacher role or a student role to use this tool. Your current role is Course Designer.',
                                        alert_contact='Please contact the course instructor.')
        # TA Role
        elif 'TeachingAssistant' in session['user_role']:
            return render_template('error.html',
                                        alert_stay='You need to have a teacher role or a student role to use this tool. Your current role is TA.',
                                        alert_contact='Please contact the course instructor.')
        # Observer Role
        elif 'Observer' in session['user_role']:
            return render_template('error.html',
                                        alert_stay='You need to have a teacher role or a student role to use this tool. Your current role is Observer.',
                                        alert_contact='Please contact the course instructor.')
        else:
            return render_template('error.html',
                                        alert_stay='Something wrong happend!',
                                        alert_contact='Please contact the course instructor.')

    except Exception as e:
        return render_template('error.html',
                    alert_stay=e,
                    alert_contact='Please contact support.')

@app.route('/launch', methods=['GET', 'POST'])
@lti(error=error, request='any', role='any', app=app)
def launch(lti=lti):
    try:
        data = request.form
        app.logger.info(json.dumps(request.form, indent=2))
        session['canvas_course_id'] = request.form.get('custom_canvas_course_id')
        session['canvas_user_id'] = request.form.get('custom_canvas_user_id')
        session['canvas_user_login_id'] = request.form.get('custom_canvas_user_login_id')
        session['user_fullname'] = request.form.get('custom_canvas_user_login_id')
        session['user_firstname'] = request.form.get('lis_person_name_given')
        session['user_role'] = request.form.get('roles')
        return redirect(url_for('index'))

    except Exception as e:
        return render_template('error.html',
                    alert_stay=e,
                    alert_contact='Please contact support.')

@app.route('/template')
def template():
    def generate():
        data = StringIO()
        writer = csv.writer(data)
        url = settings.CANVAS_API_URL + 'courses/' + str(session['canvas_course_id']) + '/students'
        response = requests.get(url, headers=settings.HEADERS)
        status_code = response.status_code

        if status_code != 200:
                writer.writerow(('Something wrong happened, please contact 302-831-6400.',))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)
        else:
            json_response = response.json()
            student_names = []
            sis_user_ids = []
            for student in json_response:
                student_name = str(student['name'])
                sis_user_id = str(student['sis_user_id'])

                if sis_user_id != 'None':
                    student_names.append(student_name)
                    sis_user_ids.append(sis_user_id)

            if not sis_user_ids:
                writer.writerow(('No student enrollment in this course site.',))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)
            else:
                csv_data = zip(student_names, sis_user_ids)
                csv_data_list = list(csv_data)
                writer.writerow(('Name', 'SISID'))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)

                for item in csv_data_list:
                    writer.writerow((item[0], item[1]))
                    yield data.getvalue()
                    data.seek(0)
                    data.truncate(0)

    try:
        csv_headers = Headers()
        postem_file_name = str(session['canvas_course_id']) + '.csv'
        csv_headers.set('Content-Disposition', 'attachment', filename=postem_file_name)

        # stream the response as the data is generated
        return Response(stream_with_context(generate()),
                                mimetype='text/csv',
                                headers=csv_headers)

    except Exception as e:
        return render_template('error.html',
                    alert_stay=e,
                    alert_contact='Please contact support.')

@app.route('/download')
def download_csv():
    try:
        flag_no_data = True
        postem_filename = str(session['canvas_course_id']) + '.csv'
        postem_bucket = s3_resource.Bucket(settings.BUCKET)
        for file in postem_bucket.objects.all():
            if file.key == postem_filename:
                flag_no_data = False
                break

        if flag_no_data is False:
            postem_file = s3_client.get_object(Bucket=settings.BUCKET, Key=postem_filename)
            csv_headers = Headers()
            csv_headers.set('Content-Disposition', 'attachment', filename=postem_filename)
            return Response(stream_with_context(postem_file['Body'].read().decode('utf-8')),
                                    mimetype='text/csv',
                                    headers=csv_headers)
        else:
            flash('You have not uploaded anything!', 'warning')
            return redirect(url_for('index'))

    except Exception as e:
        return render_template('error.html',
                    alert_stay=e,
                    alert_contact='Please contact support.')

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS
    try:
        if request.method == 'POST':
            if 'file' not in request.files:
                #flash('No selected file.', 'warning')
                return redirect(url_for('index'))

            file = request.files['file']
            if file.filename == '':
                #flash('No selected file.', 'warning')
                return redirect(url_for('index'))

            if file and allowed_file(file.filename):
                filename = str(session['canvas_course_id']) + '.csv'
                s3_resource.Bucket(settings.BUCKET).put_object(Key=filename, Body=file)
                #flash('File upload successfully!', 'success')
                return redirect(url_for('index'))
            else:
                #flash('Only CSV file is allowed to upload.', 'warning')
                return redirect(url_for('index'))

    except Exception as e:
        return render_template('error.html',
                    alert_stay=e,
                    alert_contact='Please contact support.')

@app.route('/xml')
def lti_xml():
    return redirect(url_for('static', filename='lti.xml'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect("https://commons.udel.edu/", code=302)

if __name__ == "__main__":
    app.run(debug=True)
