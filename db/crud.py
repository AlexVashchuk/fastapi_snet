from datetime import datetime
from fastapi import HTTPException
from psycopg2 import OperationalError
from sqlalchemy import and_


from db.db import SessionLocal
from models.models import User, Post, LikeDislike
from schemas.user_schema import UserInDB
from schemas.post_schema import PostUpdate, PostOnUpdate, PostInDBFull, LikesInDB


def create_session(model):
    session = SessionLocal()
    session.add(model)
    try:
        session.commit()
    except OperationalError as e:
        session.rollback()
        raise e.pgerror
    finally:
        session.close()


def create_user(user_dict: dict):
    create_session(User(**user_dict))


def delete_user(current_user: User):
    session = SessionLocal()
    user = session.query(User).filter(User.id == current_user.id).first()
    if not user:
        session.rollback()
    else:
        user.is_active = False
        session.commit()
    session.close()

    if user:
        return UserInDB(
            username=user.username, 
            id=user.id,
            is_active=user.is_active
            )
    return None
    

def user_by_username(name: str):
    session = SessionLocal()
    result = session.query(User).filter(User.username == name).first()
    session.close()
    if result:
        return result


def get_user_posts(name: str):
    author = user_by_username(name)
    session = SessionLocal()
    result = session.\
        query(Post.title, Post.text, Post.likes, Post.dislikes).\
            join(Post).filter(Post.user == author.id).all()
        
    session.close()
    if result:
        return result


def create_post(data: dict):
    data['date'] = datetime.now()
    create_session(Post(**data))


def get_post(post_id: int, user_id: int): 
    
    session = SessionLocal()
    res = [None, None]
    res[0] = session.query(Post, User).join(User, User.id == Post.user).filter(Post.id == post_id).first()
    if user_id:
        res[1] = session.query(LikeDislike).filter(and_(LikeDislike.post == post_id, LikeDislike.user == user_id)).first()
        if res[1] is None:
            res[1] = "no reaction"
    
    if res[0]:
        result = {
            'author': res[0][1].username, 'title': res[0][0].title, 'text': res[0][0].text,
            'likes': res[0][0].likes, 'dislikes': res[0][0].dislikes, 'date': res[0][0].date,
            'author_id': res[0][0].user
        }
        if res[1]:
            result['reaction'] = res[1].likedislike if type(res[1]) != str else res[1]
    
    else:
        result = None

    session.close()
    return (result)   


def update_post(post_id: int, user_id: int, data: PostUpdate):
    session = SessionLocal()

    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None

    if user_id != post.user:
        raise HTTPException(status_code=400, detail="You cannot edit someone else's text")
    _ = [setattr(post, item[0], item[1]) for item in data if item[1]]
    if _:
        post.likes = 0
        post.dislikes = 0
        post.date = datetime.now()   
        session.query(LikeDislike).filter_by(post = post_id).delete(synchronize_session=False)
        
    
    result = {
        'title': post.title, 'text': post.text, 'date': post.date,
        'author_id': post.user, 'likes': post.likes, 'dislikes': post.dislikes,
    }

    session.commit()
    session.close()
    return PostOnUpdate(**result)


def delete_post(post_id: int, current_user: int):
    result = None
    session = SessionLocal()
    post = session.query(Post).filter(Post.id == post_id).first()
    
    if post:
        if current_user != post.user:
            session.rollback()
            session.close()
            raise HTTPException(status_code=400, detail="You cannot delete someone else's text")

        post.deleted_at = datetime.now()
        result = {
            'title': post.title, 'text': post.text, 'date': post.date,
            'author_id': post.user, 'likes': post.likes, 'dislikes': post.dislikes,
            'id': post.id, 'deleted_at': post.deleted_at
        }
        session.commit()
    else:
        session.rollback()
    session.close()

    if result:
        return PostInDBFull(**result)

    return  None
    

def like(post_id: int, current_user: int):
    return likes(post_id, current_user, 'like')


def dislike(post_id: int, current_user: int):
    return likes(post_id, current_user, 'dislike')


def likes(post_id: int, current_user:int, action):
    """
    Change data about likes and dislakes based on flags in passed from single name func
    """
    like_dislike_resp = {}
    lds, anti_lds = False, True
    if action == 'like':
        lds, anti_lds = True, False
    

    session = SessionLocal()
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post or post.deleted_at != None:
        session.rollback()
        session.close()
        raise HTTPException(status_code=400, detail="Post not found")

    if post.user == current_user.id:
        session.rollback()
        session.close()
        raise HTTPException(status_code=405, detail=f"You cannot {action} your own posts")

    rec = session.query(LikeDislike).filter(
        and_(LikeDislike.post == post_id, LikeDislike.user == current_user.id)).first()
    
    if not rec:
        if lds == True:
            post.likes += 1
        else:
            post.dislikes += 1
        
        session.add(LikeDislike(user=current_user.id, post=post_id, likedislike=lds))
        like_dislike_resp = {'reaction':lds, 'description': f'You {action} this post'}


    else:
        if rec.likedislike == lds:
            if lds == True:
                post.likes -= 1
            else:
                post.dislikes -= 1
            like_dislike_resp = {'reaction': 'No reaction', 'description': 'You have no reaction for this post'}
            session.delete(rec)
            session.commit()
            session.close()


        if rec.likedislike == anti_lds:
            rec.likedislike = lds
            if lds == True:
                post.likes += 1
                post.dislikes -= 1
            else:
                post.dislikes += 1
                post.likes -= 1
            like_dislike_resp = {'reaction':lds, 'description': f'You {action} this post'}

    session.commit()
    session.close()
    return LikesInDB(user_id=current_user.id, post_id=post_id, **like_dislike_resp)
