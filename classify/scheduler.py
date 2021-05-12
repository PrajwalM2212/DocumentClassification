import schedule
import requests

'''
Improves the classification every 3 hours
'''
def task():
    r = requests.get('http://127.0.0.1:5000/api/classify')
    print(r.text)

schedule.every(3).hours.do(task)

if __name__ == '__main__':
    while True:
        schedule.run_pending()