
import os

from flask import Flask,request,render_template,g,session,redirect,url_for,make_response

import requests
import time

import sqlite3

from werkzeug.security import generate_password_hash, \
     check_password_hash

app = Flask(__name__,template_folder = 'Templates')
app.config['SECRET_KEY'] = "b'J\x01\xe7M\x00\xd0\xb2\xc3-_\x7f\x87`\xca\xcc\\\x1b\x18\xd5\x11\x99LCh'"

""""
########################################
Connection to Database
########################################
"""
def connect_db():
    return sqlite3.connect('F:/Weather/users.db')


@app.before_request
def before_request():
    g.db = connect_db()


"""
########################################
########################################
"""

"""
########################################
Initial View: search.html and inital.html
########################################
"""

@app.route('/',methods=['GET','POST'])
def initial_view():
    try:
        if session.get('username') is not None:
            return redirect(url_for('user'), code=301)
        else:
            session.pop('user',None)
            session.pop('username',None)
            raise Exception('Session User should not be None')
            return None
    except:
        url = 'http://api.ipstack.com/{}?access_key=7a87a908475dd3aa325ad0854b44b750&format=1&output=json'.format(request.remote_addr)
        r = requests.get(url).json()
        city_element = r['city']
        if request.method == 'GET':
            return render_template('initial.html',background='initial.jpg',theme='Theme: Default',colorDiv='rgba(0,0,0,0.6)',fontDiv='white',city=city_element,login='True')
        elif request.method == 'POST':
            search_element = request.form['search']
            url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&APPID=594c7aab9fffecc844145f06d31f8c91&q={}'
            loc_json = requests.get(url.format(search_element)).json()
            ts = time.time()
            if(loc_json['cod']==200):
                if(ts>=loc_json['sys']['sunrise'] and ts<=loc_json['sys']['sunset']):
                    weather = {
                        'city' : loc_json['name'],
                        'temprature' : loc_json['main']['temp'],
                        'description' : loc_json['weather'][0]['description'],
                        'icon' : loc_json['weather'][0]['icon']
                    }
                    return render_template('search.html',weather=weather,background='daylight.jpg',theme='Theme: Daylight',fontDiv='white',colorDiv='rgba(0,0,0,0.6)',city=city_element)
                else:
                    weather = {
                        'city' : loc_json['name'],
                        'temprature' : loc_json['main']['temp'],
                        'description' : loc_json['weather'][0]['description'],
                        'icon' : loc_json['weather'][0]['icon']
                    }
                    return render_template('search.html',weather=weather,background='night.jpg',theme='Theme: Nightfall',colorDiv='rgba(255,255,255,0.8)',fontDiv='black',city=city_element)
            else:
                weather={
                    'city' : "City could not be located. Please try again.",
                    'temprature' : '',
                    'description' : '',
                    'icon' : '',
                }
                return render_template('search.html',background='initial.jpg',theme='Theme: Default',fontDiv='white',colorDiv='rgba(0,0,0,0.6)',city=city_element)

"""
##############################################
##############################################
"""

"""
##############################################
Takes user to page displaying weather for their location
##############################################
"""

@app.route('/loc')
def loc_view():
    try:
        if session.get('username') is not None:
            return redirect(url_for('user'), code=301)
        else:
            session.pop('user',None)
            session.pop('username',None)
            raise Exception('Session User should not be None')
            return None
    except:
        url = 'http://api.ipstack.com/{}?access_key=7a87a908475dd3aa325ad0854b44b750&format=1&output=json'.format(request.remote_addr)
        r = requests.get(url).json()
        city_element = r['city']
        url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&APPID=594c7aab9fffecc844145f06d31f8c91&q={}'
        loc_json = requests.get(url.format(city_element)).json()
        ts = time.time()
        if(ts>=loc_json['sys']['sunrise'] and ts<=loc_json['sys']['sunset']):
            weather = {
                'city' : loc_json['name'],
                'temprature' : loc_json['main']['temp'],
                'description' : loc_json['weather'][0]['description'],
                'icon' : loc_json['weather'][0]['icon']
            }
            return render_template('search.html',weather=weather,background='daylight.jpg',theme='Theme: Daylight',fontDiv='white',colorDiv='rgba(0,0,0,0.6)')
        else:
            weather = {
                'city' : loc_json['name'],
                'temprature' : loc_json['main']['temp'],
                'description' : loc_json['weather'][0]['description'],
                'icon' : loc_json['weather'][0]['icon']
            }
            return render_template('search.html',weather=weather,background='night.jpg',theme='Theme: Nightfall',colorDiv='rgba(255,255,255,0.7)',fontDiv='black')

