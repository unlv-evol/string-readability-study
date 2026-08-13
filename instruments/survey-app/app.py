from flask import Flask, redirect, url_for, render_template,session, jsonify, request,send_file, send_from_directory
from datetime import datetime
from pathlib import Path
import randomize
import csv
import os
import uuid
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# Response storage. The original study uploaded each response to a private S3
# bucket; replications have no access to it, so local CSV storage is the
# default. Set RESPONSE_STORAGE=s3 (plus AccessKey/SecreteAccessKey and the
# bucket names) to restore the original behaviour. See .env.example.
RESPONSE_STORAGE = os.environ.get('RESPONSE_STORAGE', 'local').lower()


def _default_response_dir():
    """<repo>/data/responses when running from the repository, else ./responses.

    In a container the app is copied to /app, outside the repository layout,
    so the repo-relative default is not always available.
    """
    app_dir = Path(__file__).resolve().parent
    if len(app_dir.parents) >= 2:
        return app_dir.parents[1] / 'data' / 'responses'
    return app_dir / 'responses'


RESPONSE_DIR = Path(os.environ.get('RESPONSE_DIR') or _default_response_dir())
TASK_BUCKET = os.environ.get('TaskBucket', 'string-experiment')
SURVEY_BUCKET = os.environ.get('SurveyBucket', 'string-experiment-post')

transfer = None
if RESPONSE_STORAGE == 's3':
    import boto3
    from boto3.s3.transfer import S3Transfer
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ['AccessKey'],
            aws_secret_access_key=os.environ['SecreteAccessKey'],
        )
    except KeyError as exc:
        raise SystemExit(
            f"RESPONSE_STORAGE=s3 requires {exc} in the environment or .env file.\n"
            "Copy .env.example to .env and fill it in, or unset RESPONSE_STORAGE "
            "to record responses locally instead."
        )
    transfer = S3Transfer(s3_client)
else:
    RESPONSE_DIR.mkdir(parents=True, exist_ok=True)


def store_response(df, uid, kind, bucket):
    """Persist one participant's responses.

    Writes a CSV next to the other study data (local mode) or uploads it to the
    study's S3 bucket (s3 mode). Returns the path written locally, if any.
    """
    filename = f"{uid}_{kind}.csv"

    if transfer is None:
        path = RESPONSE_DIR / filename
        df.to_csv(path, index=False)
        return path

    path = Path('/tmp') / filename
    df.to_csv(path, index=False)
    # The object key is the access key id, matching the naming of the original
    # collected files in data/raw/ (the bucket is versioned).
    transfer.upload_file(str(path), bucket, os.environ['AccessKey'],
                         extra_args={'ServerSideEncryption': "AES256"})
    return path


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-not-for-production')

@app.route("/informed-consent")
def consent():
    return render_template("consent.html")

@app.route('/doc/<filename>')
def download_file(filename):
    """Serve static PDF files from the 'static/doc' directory."""
    return send_from_directory('static/doc', filename)

@app.route("/declined")
def decline():
    return render_template("decline.html")

@app.route("/")
def home():
    # make sure session is empty at the start of each experience or
    # at the end of experience
    session.clear()
    return render_template("welcome.html")
@app.route("/protocol")
def protocol():
    return render_template("protocol.html")
@app.route("/demographics")
def demographics():
    return render_template("demographics.html")

@app.route("/pre-tasks")
def pre_tasks():
    return render_template("pre-tasks.html")

@app.route("/experiment")
def experiment():
    return render_template("experiment.html")

@app.route("/experiment-completed")
def experiment_completed():
    return render_template("end.html")

@app.route("/post-survey")
def post_survey():
    return render_template("post-survey.html")

@app.route("/process-post-survey", methods=['POST'])
def process_post_survey():
    # data = request.get_json()

    uid = session.get('uid')
    if isinstance(uid, tuple):
        uid = uid[0]  # extract the actual UID
    
    readability_reflection = request.form.get('readability_reflection'),
    comprehension_debugging = request.form.get('comprehension_debugging'),
    preference_rationale = request.form.get('preference_rationale'),
    learning_curve = request.form.get('learning_curve'),
    suggestions_improvement = request.form.get('suggestions_improvement')
    
    data_for_df = {
        'UID': uid,
        'readability_reflection': readability_reflection,
        'comprehension_debugging': comprehension_debugging,
        'preference_rationale': preference_rationale,
        'learning_curve': learning_curve,
        'suggestions_improvement': suggestions_improvement
    }

     # Create DataFrame
    df = pd.DataFrame(data_for_df)
    store_response(df, uid, 'post_survey_response', SURVEY_BUCKET)

    return redirect(url_for('experiment_completed'))

@app.route("/process", methods=['POST'])
def process_demographics():
    session['age'] = request.form['age']
    session['year'] = request.form['year'] # college year
    session['education'] = request.form['education'] # college year
    session['jobxp'] = request.form['jobxp'] # year of programming experience
    session['state'] = request.form['state']
    session['major'] = request.form['major']
    session['gender'] = request.form['gender']
    session['uid'] = str(uuid.uuid1())[:8]
    return redirect(url_for('pre_tasks'))

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()

    uid = session.get('uid')
    if isinstance(uid, tuple):
        uid = uid[0]  # extract the actual UID
    
    data_for_df = [
    {
        'UID': session['uid'],
        'Gender': session['gender'],
        'Age': session['age'],
        'YearInCollege': session['year'],
        'Education': session['education'],
        'State': session['state'],
        'Major': session['major'],
        'JobExperience': session['jobxp'],
        'TaskID': question_id,
        'Complexity': answers['complexity'],
        'Category': answers['category'],
        'CorrectAnswer': answers['correctAnswer'],
        'UserAnswer': answers['userAnswer'],
        'Duration': answers['duration']
    }
    for question_id, answers in data.items()
    ]

    # Create DataFrame
    df = pd.DataFrame(data_for_df)
    store_response(df, uid, 'response', TASK_BUCKET)

    return jsonify({'status': 'success'})

@app.route("/responses")
def responses():
    return render_template("responses.html")

@app.route('/download')
def download():
    directory = Path('/tmp') if transfer is not None else RESPONSE_DIR
    return send_file(directory / f"{session['uid']}_response.csv", as_attachment=True)

if __name__ == "__main__":
    # On macOS, port 5000 is taken by the AirPlay Receiver by default.
    # Either disable it in System Settings > General > AirDrop & Handoff,
    # or run with a different port:  PORT=5050 python app.py
    port = int(os.environ.get('PORT', 5000))
    print(f" * Storing responses: {RESPONSE_STORAGE}"
          + (f" ({RESPONSE_DIR})" if transfer is None else ""))
    app.run(debug=True, port=port)
