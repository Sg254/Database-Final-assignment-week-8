from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./crudapp.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Models
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    patient = relationship("Patient")

Base.metadata.create_all(bind=engine)

# Schemas
class PatientSchema(BaseModel):
    name: str
    age: int
    class Config: orm_mode = True

class AppointmentSchema(BaseModel):
    date: str
    patient_id: int
    class Config: orm_mode = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD Endpoints
@app.post("/patients")
def create_patient(patient: PatientSchema):
    db = SessionLocal()
    new_patient = Patient(name=patient.name, age=patient.age)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.get("/patients", response_model=List[PatientSchema])
def get_patients():
    db = SessionLocal()
    return db.query(Patient).all()

@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, patient: PatientSchema):
    db = SessionLocal()
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_patient.name = patient.name
    db_patient.age = patient.age
    db.commit()
    db.refresh(db_patient)
    return db_patient

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    db = SessionLocal()
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(db_patient)
    db.commit()
    return {"message": "Patient deleted"}

@app.post("/appointments")
def create_appointment(appt: AppointmentSchema):
    db = SessionLocal()
    new_appt = Appointment(date=appt.date, patient_id=appt.patient_id)
    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)
    return new_appt

@app.get("/appointments", response_model=List[AppointmentSchema])
def get_appointments():
    db = SessionLocal()
    return db.query(Appointment).all()
  
