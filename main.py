import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import security.auth as auth
import db.crud as cr


from schemas.user_schema import User, UserToDB
from schemas.post_schema import Post, PostInDB, PostInDBExt, PostUpdate


app = FastAPI()


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    user = cr.user_by_username(form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not auth.check_hash(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")   
async def read_users_me(current_user: User = Depends(auth.get_current_active_user)):
    return current_user


@app.post("/user/new")
async def new_user(user: UserToDB, no_user: None = Depends(auth.get_no_user)):

    if user.password != user.repeat:
        raise HTTPException(status_code=400, detail="Password in not repeated")

    if cr.user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    cr.create_user(
        {
            'username':user.username, 
            'hashed_password':auth.gen_hash(user.password)
        })
    return {"username": user.username}


@app.post("user/{id}/delete")
async def delete_user(current_user: User = Depends(auth.get_current_active_user)):
    return delete_user(current_user)


@app.post("/posts/new")
async def new_post(post: Post, current_user = Depends(auth.get_current_active_user)):
    if len(post.title) > 50:
        raise HTTPException(status_code=400, detail="Title must have 50 symbols max")
    if len(post.text) > 350:
        raise HTTPException(status_code=400, detail="Post body must have 350 symbols max")
    cr.create_post(
        {
            'title': post.title,
            'text': post.text,
            'user': current_user.id
        }
    )
    return {"title": post.title, "status": "created"}


@app.get("/user/posts/{author}")
async def user_posts(author: str):
    if not cr.user_by_username(author):
        raise HTTPException(status_code=400, detail="Author not found")
    return cr.get_user_posts(author)


@app.get("/posts/{id}")
async def get_post(id: int, current_user: User | None = Depends(auth.get_read_mode)):

    user = current_user.id if current_user else None
    result =  cr.get_post(id, user)
    if not result:
        raise HTTPException(status_code=400, detail="Post not found")
    
    if user:
        if user == result['author_id']:
            result['reaction'] = "It's your post"
        return PostInDBExt(**result)
    
    return PostInDB(**result)


@app.post("/posts/{id}")
async def update_post(data: PostUpdate, id: int, current_user = Depends(auth.get_current_active_user)):
    result = cr.update_post(id, current_user.id, data)
    if not result:
        raise HTTPException(status_code=400, detail="Post not found")
    return result


@app.post("/posts/delete/{id}")
async def delete_post(id: int, current_user = Depends(auth.get_current_active_user)):
    result = cr.delete_post(id, current_user.id)
    if not result:
        raise HTTPException(status_code=400, detail="Post not found")
    return result


@app.post("/posts/{id}/like")
async def like(id: int, current_user = Depends(auth.get_current_active_user)):
    return cr.like(id, current_user)


@app.post("/posts/{id}/dislike")
async def like_post(id: int, current_user = Depends(auth.get_current_active_user)):
    return cr.dislike(id, current_user)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