"""
########################################
########################################
"""

"""
########################################
Login Page
########################################
"""

@app.route('/login',methods=["POST","GET"])
def login_view():
    try:
        if session.get('username') is not None:
            return redirect(url_for('user'), code=301)
        else:
            session.pop('user',None)
            session.pop('username',None)
            raise Exception('Session User should not be None')
            return None
    except:
        url = 'http://api.ipstack.com/{}?access_key=7a87a908475dd3aa325ad0854b44b750&format=1&output=json'.format(request.remote_addr)
        r = requests.get(url).json()
        city_element = r['city']
        if request.method == 'GET':
            return render_template('login.html',background='initial.jpg',fontDiv = 'white',colorDiv = 'rgba(0,0,0,0.6)', theme = 'Theme: Default',city=city_element)
        elif request.method == 'POST':
            try:
                cursor = g.db.execute('SELECT password FROM user WHERE username = ?',[request.form['username']])
                passwordh = cursor.fetchall()
                if(check_password_hash(passwordh[0][0],request.form['pass'])):
                    session['username'] = request.form['username']
                    uid = g.db.execute('SELECT uid FROM user WHERE username = ?',[request.form['username']]).fetchall()
                    session['user'] = uid[0][0]
                    g.db.execute("INSERT INTO timeLog(loginTime,logoutTime,uid) VALUES((datetime('now')),NULL,?)",[uid[0][0]])
                    g.db.commit()
                    g.db.close()
                    return redirect(url_for('user'),code=301)
                else:
                    g.db.rollback()
                    message={
                        'error':'Incorrect Password. Please register if you are new to Weather Web',
                        'errorID':'PM101'
                    }
                    g.db.execute('INSERT INTO errorStack(errorID,errorMsg) VALUES(?,?)',[message['errorID'],message['error']])
                    g.db.commit()
                    g.db.close()
                    return render_template('login.html',background='initial.jpg',fontDiv = 'white',colorDiv = 'rgba(0,0,0,0.6)', theme = 'Theme: Default',city=city_element,hometown=city_element,message=message)
            except:
                g.db.rollback()
                message={
                    'error':'Please register first in case you are not a member of Weather Web.',
                    'errorID':'IE101'
                }
                g.db.execute('INSERT INTO errorStack(errorID,errorMsg) VALUES(?,"Possible Internal Error")',[message['errorID']])
                g.db.commit()
                g.db.close()
                return redirect(url_for('reg_view'))

"""
#########################################
#########################################
"""

"""
#########################################
Registration Page
#########################################
"""

