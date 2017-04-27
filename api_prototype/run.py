# run.py

from app import app

# if running on AWS
# if __name__ == '__main__':
#     app.run('0.0.0.0', 80)

# if running locally
if __name__ == '__main__':
	app.run()