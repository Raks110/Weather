import os
import requests
from flask import Flask,request,render_template
import time

app = Flask(__name__,template_folder = 'Templates')

@app.route('/',methods=['GET','POST'])
def initial_view():
    if request.method == 'GET':
        return render_template('initial.html',background='initial.jpg',theme='Theme: Default',colorDiv='rgba(0,0,0,0.7)',fontDiv='white')
    elif request.method == 'POST':
        search_element = request.form['search']
        url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&APPID=594c7aab9fffecc844145f06d31f8c91&q={}'
        loc_json = requests.get(url.format(search_element)).json()
        ts = time.time()
        if(ts>=loc_json['sys']['sunrise'] and ts<=loc_json['sys']['sunset']):
            if(loc_json['cod']==200):
                weather = {
                    'city' : loc_json['name'],
                    'temprature' : loc_json['main']['temp'],
                    'description' : loc_json['weather'][0]['description'],
                    'icon' : loc_json['weather'][0]['icon']
                }
                return render_template('search.html',weather=weather,background='daylight.jpg',theme='Theme: Daylight',fontDiv='white')
            else:
                weather={
                'city' : "City could not be located. Please try again.",
                'temprature' : '',
                'description' : '',
                'icon' : '',
                }
                return render_template('search.html',background='initial.jpg',theme='Theme: Default',fontDiv='white')
        else:
            if(loc_json['cod']==200):
                weather = {
                    'city' : loc_json['name'],
                    'temprature' : loc_json['main']['temp'],
                    'description' : loc_json['weather'][0]['description'],
                    'icon' : loc_json['weather'][0]['icon']
                }
                return render_template('search.html',weather=weather,background='night.jpg',theme='Theme: Nightfall',colorDiv='rgba(255,255,255,0.7)',fontDiv='black')
            else:
                weather={
                'city' : "City could not be located. Please try again.",
                'temprature' : '',
                'description' : '',
                'icon' : '',
                }
                return render_template('search.html',background='initial.jpg',theme='Theme is set to Default',fontDiv='white')

if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