@app.route('/register',methods=["POST","GET"])
def reg_view():
    try:
        if session.get('username') is not None:
            return redirect(url_for('user'), code=301)
        else:
            session.pop('user',None)
            raise Exception('Session User should not be None')
            return None
    except:
        url = 'http://api.ipstack.com/{}?access_key=7a87a908475dd3aa325ad0854b44b750&format=1&output=json'.format(request.remote_addr)
        r = requests.get(url).json()
        city_element = r['city']
        if request.method == 'GET':
            return render_template('register.html',background='initial.jpg',fontDiv = 'white',colorDiv = 'rgba(0,0,0,0.6)', theme = 'Theme: Default',city=city_element,hometown=city_element)
        elif request.method == 'POST':
            if request.form['pass'] == request.form['conf_pass']:
                try:
                    init_check = g.db.execute('SELECT COUNT(*) FROM user WHERE username = ?',[request.form['username']]).fetchall()
                    if init_check[0][0] == 0:
                        passwordh = generate_password_hash(request.form['pass'])
                        url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&APPID=594c7aab9fffecc844145f06d31f8c91&q={}'
                        loc_json = requests.get(url.format(city_element)).json()
                        if loc_json['cod'] == 200:
                            g.db.execute('INSERT INTO user(home,username,password) VALUES (?,?,?)',[request.form['home'],request.form['username'],passwordh])
                            g.db.commit()
                            session['username'] = request.form['username']
                            uid = g.db.execute('SELECT uid FROM user WHERE username = ?',[request.form['username']]).fetchall()
                            session['user'] = uid[0][0]
                            g.db.execute("INSERT INTO timeLog(loginTime,logoutTime,uid) VALUES((datetime('now')),NULL,?)",[uid[0][0]])
                            g.db.commit()
                            g.db.execute("INSERT INTO cities(uid) VALUES(?)",[session['user']])
                            g.db.commit()
                            g.db.close()
                            return redirect(url_for('user'),code=301)
                        else:
                            g.db.rollback()
                            message={
                                'error':'Home Town not found. Please try some other city.',
                                'errorID':'LE100'
                            }
                            g.db.execute('INSERT INTO errorStack(errorID,errorMsg) VALUES(?,?)',[message['errorID'],message['error']])
                            g.db.commit()
                            g.db.close()
                            return render_template('register.html',background='initial.jpg',fontDiv = 'white',colorDiv = 'rgba(0,0,0,0.6)', theme = 'Theme: Default',city=city_element,hometown=city_element,message=message)
                    else:
                        g.db.rollback()
                        message={
                            'error':'You seem to have an account with Weather Web already. Please try logging in.',
                            'errorID':'AC100'
                        }
                        g.db.execute('INSERT INTO errorStack(errorID,errorMsg) VALUES(?,?)',[message['errorID'],message['error']])
                        g.db.commit()
                        g.db.close()
                        return render_template('login.html',background='initial.jpg',fontDiv = 'white',colorDiv = 'rgba(0,0,0,0.6)', theme = 'Theme: Default',city=city_element,hometown=city_element,message=message)
                except:
                    g.db.rollback()
                    messageDisp={
                        'error': 'Registration Failed. Please try again.',
                        'errorID': 'IE100'
                    }
                    g.db.execute('INSERT INTO errorStack(errorID,errorMsg) VALUES(?,?)',[messageDisp['errorID'],messageDisp['error']])
                    g.db.commit()
                    g.db.close()
                    return render_template('register.html',message=messageDisp,background='initial.jpg',fontDiv = 'white',colorDiv = 'rgba(0,0,0,0.6)', theme = 'Theme: Default',city=city_element,hometown=city_element)
            else:
                g.db.rollback()
                messageDisp={
                    'error': 'Passwords didn\'t match. Please try again.',
                    'errorID': 'PM100'
                }
                g.db.execute('INSERT INTO errorStack(errorID,errorMsg) VALUES(?,?)',[messageDisp['errorID'],messageDisp['error']])
                g.db.commit()
                g.db.close()
                return render_template('register.html',message=messageDisp,background='initial.jpg',fontDiv = 'white',colorDiv = 'rgba(0,0,0,0.6)', theme = 'Theme: Default',city=city_element,hometown=city_element)



"""
########################################
########################################
"""

"""
########################################
Logged in View
########################################
"""

