from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    level = Column(String)
    preparation_time = Column(String)
    ready_in = Column(String)
    serves = Column(String)
    dish_type = Column(String)
    season = Column(String)
    course = Column(String)
    main_ingredient = Column(String)
    ingredients = relationship('RecipeIngredient', back_populates='recipe')
    preparation_steps = relationship('PreparationStep', back_populates='recipe')
    nutritional_info = relationship('NutritionalInfo', back_populates='recipe', uselist=False)

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    measurement = Column(String)
    amount = Column(String)
    recipe = relationship('Recipe', back_populates='ingredients')
    ingredient = relationship('Ingredient')
    __table_args__ = (
        Index('idx_recipe_id', 'recipe_id'),
        Index('idx_ingredient_id', 'ingredient_id'),
    )

class PreparationStep(Base):
    __tablename__ = 'preparation_steps'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    step_number = Column(Integer)
    description = Column(String)
    recipe = relationship('Recipe', back_populates='preparation_steps')

class NutritionalInfo(Base):
    __tablename__ = 'nutritional_info'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    sodium_amount = Column(Float)
    sodium_unit = Column(String)
    protein_amount = Column(Float)
    protein_unit = Column(String)
    calories = Column(Float)
    total_fat_amount = Column(Float)
    total_fat_unit = Column(String)
    recipe = relationship('Recipe', back_populates='nutritional_info')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    quantity = Column(Float)
    unit = Column(String)

# Create an engine and bind the session
engine = create_engine('sqlite:///recipes.db')
Session = sessionmaker(bind=engine)
session = Session()

# Create tables
Base.metadata.create_all(engine)

# Paths to the input files and the output file
merged_file_path = 'scrape/all_recipe_data.json'

# Load the contents of the first file
with open(merged_file_path, 'r') as file:
    data = json.load(file)


# Parse and seed data into the database
def seed_database(data):
    # Check if ingredient exists, if not, add it
    def get_or_create_ingredient(session, name):
        ingredient = session.query(Ingredient).filter_by(name=name).first()
        if not ingredient:
            ingredient = Ingredient(name=name)
            session.add(ingredient)
            session.commit()
        return ingredient

    for d in data:
        recipe = Recipe(
            name=d['title'],
            level=d['details']['Level'],
            preparation_time=d['details']['Preparation'],
            ready_in=d['details']['Ready in'],
            serves=d['details']['Serves'],
            dish_type=d['details']['Dish Type'],
            season=d['details']['Season'],
            course=d['details']['Course'],
            main_ingredient=d['details']['Main Ingredient']
        )
        session.add(recipe)
        
        for i, ingredient_data in enumerate(d['ingredients'], start=1):
            ingredient = get_or_create_ingredient(session, ingredient_data['name'])
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                measurement=ingredient_data.get('measurement', ''),
                amount=ingredient_data['amount']
            )
            session.add(recipe_ingredient)
        
        for i, step in enumerate(d['preparation_steps'], start=1):
            preparation_step = PreparationStep(
                recipe=recipe,
                step_number=i,
                description=step
            )
            session.add(preparation_step)
        
        nutritional_info = NutritionalInfo(
            recipe=recipe,
            sodium_amount=float(d['nutritional_info']['Sodium']['amount'].replace(",", "").replace("mg", "")),
            sodium_unit=d['nutritional_info']['Sodium']['unit'],
            protein_amount=float(d['nutritional_info']['Protein']['amount'].replace("g", "")),
            protein_unit=d['nutritional_info']['Protein']['unit'],
            calories=float(d['nutritional_info']['Calories']['amount']),
            total_fat_amount=float(d['nutritional_info']['Total Fat']['amount'].replace("g", "")),
            total_fat_unit=d['nutritional_info']['Total Fat']['unit']
        )
        session.add(nutritional_info)

        session.commit()
    
# Assuming the JSON data is loaded into `data`
seed_database(data)
