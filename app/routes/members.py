from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from sql_data.schemas.members import Member, MemberCreate
from sql_data.crud.members import get_members, create_member, get_member
from sql_data.config import SessionLocal

router = APIRouter()

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/members/", response_model=Member)
def create_new_member(Member: MemberCreate, db: Session = Depends(get_db)):
    return create_member(db=db, Member=Member)

@router.get("/members/", response_model=List[Member])
def get_all_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_members(db, skip=skip, limit=limit)

@router.get("/members/{member_id}", response_model=Member)
def get_member_by_id(member_id: str, db: Session = Depends(get_db)):
    db_member = get_member(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