@app.route('/user',methods=["GET","POST"])
def user():
    try:
        if session.get('username') is not None:
            if request.method == 'GET':
                city_element = g.db.execute('SELECT home FROM user WHERE uid = ?',[session['user']]).fetchall()
                url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&APPID=594c7aab9fffecc844145f06d31f8c91&q={}'
                loc_json = requests.get(url.format(city_element[0][0])).json()
                ts = time.time()
                res = g.db.execute('SELECT city1,city2,city3,city4,city5 FROM cities WHERE uid = ?',[session['user']]).fetchall()
                resEdit = []
                for i in res[0]:
                    if i != 'None':
                        resEdit.append(i);
                if not resEdit:
                    if ts>=loc_json['sys']['sunrise'] and ts<=loc_json['sys']['sunset']:
                        weather = {
                            'city' : loc_json['name'],
                            'temprature' : loc_json['main']['temp'],
                            'description' : loc_json['weather'][0]['description'],
                            'icon' : loc_json['weather'][0]['icon']
                        }
                        kwargs={
                         'background' : 'daylight.jpg',
                         'theme' : 'Theme: Daylight',
                         'colorDiv': 'rgba(0,0,0,0.6)',
                         'fontDiv': 'white',
                         'user' : session['username']
                        }
                        return render_template('index.html', weather=weather, **kwargs)
                    else:
                        weather = {
                            'city' : loc_json['name'],
                            'temprature' : loc_json['main']['temp'],
                            'description' : loc_json['weather'][0]['description'],
                            'icon' : loc_json['weather'][0]['icon']
                        }
                        kwargs={
                         'background' : 'night.jpg',
                         'theme' : 'Theme: Nightfall',
                         'colorDiv': 'rgba(255,255,255,0.7)',
                         'fontDiv': 'black',
                         'user' : session['username'],
                         'notinList':'True'
                        }
                        header={'Content-Type':'text/html'}
                        return make_response(render_template('index.html', weather=weather, **kwargs),header)
                else:
                    if ts>=loc_json['sys']['sunrise'] and ts<=loc_json['sys']['sunset']:
                        weather = {
                            'city' : loc_json['name'],
                            'temprature' : loc_json['main']['temp'],
                            'description' : loc_json['weather'][0]['description'],
                            'icon' : loc_json['weather'][0]['icon']
                        }
                        kwargs={
                         'background' : 'daylight.jpg',
                         'theme' : 'Theme: Daylight',
                         'colorDiv': 'rgba(0,0,0,0.6)',
                         'fontDiv': 'white',
                         'user' : session['username'],
                         'citiesTab':resEdit
                        }
                        return render_template('index.html', weather=weather, **kwargs)
                    else:
                        weather = {
                            'city' : loc_json['name'],
                            'temprature' : loc_json['main']['temp'],
                            'description' : loc_json['weather'][0]['description'],
                            'icon' : loc_json['weather'][0]['icon']
                        }
                        kwargs={
                         'background' : 'night.jpg',
                         'theme' : 'Theme: Nightfall',
                         'colorDiv': 'rgba(255,255,255,0.7)',
                         'fontDiv': 'black',
                         'user' : session['username'],
                         'citiesTab' : resEdit
                        }
                        header={'Content-Type':'text/html'}
                        return make_response(render_template('index.html', weather=weather, **kwargs),header)

            elif request.method == 'POST':
                try:
                    if request.form['logout'] is not None:
                        g.db.execute("UPDATE timeLog SET logoutTime = (datetime('now')) WHERE uid = ? and logoutTime is null",[session['user']])
                        g.db.commit()
                        g.db.close()
                        session.pop('user',None)
                        session.pop('username',None)
                        return redirect(url_for('login_view'), code=301)
                    else:
                        return redirect(url_for('user'))
                except:
                    return redirect(url_for('user'))
        else:
            g.db.execute("INSERT INTO errorStack(errorID,errorMsg) VALUES('Illegal Login Attempt','IL101')")
            g.db.commit()
            g.db.close()
            return redirect(url_for('login_view'), code=301)
    except:
        g.db.execute("INSERT INTO errorStack(errorID,errorMsg) VALUES('Illegal Login Attempt','IL101')")
        g.db.commit()
        g.db.close()
        return redirect(url_for('login_view'), code=301)


