from sqlalchemy.orm import Session

from sql_data.schemas.members import Member
from sql_data.models.members import Member as MemberModel

def get_member(db: Session, member_id: str):
    return db.query(MemberModel).filter(Member.id == member_id).first()

def get_members(db: Session, skip: int = 0, limit: int = 100):
    return db.query(MemberModel).offset(skip).limit(limit).all()

def create_member(db: Session, member: Member):
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def update_member(db: Session, member: Member):
    db.query(MemberModel).filter(Member.id == member.id).update(member.dict())
    db.commit()
    return member