from datetime import datetime, date
from app import db
from sqlalchemy.dialects.postgresql import JSONB

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    preferred_language = db.Column(db.String(10), default='es')
    dark_theme = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    profile = db.relationship("Profile", back_populates="user", uselist=False)
    resumes = db.relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    postulaciones = db.relationship("Postulacion", backref="usuario")
    job_applications = db.relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    linkedin_url = db.Column(db.Text)
    github_url = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    headline = db.Column(db.String(255))
    availability_status = db.Column(db.String(50))
    preferred_work_type = db.Column(db.String(20))

    # Relación con el modelo User
    user = db.relationship("User", back_populates="profile")

    # Relaciones con WorkExperience, Education, Language, Skill, Certificate
    work_experiences = db.relationship("WorkExperience", back_populates="profile", cascade="all, delete-orphan")
    educations = db.relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    languages = db.relationship("Language", back_populates="profile", cascade="all, delete-orphan")
    skill_categories = db.relationship("SkillCategory", back_populates="profile", cascade="all, delete-orphan")
    certificates = db.relationship("Certificate", back_populates="profile", cascade="all, delete-orphan")
    skills = db.relationship("Skill", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Profile {self.id}>"

class WorkExperience(db.Model):
    __tablename__ = 'work_experience'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text)
    current_job = db.Column(db.Boolean, default=False)

    # Relación con el modelo Profile
    profile = db.relationship("Profile", back_populates="work_experiences")

    def __repr__(self):
        return f"<WorkExperience {self.position} at {self.company}>"

class Education(db.Model):
    __tablename__ = 'education'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)

    # Relación con el modelo Profile
    profile = db.relationship("Profile", back_populates="educations")

    def __repr__(self):
        return f"<Education {self.degree} at {self.institution}>"

class Language(db.Model):
    __tablename__ = 'languages'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)

    # Relación con el modelo Profile
    profile = db.relationship("Profile", back_populates="languages")

    def __repr__(self):
        return f"<Language {self.language} ({self.level})>"

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)

    # Relación con el modelo Profile
    profile = db.relationship("Profile", back_populates="skills")

    def __repr__(self):
        return f"<Skill {self.name} ({self.type})>"

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')
    file_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con el modelo User
    user = db.relationship("User", back_populates="resumes")

    # Relación con el modelo JobApplication
    job_applications = db.relationship("JobApplication", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume {self.title}>"

class Postulacion(db.Model):
    __tablename__ = 'postulaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nombre_cargo = db.Column(db.String(200), nullable=False)
    empresa = db.Column(db.String(200))
    link = db.Column(db.String(500))
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(50), default="En Progreso")

    def __repr__(self):
        return f"<Postulacion {self.nombre_cargo} at {self.empresa}>"

class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    job_url = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    match_percentage = db.Column(db.Integer)
    application_deadline = db.Column(db.Date)
    source = db.Column(db.String(50))

    # Relación con el modelo User
    user = db.relationship("User", back_populates="job_applications")

    # Relación con el modelo Resume
    resume = db.relationship("Resume", back_populates="job_applications")

    def __repr__(self):
        return f"<JobApplication {self.position} at {self.company}>"

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date)
    url = db.Column(db.Text)

    # Relación con el modelo Profile
    profile = db.relationship("Profile", back_populates="certificates")

    def __repr__(self):
        return f"<Certificate {self.name} from {self.institution}>"
    
class SkillType(db.Model):
    __tablename__ = 'skill_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)  # 'Técnica' o 'Blanda'

class SkillCategory(db.Model):
    __tablename__ = 'skill_categories'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    skill_type_id = db.Column(db.Integer, db.ForeignKey('skill_types.id'), nullable=False)
    skills = db.Column(JSONB)
    
    profile = db.relationship("Profile", back_populates="skill_categories")
    skill_type = db.relationship("SkillType")

class StandardSkill(db.Model):
    __tablename__ = 'standard_skills'
    id = db.Column(db.Integer, primary_key=True)
    normalized_name = db.Column(db.String(100), unique=True)  # "reactjs"
    display_name = db.Column(db.String(100))  # "React.js"
    skill_type_id = db.Column(db.Integer, db.ForeignKey('skill_types.id'))
    
    skill_type = db.relationship("SkillType")