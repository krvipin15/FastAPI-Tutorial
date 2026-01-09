"""
FastAPI development using Psycopg2 instead of SQLAlchemy
"""
import os
import time
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Access variables
DATABASE: str | None = os.getenv("DATABASE")
USER: str | None = os.getenv("USER")
PASSWORD: str | None = os.getenv("PASSWORD")
HOST: str | None = os.getenv("HOST")
PORT: str | None = os.getenv("PORT")

# Create a FastAPI instance
app: FastAPI = FastAPI()


# Create schema for posts
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


# Connect to your postgres DB
while True:
    try:
        conn = psycopg2.connect(
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Succesfully connected to the database")
        break
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}. Retrying in 2 seconds...")
        time.sleep(2)
    except psycopg2.Error as e:
        print(f"Database error occurred (non-recoverable): {e}")
        break
    except Exception as e:
        print(f"Unexpected error: {e}")
        break


# Home page
@app.get("/")
def root() -> str:
    return "Home Page"


# Retrieve all the posts
@app.get("/posts")
def get_posts() -> dict[str, list]:
    cursor.execute("""SELECT * FROM posts;""")
    posts: list = cursor.fetchall()
    return {"data": posts}


# Create a post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post) -> dict:
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *;""",
        (post.title, post.content, post.published),
    )
    cursor.connection.commit()
    new_post = cursor.fetchone()
    return {"new post": new_post}


# Retrieve a post by id
@app.get("/posts/{id}")
def get_post(id: int) -> dict:
    cursor.execute("""SELECT * FROM posts WHERE id = %s;""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found"
        )
    return {"post_detail": post}


# Delete a post by id
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int) -> None:
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (str(id)))
    cursor.connection.commit()
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post id with {id} not found"
        )
    return None


# Update a post by id
@app.put("/posts/{id}")
def update_post(id: int, post: Post) -> dict:
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(id)),
    )
    cursor.connection.commit()
    updated_post = cursor.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post id {id} not found")
    return {"updated post": updated_post}