"""
########################################
########################################
"""
@app.route('/suser',methods=['GET','POST'])
def suser():
    try:
        if session['username'] is not None:
            if request.method == 'GET':
                print(1)
                if request.args.get('search') is not None:
                    print(2)
                    city_element = request.args.get('search')
                    url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&APPID=594c7aab9fffecc844145f06d31f8c91&q={}'
                    loc_json = requests.get(url.format(city_element)).json()
                    ts = time.time()
                    res = g.db.execute('SELECT city1,city2,city3,city4,city5 FROM cities WHERE uid = ?',[session['user']]).fetchall()
                    print(3)
                    if request.args.get('search') in res[0]:
                        notinList = 'False'
                    else:
                        notinList = 'True'
                    if ts>=loc_json['sys']['sunrise'] and ts<=loc_json['sys']['sunset']:
                        weather = {
                            'city' : loc_json['name'],
                            'temprature' : loc_json['main']['temp'],
                            'description' : loc_json['weather'][0]['description'],
                            'icon' : loc_json['weather'][0]['icon']
                        }
                        kwargs={
                         'background' : 'daylight.jpg',
                         'theme' : 'Theme: Daylight',
                         'colorDiv': 'rgba(0,0,0,0.6)',
                         'fontDiv': 'white',
                         'user' : session['username'],
                         'notinList' : notinList,
                         'back':'True'
                        }
                        header={'Content-Type':'text/html'}
                        return make_response(render_template('index.html', weather=weather, **kwargs),header)
                    else:
                        weather = {
                            'city' : loc_json['name'],
                            'temprature' : loc_json['main']['temp'],
                            'description' : loc_json['weather'][0]['description'],
                            'icon' : loc_json['weather'][0]['icon']
                        }
                        kwargs={
                         'background' : 'night.jpg',
                         'theme' : 'Theme: Nightfall',
                         'colorDiv': 'rgba(255,255,255,0.7)',
                         'fontDiv': 'black',
                         'user' : session['username'],
                         'notinList':notinList,
                         'back':'True'
                        }
                        header={'Content-Type':'text/html'}
                        return make_response(render_template('index.html', weather=weather, **kwargs),header)
                else:
                    return render_template('initial.html',background='initial.jpg',theme='Theme: Default',colorDiv='rgba(0,0,0,0.6)',fontDiv='white')
            elif request.method == 'POST':
                city_element = request.form['search']
                url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&APPID=594c7aab9fffecc844145f06d31f8c91&q={}'
                loc_json = requests.get(url.format(city_element)).json()
                ts = time.time()
                if(loc_json['cod']==200):
                    res = g.db.execute('SELECT city1,city2,city3,city4,city5 FROM cities WHERE uid = ?',[session['user']]).fetchall()
                    if request.form['search'] in res[0]:
                        notinList = 'False'
                    else:
                        notinList = 'True'
                    if ts>=loc_json['sys']['sunrise'] and ts<=loc_json['sys']['sunset']:
                        weather = {
                            'city' : loc_json['name'],
                            'temprature' : loc_json['main']['temp'],
                            'description' : loc_json['weather'][0]['description'],
                            'icon' : loc_json['weather'][0]['icon']
                        }
                        kwargs={
                         'background' : 'daylight.jpg',
                         'theme' : 'Theme: Daylight',
                         'colorDiv': 'rgba(0,0,0,0.6)',
                         'fontDiv': 'white',
                         'user' : session['username'],
                         'notinList' : notinList
                        }
                        header={'Content-Type':'text/html'}
                        return make_response(render_template('index.html', weather=weather, **kwargs),header)
                    else:
                        weather = {
                            'city' : loc_json['name'],
                            'temprature' : loc_json['main']['temp'],
                            'description' : loc_json['weather'][0]['description'],
                            'icon' : loc_json['weather'][0]['icon']
                        }
                        kwargs={
                         'background' : 'night.jpg',
                         'theme' : 'Theme: Nightfall',
                         'colorDiv': 'rgba(255,255,255,0.7)',
                         'fontDiv': 'black',
                         'user' : session['username'],
                         'notinList':notinList
                        }
                        header={'Content-Type':'text/html'}
                        return make_response(render_template('index.html', weather=weather, **kwargs),header)
                else:
                    weather={
                        'city' : "City could not be located. Please try again.",
                        'temprature' : '',
                        'description' : '',
                        'icon' : '',
                    }
                    return render_template('index.html',background='initial.jpg',theme='Theme: Default',fontDiv='white',colorDiv='rgba(0,0,0,0.6)')
    except:
        return redirect(url_for('user'))


"""
#######################################
Add City
#######################################
"""

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method == 'GET':
        return redirect(url_for('user'),code=301)
    elif request.method == 'POST':
        res = g.db.execute('SELECT city1,city2,city3,city4,city5 FROM cities WHERE uid = ?',[session['user']]).fetchall()
        iters = 0
        for i in res[0]:
            iters += 1
            if(i=='None'):
                break;
        valueToBe = 'UPDATE cities SET city'+str(iters)+' = ? WHERE uid = ?'
        try:
            g.db.execute(valueToBe,[request.form['cityAdd'],session['user']])
            g.db.commit()
            g.db.close()
            return redirect(url_for('user'))
        except:
            return redirect(url_for('user'))

@app.route('/remove',methods=['GET','POST'])
def remove():
    if request.method == 'GET':
        return redirect(url_for('user'),code=301)
    elif request.method == 'POST':
        res = g.db.execute('SELECT city1,city2,city3,city4,city5 FROM cities WHERE uid = ?',[session['user']]).fetchall()
        iters = 0
        for i in res[0]:
            iters += 1
            if(i==request.form['cityRem']):
                break;
        valueToBe = "UPDATE cities SET city"+str(iters)+" = 'None' WHERE uid = ?"
        try:
            g.db.execute(valueToBe,[session['user']])
            g.db.commit()
            g.db.close()
            return redirect(url_for('user'))
        except:
            return redirect(url_for('user'))

"""
#######################################
#######################################
"""

"""
########################################
Port Creation and Hosting
########################################
"""

if __name__ == '__main__':
    app.debug = True
    app.secret_key = "b'J\x01\xe7M\x00\xd0\xb2\xc3-_\x7f\x87`\xca\xcc\\\x1b\x18\xd5\x11\x99LCh'"
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)

"""
##########################################
##########################################
"""
