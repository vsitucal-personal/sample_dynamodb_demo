# sample_dynamodb_demo
## Demo for DynamoDB

---

**Setup custom jupyter kernel with python virtual environment**

setup venv

`python -m venv venv`

activate venv

`venv/Scripts/activate`

setup custom kernel

`ipython kernel install --name "dynamodb-demo-venv" --user`

create another python.exe executable inside venv/Scripts (to avoid spark errors)

`cp python.exe python3.exe`

---

**Setup Dependency Repo**

clone icgphutils repository

`git clone https://github.com/vsitucal-personal/icg-ph-python-utils.git`

in console move to where setup.py is located, example:

`cd ..\icg-ph-python-utils\src\icgphutils`

setup in develop mode

`pip setup.py develop`

---

**Install pip dependencies**

`pip install -r requirements.txt`

---

**Setup environment varible**

create environment variable file

`touch .env`

and pass variables
```
PATH_TO_AWS_CREDS=xxx
DB_NAME=xxx
GSI_INDEX_NAME=xxx
```

---

**Start JupyterLab**

`jupyter lab`

---

**If you want to deploy in your aws account via cloudformation using aws cli**

`aws cloudformation package --template-file template.yml --s3-bucket $BUILD_OUTPUT_BUCKET --s3-prefix $SERVICE --output-template-file app-output_sam.yaml`

`aws cloudformation deploy --template-file app-output_sam.yaml --stack-name sample-dynamodb-demo --capabilities CAPABILITY_IAM`
