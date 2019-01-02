from flask import Flask, render_template, request, redirect, url_for,\
    flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import User, Category, Item, Base

from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import random
import string

app = Flask(__name__)

engine = create_engine('sqlite:///finalProject.db?check_same_thread=False')
DBSession = sessionmaker(bind=engine)
session = DBSession()

####
# setup for login through google
####
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "myfinalproject-224206"


# This method is for google login and copied from Udacity Calss
# with some alteration for upgrading to python3 and for saving user info to DB
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    # print(code)
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError as e:
        print(e)
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # h = httplib2.Http()
    # result = json.loads(h.request(url, 'GET'))
    result = json.loads(requests.get(url).text)
    print(result)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already '
                                            'connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    if 'name' in data:
        login_session['username'] = data['name']
    else:
        login_session['username'] = 'Name Is Not Available'
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    if session.query(User).filter_by(email=login_session['email']).first()\
            is None:
        newUser = User(name=login_session['username'],
                       email=login_session['email'])
        session.add(newUser)
        session.commit()
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'\
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# to disconnect users from the website. THis is taken from Udacity class with
# some adjustments
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    # if result['status'] == '200':
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    return redirect('/')


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# This is the first responder 'the home page'
@app.route('/')
def home():
    ItemList = []
    categList = session.query(Category).all()
    itemList = session.execute('select * from Item order by id desc limit 9')
    for item in itemList:
        for cat in categList:
            if item.categ_id == cat.id:
                ItemList.append([item.id, item.name, cat.name])

    return render_template('home.html', categs=categList, ItemList=ItemList,
                           login_session=login_session)


# this returns the items for a clicked catalog
@app.route('/<int:categ_id>/items')
def showItems(categ_id):
    categList = session.query(Category).all()
    categName = session.query(Category).filter_by(id=categ_id).first().name
    itemList = session.query(Item).filter_by(categ_id=categ_id).all()
    return render_template('categDetails.html', numOfEle=len(itemList),
                           categName=categName, itemList=itemList,
                           categList=categList, login_session=login_session)


# This method is got called when adding items
@app.route('/addItem', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], details=request.form['desc'],
                       categ_id=request.form['categ_id'],
                       user_id=login_session['email'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('home'))
    else:
        categList = session.query(Category).all()
        print(categList)
        return render_template('newItemForm.html', login_session=login_session,
                               categList=categList)


# This method is got called to show the description of an item
@app.route('/<int:item_id>')
def viewItem(item_id):
    s_item = session.query(Item).filter_by(id=item_id).first()
    return render_template('details.html', s_item=s_item,
                           login_session=login_session)


# This method is got called when editing an item
@app.route('/<int:item_id>/edit',  methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    # extra piece of security for checking if the user is authorized to edit
    # this item
    itemObj = session.query(Item).filter_by(id=item_id).first()
    if itemObj:
        if login_session['email'] != itemObj.user_id:
            return 'You are not authorized to delete this object'
    else:
        return 'Are you sure about the id you privided above'

    if request.method == 'POST':
        itemObj = session.query(Item).filter_by(id=item_id).first()
        itemObj.name = request.form['name']
        itemObj.details = request.form['desc']
        session.add(itemObj)
        session.commit()
        return redirect(url_for('viewItem', item_id=item_id))
    else:
        itemObj = session.query(Item).filter_by(id=item_id).first()
        return render_template('editItemForm.html', itemObj=itemObj)


# This method is got called when deleting an item
@app.route('/<int:item_id>/delete',  methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    # extra checking if the user trying to delete an item the does
    # not belong to him/her
    itemObj = session.query(Item).filter_by(id=item_id).first()
    if itemObj:
        if login_session['email'] != itemObj.user_id:
            return 'You are not authorized to delete this object'
    else:
        return 'Are you sure about the id you privided above'

    if request.method == 'POST':
        session.query(Item).filter_by(id=item_id).delete()
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('confirmDeletion.html', item_id=item_id)


# This method return a json formatted string contains all the Categories with
# their associated items
@app.route('/categ.json')
def allInJSON():
    # Here the backend goes only once to get the data from the database which
    # will be converted to json
    allCategories = session.query(Category).options(joinedload(Category.items)
                                                    ).all()
    return jsonify(dict(Catalog=[dict(cat.serialize, Items=[i.serialize
                                      for i in cat.items])
                        for cat in allCategories]))


# This method returns a JSON formatted string for the passed item
@app.route('/<int:item_id>/item.json')
def JSONperItem(item_id):
    singleItem = session.query(Item).filter_by(id=item_id).first()

    return jsonify(SingleItem=singleItem.serialize)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_complex_key'
    app.run(host='0.0.0.0', port=5001)
