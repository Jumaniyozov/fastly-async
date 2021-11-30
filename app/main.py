from fastapi.exceptions import HTTPException
from sqlalchemy.sql.expression import delete, select
from sqlalchemy import update
from starlette.responses import Response
from .schemas import Post
from .db import get_db
from . import models
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, status


app = FastAPI()


# @app.on_event("startup")
# async def startup_event():
#     async with engine.begin() as conn:
#         await conn.run_sync(models.Base.metadata.create_all)


@app.get("/")
async def home():
    return {"message": "hello world"}


@app.get('/posts')
async def get_all_posts(db: Session = Depends(get_db)):
    posts = await db.execute(select(models.Post))

    return {"data": posts.scalars().all()}


@app.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return {"data": new_post}


@app.get('/posts/{id}')
async def get_post(id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(models.Post).where(models.Post.id == id))
    post = result.scalar()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )

    return {"data": post}


@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(models.Post).where(models.Post.id == id))
    post = result.scalar()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )

    await db.execute(delete(models.Post).where(models.Post.id == id))
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/posts/{id}', status_code=status.HTTP_200_OK)
async def delete_post(id: int, post: Post, db: Session = Depends(get_db)):
    # result = await db.execute(select(models.Post).where(models.Post.id == id))
    # r_post = result.scalar()
    # print(r_post)

    # if r_post == None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"post with id: {id} was not found"
    #     )

    updated_result = await db.execute(update(models.Post).where(models.Post.id == id).values(**post.dict()).returning(models.Post))

    await db.commit()

    data = updated_result.fetchone()._asdict()

    return {"data": data}
