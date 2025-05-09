import os
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email_found = Column(Boolean, default=False)
    email = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

# Create SQLite database engine
engine = create_engine('sqlite:///contacts.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def save_contact(name, email_found, email=None):
    session = Session()
    try:
        contact = Contact(
            id=name.lower().replace(" ", "_"),
            name=name,
            email_found=email_found,
            email=email,
            date=datetime.utcnow()
        )
        session.add(contact)
        session.commit()
        return True
    except Exception as e:
        print(f"Error saving contact: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def contact_exists(name):
    session = Session()
    try:
        contact = session.query(Contact).filter(Contact.name == name).first()
        return bool(contact)
    finally:
        session.close()

def cleanup_old_records():
    """Delete records older than 2 weeks"""
    session = Session()
    try:
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        session.query(Contact).filter(Contact.date < two_weeks_ago).delete()
        session.commit()
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        session.rollback()
    finally:
        session.close()
