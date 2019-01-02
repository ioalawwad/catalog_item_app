from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Item

engine = create_engine('sqlite:///finalProject.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# startups
user1 = User(name="Ibrahim", email='ibrahim@gmail.com')
session.add(user1)
session.commit()

categ2 = Category(name = 'Basketball')
categ1 = Category(name = 'Soccer')
categ3 = Category(name = 'Baseball')
categ4 = Category(name = 'Frisbee')
categ5 = Category(name = 'Snowboarding')
categ6 = Category(name = 'Rock Climning')
categ7 = Category(name = 'Foosball')
categ8 = Category(name = 'Skating')
categ9 = Category(name = 'Hockey')

session.add_all([categ1,categ2, categ3, categ4, categ5, categ6, categ7, categ8, categ9])
session.commit()

item1_1 = Item(name = 'Jersey', details = "A jersey is an item of knitted"
    "clothing,traditionally in wool or cotton, with sleeves, worn as a pullover"
    ", as it does not open at the front, unlike a cardigan. It is acommonly"
    " worn by sports teams as part of the team uniform, in team colors, often"
    " with a required number and optionally the player's name on the back."
    , category = categ1, user = user1)
item1_2 = Item(name = 'Foosball', details = "a piece of clothes that is made of"
    "rubble. This piece has the ability to keep air inside it for long time."
    , category = categ1, user = user1)
item5_1 = Item(name = 'Snowboard', details = "A flat long board that can smoothly move on snow"
    , category = categ5, user = user1)
session.add_all([item1_1, item1_2, item5_1])
session.commit()

print("some categories and items are just added!")
