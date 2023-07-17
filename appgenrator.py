from flask import Flask, request, render_template, send_file
import os
import tempfile
from zipfile import ZipFile

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            title = request.form['title']
            variable_input_2 = int(request.form['variable_input_2'])

            n_values = []
            for i in range(1, variable_input_2+1):
                input_name = 'input_' + str(i)
                value = request.form.get(input_name)
                n_values.append(value)
            print(n_values)
            open_id = request.form['open_id']
            prompt = request.form['prompt']

            # Define the new project's directory

            temp_dir = tempfile.gettempdir()

            # project_directory = os.path.join(app.root_path, title)
            project_directory = os.path.join(temp_dir, title)

            # Create the new project directory and a 'templates' directory within it
            os.makedirs(os.path.join(project_directory,
                        'templates'), exist_ok=True)

            # Print the created directory path
            print(f"Project directory: {project_directory} has been created.")

            # Create the 'main.py' for the new project
            with open(os.path.join(project_directory, 'main.py'), 'w') as f:
                f.write(f'''
from flask import Flask, request, render_template
import openai

openai.api_key = '{open_id}'

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        n_values1 = []
        for i in range(0, {variable_input_2}):
            input_name1 = 'input_' + str(i)
            value1 = request.form.get(input_name1)
            n_values1.append(value1)

        prompt = f"{prompt}"

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            temperature=0.5,
            max_tokens=500
        )

        return render_template('index.html', n_values={n_values}, variable_input_2={variable_input_2}, result=response.choices[0].text.strip())

    return render_template('index.html', n_values={n_values}, variable_input_2={variable_input_2})

if __name__ == '__main__':
    app.run(debug=True)
''')

            print("main.py file created.")

            # Create the 'index.html' template for the new project
            with open(os.path.join(project_directory, 'templates', 'index.html'), 'w') as f:
                f.write(f'''
<!DOCTYPE html>
<html>
<head>
    <title>Input Form</title>
    <style>
        body {{
            background-color: black;
            color: white;
            text-align: center;
        }}
        
        h2, form, p {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <h2>{title}</h2><br>
    <form action="/" method="post">
        <div id="input_fields"></div>
        <input type="submit" value="Generate">
    </form>
    <h2>Result</h2>
    <p>{{{{result}}}}</p>
    <script>
        // Generate input fields based on 'no of variables'

        var inputFields = '';
        var n_values = {n_values};
        for (var i = 0; i < {variable_input_2}; i++) {{
            inputFields += '<label for="n_values_' + i + '">' + n_values[i] + '</label><br>';
            inputFields += '<input type="text" id="input_' + i + '" name="input_' + i + '"><br><br>';
        }}
        document.getElementById('input_fields').innerHTML = inputFields;
    </script>
</body>
</html>
''')

            print("index.html file created.")

            # Create the 'result.html' template for the new project
            with open(os.path.join(project_directory, 'templates', 'result.html'), 'w') as f:
                f.write(f'''
<!DOCTYPE html>
<html>
<head>
    <title>Result</title>
    <style>
        body {{
            background-color: black;
            color: white;
            text-align: center;
        }}
        
        h2, p {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <h2>Result</h2>
    <p>{{{{result}}}}</p>
</body>
</html>
''')

            print("result.html file created.")

            if os.path.exists(project_directory):
                print("Yes the project folder exists !!!!")
                project_folder_name = title

                download_response = download_folder(
                    project_directory, temp_dir, project_folder_name)

                return download_response

        except Exception as e:
            print("An error occurred while generating the project:", e)

    return render_template('index.html')


def download_folder(project_directory, temp_dir, project_folder_name):

    zip_path = os.path.join(temp_dir, f'{project_folder_name}.zip')
    zip_folder(project_directory, zip_path)

    return send_file(f'{zip_path}', as_attachment=True,
                     download_name=f'{project_folder_name}.zip')


def zip_folder(folder_path, zip_path):
    with ZipFile(zip_path, 'w') as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, arcname=os.path.relpath(
                    file_path, folder_path))


if __name__ == '__main__':
    app.run(debug=True)
