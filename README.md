# An interactive Live UI to generate a Scale Free Graph

#  New featuress
1, Using sigma.JS rather than D3 JS now supports larger graph with nodes up to 50K on local and 5K on cloud.
2, It now generates the graph dynamically and update in a real-time manner.
3, It now adds and removes nodes in a dynamic way.

[A Live DEMO](https://dynamicgraph.herokuapp.com)

Create virtuaenv for python3.

After creation go to the working directory and activate the virtual env created.

Now run command:

```
pip install -r requirements.txt
```

In order to start the application,

```python
python app.py
```

In the browser, open the link.

http://127.0.0.1:8080

Thats it, enjoy the application.

Deploy to heroku

add Procfile

web: gunicorn src.app:app --log-file=-

Install the Heroku CLI
Download and install the Heroku CLI.

If you haven't already, log in to your Heroku account and follow the prompts to create a new SSH public key.

```
$ heroku login
```
Create a new Git repository
Initialize a git repository in a new or existing directory

```
$ cd [my-project]/
$ git init
$ heroku git:remote -a [my-project]
```

Deploy your application
Commit your code to the repository and deploy it to Heroku using Git.

```
$ git add .
$ git commit -am "make it better"
$ git push heroku master
```

