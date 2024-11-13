from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from sql_data.schemas.members import Member, MemberCreate
from sql_data.models.members import Member as MemberModel
from sql_data.crud.members import get_members, create_member, get_member, update_member
from sql_data.config import SessionLocal

router = APIRouter()

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/", response_model=Member)
def create_new_member(member: MemberCreate, db: Session = Depends(get_db)):
    try:
        existing_member = db.query(MemberModel).filter(MemberModel.id == member.id).first()
        if existing_member:
            raise HTTPException(status_code=400, detail="Member ID already exists")

        db_member = MemberModel(**member.dict())
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", response_model=List[Member])
def get_all_members(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(MemberModel)
    
    if search:
        query = query.filter(
            (MemberModel.first_name.ilike(f"%{search}%")) | 
            (MemberModel.id == search) | 
            (MemberModel.last_name.ilike(f"%{search}%"))
        )
    
    members = query.offset(skip).limit(limit).all()
    return members


@router.get("/{member_id}", response_model=Member)
def get_member_by_id(member_id: str, db: Session = Depends(get_db)):
    db_member = get_member(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member


@router.put("/{member_id}", response_model=Member)
def modify_member(member_id: str, member: MemberCreate, db: Session = Depends(get_db)):
    db_member = get_member(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    if member_id != member.id:
        raise HTTPException(status_code=400, detail="Member ID cannot be modified")
    return update_member(db, member)

@router.delete("/{member_id}")
def delete_member(member_id: str, db: Session = Depends(get_db)):
    db_member = get_member(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    db.query(MemberModel).filter(MemberModel.id == member_id).delete()
    db.commit()
    return {"message": "Member deleted successfully"}