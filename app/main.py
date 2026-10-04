from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Literal, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import time


while True:
    try:
        conn = psycopg2.connect(cursor_factory=RealDictCursor, database = 'campus_marketplace',  user = 'XXX', password = 'XXX',host = 'localhost')
        cursor = conn.cursor()
        print("Connected to Database Successfully")
        break
    except Exception as error:
        print(f"Couldnt connect to database")
        print(f"Error: {error}")
        time.sleep(4)

class Listing(BaseModel):
    title: str
    description: str
    price: int = Field(gt=0)
    category: Literal['textbooks','clothing','other','electronics'] = 'other'
    condition: Literal['new','like-new','used']
    seller_name :str
    is_sold : bool = False



app = FastAPI()

@app.get("/listings")
def get_all():
    cursor.execute("""SELECT * FROM listings;""")
    listing = cursor.fetchall()
    return {"data": listing}

@app.get("/listings/search")
def filter_by_query(max_price: Optional[int] = None, is_sold: Optional[bool] = None, category: Optional[Literal['textbooks','clothing','other','electronics']] = None):
    if max_price == None and is_sold == None and category == None:
        cursor.execute("""SELECT * FROM LISTINGS;""")
        listings = cursor.fetchall()
        return {"data": listings}
    query = "SELECT * FROM listings WHERE"
    values = []
    conditions = []
    if  max_price != None:
        values.append(max_price)
        conditions.append("price <=%s")
    if is_sold != None:
        values.append(is_sold)
        conditions.append("is_sold =%s ")
    if  category != None:
        values.append(category)
        conditions.append("category =%s")
    condition_query = " AND ".join(conditions)
    #print(f"{query} {condition_query}")
    cursor.execute(f"{query} {condition_query}", tuple(values))
    listings = cursor.fetchall()
    return {"data": listings}
@app.get("/listings/{id}")
def get_listing(id: int):
    cursor.execute("""SELECT * FROM listings WHERE id = %s;""", (str(id),))
    listing = cursor.fetchone()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Listing with ID: {id} doesn't exist")
    return {"data": listing}

@app.post("/listings", status_code=status.HTTP_201_CREATED)
def create_listing(listing: Listing):
    cursor.execute("""INSERT INTO listings(title, description,price,category,condition,seller_name,is_sold) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING * ;""",(listing.title, listing.description, listing.price, listing.category,listing.condition, listing.seller_name, listing.is_sold))
    new_listing = cursor.fetchone()
    conn.commit()
    return {"data": new_listing}

@app.put("/listings/{id}")
def update_listing(id: int, listing: Listing):
    cursor.execute("""UPDATE listings SET title = %s,description = %s,price = %s,category = %s,condition = %s,seller_name = %s,is_sold = %s WHERE id = %s RETURNING *;""",(listing.title, listing.description, listing.price, listing.category,listing.condition, listing.seller_name, listing.is_sold, str(id)))
    new_listing = cursor.fetchone()
    if not new_listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Listing with ID: {id} does not exist")
    conn.commit()
    return {"data": new_listing}

@app.delete("/listings/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(id: int):
    cursor.execute("""DELETE FROM listings WHERE id = %s RETURNING *; """, (str(id),))
    new_listing = cursor.fetchone()
    if not new_listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Listing with ID: {id} does not exist")
    conn.commit()

@app.patch("/listings/{id}/{new}")
def update_is_sold(id: int, new: bool):
    cursor.execute("""UPDATE listings SET is_sold = %s WHERE id = %s RETURNING *;""", (new,str(id)))
    updated_listing = cursor.fetchone()
    if not updated_listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Listing with ID: {id} does not exist")
    conn.commit()
    return {"data": updated_listing}

