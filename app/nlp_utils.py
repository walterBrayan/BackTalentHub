import google.generativeai as genai
from collections import Counter
import json
import re

genai.configure(api_key="Token")

def analyze_profile_job(job_description, profile_data):
    """
    Analiza la descripción del puesto y el perfil profesional usando Gemini.
    """

    prompt = f"""
    Analiza la siguiente descripción de puesto y perfil profesional.

    Descripción del puesto:
    ```
    {job_description}
    ```

    Perfil profesional:
    ```
    {profile_data}
    ```

Realiza las siguientes tareas:

1. **Análisis semántico profundo:** Identifica las habilidades técnicas, herramientas, metodologías, tecnologías, conceptos y habilidades blandas más relevantes tanto en la descripción del puesto como en el perfil profesional.

    *   Evalúa la importancia de cada elemento en la descripción del puesto.
    *   Evalúa el nivel de dominio del candidato en el perfil profesional (experto, intermedio, básico) *basándote única y exclusivamente en la información proporcionada en el perfil*. **No asumas, infieras ni inventes ningún conocimiento, habilidad o experiencia que no esté explícitamente mencionado en el perfil. Esto es fundamental para la precisión y la honestidad de la evaluación.**

        *   **Criterios de evaluación del dominio:**
            *   **Experto:** El candidato ha demostrado un dominio profundo de la habilidad a través de múltiples experiencias laborales y/o proyectos relevantes. Para roles de *Head* o liderazgo, esto implica haber liderado equipos o proyectos complejos utilizando la habilidad en cuestión.
            *   **Intermedio:** El candidato tiene experiencia práctica con la habilidad y la ha utilizado de forma autónoma en proyectos o trabajos anteriores. Para roles de *Head* o liderazgo, esto implica haber aplicado la habilidad de forma autónoma en su trabajo.
            *   **Básico:** El candidato tiene conocimientos teóricos sobre la habilidad o la ha utilizado de forma limitada. Para roles de *Head* o liderazgo, esto implica un conocimiento introductorio o teórico de la habilidad.

        *   **Ejemplo:** Si el perfil menciona que el candidato ha trabajado con AWS durante 5 años y ha liderado proyectos de migración a la nube, su dominio de AWS podría considerarse "experto". Si el perfil menciona que el candidato ha tomado un curso sobre Python, pero no tiene experiencia laboral en programación, su dominio de Python podría considerarse "básico". Si el perfil no menciona experiencia en gestión de equipos, pero el puesto requiere liderazgo, el dominio de "liderazgo" debería considerarse "básico" o "nulo".

2. **Cálculo de la compatibilidad:** Calcula un porcentaje de compatibilidad general entre el perfil y el puesto, teniendo en cuenta la relevancia de las habilidades y el nivel de dominio del candidato. **Sé extremadamente honesto y preciso en tu evaluación. No exageres ni infles la compatibilidad. Si el candidato carece de habilidades o experiencia clave para el puesto, especialmente para roles de liderazgo como *Head*, refleja esto en un porcentaje de compatibilidad bajo (ej. menos del 50% si es el caso).**

3. **Sugerencias para la postulación:**
    *   Identifica las áreas del perfil que podrían mejorarse para aumentar la compatibilidad con el puesto. **Sé realista en tus sugerencias. No sugieras que el candidato destaque habilidades o experiencias que no posee. Concéntrate en cómo el candidato puede *presentar mejor* sus habilidades y experiencias *existentes* para resaltar su potencial. También puedes sugerir áreas de desarrollo a *futuro* si la compatibilidad es baja.**
    *   Genera sugerencias específicas para adaptar el currículum al puesto, incluyendo qué habilidades o experiencias resaltar, cómo cambiar la redacción de algunas frases y qué información adicional incluir.
    *   Genera una carta de presentación personalizada que destaque las habilidades y experiencias más relevantes para el puesto y que explique por qué el candidato es un buen ajuste, *siempre y cuando esto sea coherente con su nivel de dominio y experiencia real*.

4. **Generación de un CV adaptado al puesto con filtros ATS:**
    *   Genera un CV en formato de texto sin formato, optimizado para los sistemas de seguimiento de candidatos (ATS).
    *   Incluye las palabras clave más relevantes para el puesto de forma natural en el CV.
    *   Adapta el contenido del CV para resaltar las habilidades y experiencias más relevantes para el puesto, incluyendo la reordenación de secciones, la modificación de la redacción de algunas frases o la inclusión de nueva información.

    *   **No incluyas ninguna certificación, habilidad o experiencia que no esté presente en el perfil profesional. Esto es una restricción absoluta.**

El resumen profesional debe ser un reflejo *fiel* del perfil del candidato y no debe incluir ninguna información que no esté allí.

Devuelve **un JSON válido** con la siguiente estructura:

    ```json
    {{
      "compatibilidad": {{
        "porcentaje": 0%, este es el porcentaje de compatibilidad entre el perfil y el puesto, por lo tanto es variable 
        "detalle": Justifica el porcentaje de compatibilidad en base a la descripción del puesto y el perfil del candidato
      }},
      "sugerencias_postulacion": {{
        "areas_mejora": "Podría destacar su experiencia en A y B en el currículum, ya que son relevantes para el puesto. También sería útil mencionar su participación en el proyecto C, que demuestra habilidades de liderazgo.",
        "adaptacion_curriculum": "- Resaltar la habilidad X en la sección de 'Habilidades técnicas'.\n- Describir la experiencia en A utilizando palabras clave del puesto.\n- Incluir una sección sobre 'Proyectos personales' para mencionar el proyecto C.",
        "carta_presentacion": "Estimado [nombre del reclutador],\n\nEscribo para expresar mi interés en el puesto de [nombre del puesto].\n\n..."
      }},
      "cv_adaptado": {{
        "nombre": "[Nombre del candidato]",
        "contacto": {{
          "correo": "[Correo electrónico]",
          "telefono": "[Número de teléfono]",
          "linkedin": "[Enlace a LinkedIn]"
        }},
        "resumen": "[Resumen profesional adaptado al puesto]",
        "experiencia_laboral": "[Experiencia laboral adaptada al puesto]",
        "educacion": "[Educación]",
        "idiomas": "[Idiomas]",
        "certificaciones": "[Certificaciones]",
        "habilidades": "[Habilidades del candidato, no se deben cambiar ni agregar]"
      }}
    }}
    ```
    Asegúrate de que el JSON sea válido y esté bien formateado.
    """

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        # Extraer el JSON de la respuesta de Gemini
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            json_text = match.group(0)
            try:
                ai_data = json.loads(json_text)
                print("✅ Datos de IA extraídos:", ai_data)
                return ai_data
            except json.JSONDecodeError:
                print("❌ Error al decodificar JSON:", json_text)
                return None
        else:
            print("❌ No se encontró JSON válido en la respuesta de la IA.")
            return None

    except Exception as e:
        print("❌ Error al comunicarse con la IA:", e)
        return None
