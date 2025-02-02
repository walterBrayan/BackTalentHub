from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Profile, Resume, Postulacion, WorkExperience, Education, Language, Certificate, Skill, SkillType, SkillCategory, StandardSkill
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from datetime import datetime
from flask import render_template, make_response
import pdfkit
from app.nlp_utils import analyze_profile_job
import json



# Cambiar config por pdfkit_config
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

routes = Blueprint('routes', __name__)
# Crear un Blueprint para las rutas principales
main_bp = Blueprint("main", __name__)

# Definir rutas
@main_bp.route("/")
def index():
    return "¡Bienvenido al backend de TalentHub!"

# Registro de usuarios
@routes.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(name=data['name'], email=data['email'], password_hash=hashed_password, phone=data['phone'], address=data['address'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

# Inicio de sesión
@routes.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=str(user.id))  # ✅ Convertir a string
        return jsonify({'access_token': access_token, "user_id": user.id}), 200
    return jsonify({'message': 'Credenciales inválidas'}), 401

# Obtener perfil del usuario
@routes.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        return jsonify({'linkedin_url': profile.linkedin_url, 'github_url': profile.github_url, 'headline': profile.headline}), 200
    return jsonify({'message': 'Perfil no encontrado'}), 404

# Crear o actualizar perfil
@routes.route('/api/profile', methods=['POST'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)
    profile.linkedin_url = data.get('linkedin_url')
    profile.github_url = data.get('github_url')
    profile.headline = data.get('headline')
    db.session.commit()
    return jsonify({'message': 'Perfil actualizado exitosamente'}), 200

# Obtener todos los CVs del usuario
@routes.route('/api/cvs', methods=['GET'])
@jwt_required()
def get_cvs():
    user_id = get_jwt_identity()
    resumes = Resume.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': r.id, 'title': r.title, 'description': r.description} for r in resumes]), 200

# Crear un nuevo CV
@routes.route('/api/cvs', methods=['POST'])
@jwt_required()
def create_cv():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_resume = Resume(user_id=user_id, title=data['title'], description=data.get('description'))
    db.session.add(new_resume)
    db.session.commit()
    return jsonify({'message': 'CV creado exitosamente'}), 201

# Actualizar un CV existente
@routes.route('/api/cvs/<int:id>', methods=['PUT'])
@jwt_required()
def update_cv(id):
    user_id = get_jwt_identity()
    resume = Resume.query.filter_by(id=id, user_id=user_id).first()
    if not resume:
        return jsonify({'message': 'CV no encontrado'}), 404
    data = request.get_json()
    resume.title = data.get('title', resume.title)
    resume.description = data.get('description', resume.description)
    db.session.commit()
    return jsonify({'message': 'CV actualizado exitosamente'}), 200

# Obtener todas las postulaciones
@routes.route('/api/applications', methods=['GET'])
@jwt_required()
def get_applications():
    user_id = get_jwt_identity()
    applications = Postulacion.query.filter_by(usuario_id=user_id).all()
    return jsonify([{'id': a.id, 'nombre_cargo': a.nombre_cargo, 'empresa': a.empresa, 'estado': a.estado} for a in applications]), 200

# Crear una nueva postulación
@routes.route('/api/applications', methods=['POST'])
@jwt_required()
def create_application():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_application = Postulacion(usuario_id=user_id, nombre_cargo=data['nombre_cargo'], empresa=data.get('empresa'), estado='En Progreso')
    db.session.add(new_application)
    db.session.commit()
    return jsonify({'message': 'Postulación creada exitosamente'}), 201

# Actualizar el estado de una postulación
@routes.route('/api/applications/<int:id>', methods=['PUT'])
@jwt_required()
def update_application(id):
    user_id = get_jwt_identity()
    application = Postulacion.query.filter_by(id=id, usuario_id=user_id).first()
    if not application:
        return jsonify({'message': 'Postulación no encontrada'}), 404
    data = request.get_json()
    application.estado = data.get('estado', application.estado)
    db.session.commit()
    return jsonify({'message': 'Estado de postulación actualizado exitosamente'}), 200

@routes.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    # Cargar relaciones de manera eager
    profile = Profile.query.options(
        joinedload(Profile.work_experiences)
    ).filter_by(user_id=user_id).first()

    # Obtener skills desde skill_categories
    tech_category = SkillCategory.query.filter_by(
        profile_id=profile.id,
        skill_type_id=1  # ID para habilidades técnicas
    ).first()
    
    soft_category = SkillCategory.query.filter_by(
        profile_id=profile.id,
        skill_type_id=2  # ID para habilidades blandas
    ).first()

    profile = Profile.query.filter_by(user_id=user_id).first()
    profile_data = {
        'nombre': user.name,
        'email': user.email,
        'telefono': user.phone,
        'direccion': user.address,
        'linkedin_url': profile.linkedin_url if profile else None,
        'github_url': profile.github_url if profile else None,
        'experiencia_laboral': [{
            'id': exp.id,  # <- Incluir el ID
            'empresa': exp.company,
            'cargo': exp.position,
            'fecha_inicio': exp.start_date.isoformat() if exp.start_date else None,
            'fecha_fin': exp.end_date.isoformat() if exp.end_date else None,
            'descripcion': exp.description,
            'trabajo_actual': exp.current_job
        } for exp in profile.work_experiences] if profile else [],
        'educacion': [{
            'institucion': edu.institution,
            'titulo': edu.degree,
            'fecha_inicio': edu.start_date.isoformat() if edu.start_date else None,
            'fecha_fin': edu.end_date.isoformat() if edu.end_date else None,
            'descripcion': edu.description
        } for edu in profile.educations] if profile else [],
        'idiomas': [{
            'idioma': lang.language,
            'nivel': lang.level
        } for lang in profile.languages] if profile else [],
        'certificados': [{
            'nombre': cert.name,
            'institucion': cert.institution,
            'fecha': cert.date.isoformat() if cert.date else None,
            'url': cert.url
        } for cert in profile.certificates] if profile else [],
        'habilidades': {
            'habilidades_tecnicas': tech_category.skills if tech_category else [],
        'habilidades_blandas': soft_category.skills if soft_category else []
        } 
    }
    return jsonify(profile_data), 200

@routes.route('/api/user/profile', methods=['POST'])
@jwt_required()
def update_user_profile():
    user_id = get_jwt_identity()
    data = request.get_json()

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)

    user.name = data.get('nombre', user.name)
    user.email = data.get('email', user.email)
    user.phone = data.get('telefono', user.phone)
    user.address = data.get('direccion', user.address)

    profile.linkedin_url = data.get('linkedin_url', profile.linkedin_url)
    profile.github_url = data.get('github_url', profile.github_url)

    db.session.commit()
    return jsonify({'message': 'Perfil actualizado exitosamente'}), 200


@routes.route('/api/user/work-experience', methods=['POST'])
@jwt_required()
def update_work_experience():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validación estricta
        if not isinstance(data, list):
            return jsonify({'message': 'Formato de datos inválido'}), 400

        for exp in data:
            if not all(key in exp for key in ['empresa', 'cargo', 'fechaInicio']):
                return jsonify({'message': 'Faltan campos requeridos'}), 400

            if not exp['empresa'].strip() or not exp['cargo'].strip():
                return jsonify({'message': 'Empresa y cargo no pueden estar vacíos'}), 400

            try:
                start_date = datetime.strptime(exp['fechaInicio'], '%Y-%m-%d').date()
                end_date = datetime.strptime(exp['fechaFin'], '%Y-%m-%d').date() if exp.get('fechaFin') else None
            except (ValueError, TypeError):
                return jsonify({'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'message': 'Perfil no encontrado'}), 404

        # Mapeo de IDs existentes
        existing_ids = {exp.id for exp in profile.work_experiences}
        received_ids = set()

        for exp_data in data:
            # Update o Create
            if exp_data.get('id') and exp_data['id'] in existing_ids:
                work_exp = WorkExperience.query.get(exp_data['id'])
                if not work_exp:
                    continue
            else:
                work_exp = WorkExperience(profile_id=profile.id)
                db.session.add(work_exp)

            # Asignación segura de valores
            work_exp.company = exp_data['empresa'].strip()
            work_exp.position = exp_data['cargo'].strip()
            work_exp.start_date = start_date
            work_exp.end_date = end_date
            work_exp.description = exp_data.get('descripcion', '')
            work_exp.current_job = exp_data.get('trabajoActual', False)

            received_ids.add(work_exp.id)

        # Eliminar registros no incluidos
        for exp in profile.work_experiences:
            if exp.id not in received_ids:
                db.session.delete(exp)

        db.session.commit()
        return jsonify({'message': 'Experiencia laboral actualizada exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en work-experience: {str(e)}")
        return jsonify({'message': 'Error interno del servidor'}), 500
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validación básica
        if not isinstance(data, list):
            return jsonify({'message': 'Formato de datos inválido'}), 400

        for exp in data:
            if not all(key in exp for key in ['empresa', 'cargo', 'fechaInicio']):
                return jsonify({'message': 'Faltan campos requeridos'}), 400
        
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'message': 'Perfil no encontrado'}), 404

        existing_ids = {exp.id for exp in profile.work_experiences}
        received_ids = set()

        for exp in data:
            # Validación de ID existente
            if 'id' in exp and exp['id'] is not None:
                work_exp = WorkExperience.query.filter_by(
                    id=exp['id'], 
                    profile_id=profile.id
                ).first()
                if not work_exp:
                    continue
                received_ids.add(exp['id'])
            else:
                work_exp = WorkExperience(profile_id=profile.id)
                db.session.add(work_exp)

            # ... lógica de actualización de campos

        # Eliminar experiencias no incluidas en el request
        for exp_id in existing_ids - received_ids:
            WorkExperience.query.filter_by(id=exp_id).delete()
            
        db.session.commit()
        return jsonify({'message': 'Experiencia laboral actualizada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({'message': 'Error interno del servidor'}), 500

@routes.route('/api/user/education', methods=['POST'])
@jwt_required()
def update_education():
    user_id = get_jwt_identity()
    data = request.get_json()

    try:
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'message': 'Perfil no encontrado'}), 404

        existing_ids = {edu.id for edu in profile.educations}
        received_ids = set()

        for edu in data:
            # Validación de campos requeridos
            if not all(key in edu for key in ['institucion', 'titulo', 'fecha_inicio']):
                return jsonify({'message': 'Faltan campos requeridos'}), 400

            # Conversión de fechas
            try:
                start_date = datetime.strptime(edu['fecha_inicio'], '%Y-%m-%d').date()
                end_date = datetime.strptime(edu['fecha_fin'], '%Y-%m-%d').date() if edu.get('fecha_fin') else None
            except (ValueError, TypeError):
                return jsonify({'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

            # Actualizar o crear registro
            if 'id' in edu and edu['id'] in existing_ids:
                education = Education.query.get(edu['id'])
                if not education:
                    continue
            else:
                education = Education(profile_id=profile.id)
                db.session.add(education)

            education.institution = edu['institucion']
            education.degree = edu['titulo']
            education.start_date = start_date
            education.end_date = end_date
            education.description = edu.get('descripcion', '')
            
            received_ids.add(education.id)

        # Eliminar registros no enviados
        for edu in profile.educations:
            if edu.id not in received_ids:
                db.session.delete(edu)

        db.session.commit()
        return jsonify({'message': 'Educación actualizada exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en educación: {str(e)}")
        return jsonify({'message': 'Error interno del servidor'}), 500

@routes.route('/api/user/languages', methods=['POST'])
@jwt_required()
def update_languages():
    user_id = get_jwt_identity()
    data = request.get_json()

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'message': 'Perfil no encontrado'}), 404

    for lang in data:
        if 'id' in lang:
            language = Language.query.get(lang['id'])
            if not language:
                continue
        else:
            language = Language(profile_id=profile.id)
            db.session.add(language)

        language.language = lang.get('idioma', language.language)
        language.level = lang.get('nivel', language.level)

    db.session.commit()
    return jsonify({'message': 'Idiomas actualizados exitosamente'}), 200


@routes.route('/api/user/certificates', methods=['POST'])
@jwt_required()
def update_certificates():
    user_id = get_jwt_identity()
    data = request.get_json()

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'message': 'Perfil no encontrado'}), 404

    for cert in data:
        if 'id' in cert:
            certificate = Certificate.query.get(cert['id'])
            if not certificate:
                continue
        else:
            certificate = Certificate(profile_id=profile.id)
            db.session.add(certificate)

        certificate.name = cert.get('nombre', certificate.name)
        certificate.institution = cert.get('institucion', certificate.institution)
        certificate.date = cert.get('fecha', certificate.date)
        certificate.url = cert.get('url', certificate.url)

    db.session.commit()
    return jsonify({'message': 'Certificados actualizados exitosamente'}), 200


@routes.route('/api/user/skills', methods=['POST'])
@jwt_required()
def add_skills():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        profile = Profile.query.filter_by(user_id=user_id).first()

        # Obtener skills actuales
        tech_category = SkillCategory.query.filter_by(
            profile_id=profile.id,
            skill_type_id=1
        ).first()
        
        soft_category = SkillCategory.query.filter_by(
            profile_id=profile.id,
            skill_type_id=2
        ).first()

        # Actualizar técnicas (combinar existentes + nuevas)
        if tech_category:
            current_tech = set(tech_category.skills)
            new_tech = set(data.get('tecnicas', []))
            tech_category.skills = list(current_tech.union(new_tech))
        else:
            tech_category = SkillCategory(
                profile_id=profile.id,
                skill_type_id=1,
                skills=data.get('tecnicas', [])
            )
            db.session.add(tech_category)

        # Actualizar blandas (combinar existentes + nuevas)
        if soft_category:
            current_soft = set(soft_category.skills)
            new_soft = set(data.get('blandas', []))
            soft_category.skills = list(current_soft.union(new_soft))
        else:
            soft_category = SkillCategory(
                profile_id=profile.id,
                skill_type_id=2,
                skills=data.get('blandas', [])
            )
            db.session.add(soft_category)

        db.session.commit()
        return jsonify({'message': 'Habilidades actualizadas exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Endpoint de búsqueda mejorado
@routes.route('/api/skills/search', methods=['GET'])
@jwt_required()
def search_skills():
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '').lower()
        skill_type = request.args.get('type')  # 'tech' o 'soft'
        
        # Obtener skills ya existentes del usuario
        profile = Profile.query.filter_by(user_id=user_id).first()
        skill_category = SkillCategory.query.filter_by(
            profile_id=profile.id,
            skill_type_id=1 if skill_type == 'tech' else 2
        ).first()
        existing_skills = skill_category.skills if skill_category else []

        # Buscar en standard_skills
        results = StandardSkill.query.filter(
            StandardSkill.normalized_name.ilike(f"%{query}%"),
            StandardSkill.skill_type_id == (1 if skill_type == 'tech' else 2),
            ~StandardSkill.normalized_name.in_(existing_skills)
        ).limit(10).all()

        return jsonify([{
            'value': skill.normalized_name,
            'label': skill.display_name,
            'type': 'tech' if skill.skill_type_id == 1 else 'soft'
        } for skill in results]), 200

    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")
        return jsonify([]), 200


@routes.route('/api/generate-cv/<int:user_id>', methods=['POST'])
def generate_cv(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos'}), 400

    job_title = data.get("job_title")
    job_description = data.get("job_description")

    # Obtener datos del usuario y perfil
    user = User.query.get_or_404(user_id)
    profile = Profile.query.options(
        joinedload(Profile.work_experiences),
        joinedload(Profile.educations),
        joinedload(Profile.languages),
        joinedload(Profile.certificates),
        joinedload(Profile.skill_categories)
    ).filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Perfil no encontrado"}), 404

    # Crear estructura de datos para el perfil
    profile_data = {
        "nombre": user.name,
        "contacto": {
            "correo": user.email,
            "telefono": user.phone,
            "linkedin": profile.linkedin_url  # Asume que tienes un campo linkedin en tu modelo de perfil
        },
        "experiencia_laboral": [
            {"empresa": exp.company, "cargo": exp.position, "descripcion": exp.description, "fecha_inicio": exp.start_date.strftime('%Y-%m-%d'), "fecha_fin": exp.end_date.strftime('%Y-%m-%d') if exp.end_date else "Actualidad"}
            for exp in profile.work_experiences
        ],
        "educacion": [
            {"institucion": edu.institution, "titulo": edu.degree, "fecha_inicio": edu.start_date.strftime('%Y-%m-%d'), "fecha_fin": edu.end_date.strftime('%Y-%m-%d') if edu.end_date else "En curso"}
            for edu in profile.educations
        ],
        "idiomas": [
            {"idioma": lang.language, "nivel": lang.level}
            for lang in profile.languages
        ],
        "certificaciones": [
            {"nombre": cert.name, "institucion": cert.institution, "fecha": cert.date.strftime('%Y-%m-%d')}
            for cert in profile.certificates
        ],
        "habilidades": [
            {"categoria": cat.skill_type.name, "lista": [skill.replace("_", " ").title() for skill in cat.skills]}
            for cat in profile.skill_categories
        ]
    }

    # Llamar a la función de análisis
    ai_data = analyze_profile_job(job_description, profile_data)

    if not ai_data:
        return jsonify({"error": "Error al obtener respuesta de la IA"}), 500

    # Generar el PDF con la información adaptada
    html = render_template(
        'cv_template.html',
        job_title=job_title,
        ai_data=ai_data,
        profile_data=profile_data
    )


    pdf = pdfkit.from_string(html, False, configuration=pdfkit_config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="cv_{user.name}_{job_title}.pdf"'
    return response



@routes.route('/api/user/skills', methods=['GET'])  
@jwt_required()
def get_user_skills():
    try:
        user_id = get_jwt_identity()
        profile = Profile.query.filter_by(user_id=user_id).first()
        
        # Obtener skills desde skill_categories
        tech_category = SkillCategory.query.filter_by(
            profile_id=profile.id,
            skill_type_id=1
        ).first()
        
        soft_category = SkillCategory.query.filter_by(
            profile_id=profile.id,
            skill_type_id=2
        ).first()

        return jsonify({
            'tecnicas': tech_category.skills if tech_category else [],
            'blandas': soft_category.skills if soft_category else []
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes.route('/api/skill_categories', methods=['GET'])
def get_skill_categories():
        categories = SkillCategory.query.all()
        return jsonify([{
        'id': c.id,
        'tipo': c.skill_type_id,  # Asumiendo que el campo se llama 'name' en tu modelo
        'descripcion': c.skills
} for c in categories]), 200

# Añade este endpoint

@routes.route('/api/skills', methods=['PUT'])
@jwt_required()
def update_skills():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        skill_type = data.get("type")  # "tech" o "soft"
        new_skills = data.get("skills", [])  # Lista de habilidades actualizadas

        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'error': 'Perfil no encontrado'}), 404
        
        # Determinar el skill_type_id
        skill_type_id = 1 if skill_type == "tech" else 2

        skill_category = SkillCategory.query.filter_by(
            profile_id=profile.id, skill_type_id=skill_type_id
        ).first()

        if skill_category:
            skill_category.skills = new_skills  # Sobrescribe el JSON
        else:
            # Si no existe, crea uno nuevo
            skill_category = SkillCategory(
                profile_id=profile.id, skill_type_id=skill_type_id, skills=new_skills
            )
            db.session.add(skill_category)

        db.session.commit()
        return jsonify({'message': 'Habilidades actualizadas'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    
