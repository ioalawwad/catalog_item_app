# Item Catalog (final project)
This is the final project for the full stack web developer Nanodegree. In this project, we provide a website for categories of sports and activity and each category has items underneath it; each item has some description.

In more details, when you click on a category a list of items related to that category appears. And when you click on an item a new page with the description appears.

The authorization point of view of the project: a user needs to be logged in to be able to add an item. An item can be edited or deleted only by the owner of this item.

The app provide an API for JSON formatted string for all the categories details including their associated items. To

## The Setup:
- add this project inside this VM machine: [download](https://github.com/udacity/fullstack-nanodegree-vm)
- install python 3
- install the following models:
  * flask using this command `sudo pip3 install flask`
  * sqlalchemy using this command `sudo pip3 install sqlalchemy`
  * oauth2client using this command `sudo pip3 install oauth2client`

## Steps to run the project
- create the database: `python database_setup.py`
- seed it: `python seeder.py`
- run the app: `python finalProject.py`
- open the browser and put this url: [http://localhost:5001](http://localhost:5001)
- for using the API for getting all the content in JSON formatted string use this url:
  [http://localhost:5001/categ.json](http://localhost:5001/categ.json)
- Another API for retrieving single item in a JSON formatted string change item id to the id of your target item:
  [http://localhost:5001/item id/item.json](http://localhost:5001/1/item.json)
# catalog_item_app
