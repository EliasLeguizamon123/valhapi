from fastapi import HTTPException
from sqlalchemy.orm import Session
from sql_data.schemas.members import MemberCreate
from sql_data.models.members import Member as MemberModel

def get_member(db: Session, member_id: str):
    return db.query(MemberModel).filter(MemberModel.id == member_id).first()

def get_members(db: Session, skip: int = 0, limit: int = 100):
    db_members = db.query(MemberModel).offset(skip).limit(limit).all()
    return db_members if db_members else []

def create_member(db: Session, member: MemberCreate):
    existing_member = db.query(MemberModel).filter(MemberModel.id == member.id).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="Member ID already exists")

    db_member = MemberModel(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_member(db: Session, member: MemberCreate):
    db.query(MemberModel).filter(MemberModel.id == member.id).update(member.dict())
    db.commit()
    return db.query(MemberModel).filter(MemberModel.id == member.id).first()

