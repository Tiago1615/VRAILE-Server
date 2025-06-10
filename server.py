import json
import base64
import io
import os
from dotenv import load_dotenv
import random
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
import boto3

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
POLLY_ACCES_KEY = os.getenv("ACCESS_KEY")
POLLY_SECRET_KEY = os.getenv("SECRET_KEY")

if not API_KEY or not POLLY_ACCES_KEY or not POLLY_SECRET_KEY:
    raise ValueError("Missing required environment variables: OPENAI_API_KEY, ACCESS_KEY, SECRET_KEY")

with open("config.json") as config_file:
    data = json.load(config_file)

SERVER_IP = data["SERVER_IP"]

if SERVER_IP == "YOUR_SERVER_IP_HERE":
    raise ValueError("Please set your server IP in config.json")

client = OpenAI()

polly_client = boto3.client(
    "polly",
    region_name="eu-central-1",
    aws_access_key_id=POLLY_ACCES_KEY,
    aws_secret_access_key=POLLY_SECRET_KEY
)

app = Flask(__name__)

NPC_Voices = {
    0: {"Voice":"Sergio"},
    1: {"Voice":"Andres"},
    2: {"Voice":"Mia"},
    3: {"Voice":"Pedro"},
    4: {"Voice":"Lupe"},
    5: {"Voice":"Lucia"},
}

symptoms = {
    # Hipertensión
    0: "mareos, visión borrosa, zumbido de oídos, fatiga, confusión, pérdida de la consciencia, dolor en el pecho, palpitacoines, orina espumosa",

    # Migraña
    1: "dolor de cabeza intenso y punzante, molestia con la luz, molestia con los ruidos, náuseas o vómitos, molestias oculares: destellos, visión borrosa o líneas en zigzag",

    # Apendicitis
    2: "dolor abdominal punzante o tipo cólico, náuseas, vomitos, pérdida de apetito, fiebre, sensibilidad en el abdomen, dificultad para moverse o caminar por el dolor",

    # VIH/SIDA
    3: "fiebre, dolor de garganta, fatiga, dolor muscular o articular, pérdida de peso, sudores nocturnos, diarrea crónica, lesiones en piel, infecciones respiratorias recurrentes",

    # COVID-19
    4: "fiebre, tos seca, dificultad para respirar, fatiga, dolor de garganta, dolor muscular, pérdida del gusto o el olfato, congestión nasal, diarrea, náuseas o vómitos",

    # Pediatría (Bronquiolitis)
    5: "congestión nasal, tos persistente, dificultad para respirar, fiebre, irritabilidad o letargo, pérdida del apetito, silbidos al respirar",
}

examples = {
    # Hipertensión
    0: {
        0: "Doctor, ultimamente me duele mucho la cabeza, sobre todo en las mañanas",
        1: "A veces siento que me zumban los oidos y me mareo al levantarme.",
        2: "He notado que se me hinchan los pies por las tardes.",
        3: "Me canso muy rapido al subir escaleras.",
    },

    # Migraña
    1: {
        0: "Doctor, siento un dolor muy fuerte en un lado de la cabeza, como si me latiera.",
        1: "La luz y los ruidos me molestan mucho cuando me duele la cabeza.",
        2: "Antes de que me empiece el dolor, veo luces raras o destellos.",
        3: "A veces tengo que acostarme en un lugar oscuro porque no soporto el dolor.",
    },

    # Apendicitis
    2: {
        0: "Doctor, me empezó un dolor en la parte alta del estómago y ahora lo siento mas abajo, a la derecha.",
        1: "No tengo nada de apetito desde que empece con el dolor.",
        2: "Me siento con náuseas y he vomitado alguna que otra una vez.",
        3: "Me duele más cuando camino o cuando toco la zona.",
    },

    # VIH/SIDA
    3: {
        0: "Doctor, me siento muy cansado desde hace varias semanas y he bajado de peso.",
        1: "Últimamente sudo mucho por las noches y me despierto empapado.",
        2: "He tenido varias infecciones y me cuesta recuperarme.",
        3: "Me han salido unas manchas raras en la piel.",
    },

    # COVID-19
    4: {
        0: "Doctor, me siento muy cansado y me cuesta respirar, como si me faltara el aire.",
        1: "Llevo varios días con fiebre y no se me va con nada.",
        2: "Perdí completamente el olfato y el gusto desde ayer.",
        3: "Estoy tosiendo mucho, pero no me sale nada.",
    },

    # Pediatría
    5: {
        0: "Mi pequeño se queja de dolor de barriga...",
        1: "He visto como tiembla de frío y ha perdido el apetito.",
        2: "Está muy cansado y solo quiere dormir.",
        3: "Respirar le cuesta un poco y tiene tos.",
    },
}

patientList = random.sample(list(symptoms.keys()), len(symptoms))
currentIndex = 0
patientVoice = "Sergio"

messages = []

@app.route("/chat", methods=["POST"])
def chat():
    input = request.json.get("input", "").lower()

    if not input:
        return jsonify({"error": "No input provided"}), 400
    
    if input == "exit":
        return jsonify({"message": "Connection closed"}), 200
    
    messages.append({
        "role": "user",
        "content": input
    })

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    response = completion.choices[0].message.content
    messages.append({
        "role": "assistant",
        "content": response
    })

    return jsonify({"response": response}), 200

@app.route("/cehck-status", methods=["GET"])
def check_status():
    status_openai, code = check_openai_status()
    if status_openai is False:
        if code == 1:
            return jsonify({"status": "OpenAI is down"}), 503
        elif code == 2:
            return jsonify({"status": "Error checking OpenAI status"}), 500
    
    return jsonify({"status": "OpenAI is up"}), 200

def check_openai_status():
    """
    retrun False, 1 if OpenAI is down
    retrun True, 0 if OpenAI is up
    retrun False, 2 if there was an error checking the status
    """
    end_point = "https://status.openai.com/api/v2/summary.json"
    try:
        response = requests.get(end_point)
        response.raise_for_status()

        data = response.json()
        status = data.get("status", {}).get("indicator")

        if status != "none":
            return False, 1
        
        return True, 0
    except Exception as e:
        return False, 2

@app.route("/set-up", methods=["GET"])
def set_up():
    try:
        global patientList, currentIndex, patientVoice, pediatrics

        if currentIndex >= len(patientList):
            return jsonify({"message": "No more patients"}), 200
        
        patient = patientList[currentIndex]
        print("Current patient: ", patient)
        patientSymptoms = symptoms[patient]
        patientPhraseExample = examples[patient]

        if patient != 5:
            gender, _ = get_patient_gender(patient)
            patientVoice = NPC_Voices[patient]["Voice"]
            content =f"""
                Eres {gender}.
                Tu nombre es {get_patient_name(patient)}.
                Tu edad es un número entre {set_patient_age(get_patient_age(patient))}, elige un
                número al azar entre esos dos, no lo menciones si no se te pregunta.
                Estás enfermo y necesitas atención médica.
                Actúa de forma informal, pero educada.
                Describe tus síntomas y responde a las preguntas del médico.
                Responde en dos frases.

                Aquí tienes una ristra de síntomas que puedes mencionar, no es
                necesario que los digas todos, elige dos y expande por tu cuenta:
                {patientSymptoms}

                Aquí tienes una ristra de frases de ejemplo, elige una y expande por
                tu cuenta:
                {patientPhraseExample}
            """
        else:
            print("Pediatria")
            patientVoice = NPC_Voices[patient]["Voice"]
            pediatrics = True
            content = f"""
                Eres una madre que lleva a su hijo al médico.
                Tu nombre es {get_patient_name(patient)}.
                Actúa de forma informal, pero educada.
                Describe los síntomas de tu hijo y responde a las preguntas del médico.
                Responde en dos frases.

                Aquí tienes una ristra de síntomas que puedes mencionar, no es
                necesario que los digas todos, elige dos y expande por tu cuenta:
                {patientSymptoms}

                Aquí tienes una ristra de frases de ejemplo, elige una y expande por
                tu cuenta:
                {patientPhraseExample}
            """

        messages.clear()
        messages.append({
            "role": "system",
            "content": content
        })
        currentIndex += 1

        return jsonify({"Patient": patient}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stt", methods=["POST"])
def speech_to_text():
    global pediatrics
    try:
        audio_bytes = request.data
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"

        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        print(transcription)

        messages.append({
            "role": "user",
            "content": transcription
        })

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        response = completion.choices[0].message.content
        messages.append({
            "role": "assistant",
            "content": response
        })

        print(patientVoice)
        audio = amazonPolly(response, patientVoice)
        response_json = jsonify({"response_text": response, "audio": audio})
        response_json.headers["Content-Length"] = str(len(response_json.get_data()))
        return response_json, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/check-answers", methods=["POST"])
def check_answers():
    try:
        data = request.get_json()
        answers = data['patology_answers']
        ageAnswers = data['age_answers']
        genderAnswers = data['gender_answers']
        print("Answers: ", answers)
        print("Age Answers: ", ageAnswers)
        print("Gender Answers: ", genderAnswers)

        if len(answers) != len(patientList) or len(ageAnswers) != len(patientList) or len(genderAnswers) != len(patientList):
            return jsonify({"error": "Invalid number of answers"}), 400
        
        results = {"patology_answers": [0] * len(patientList), "age_answers": [0] * len(patientList), "gender_answers": [0] * len(patientList)}
        for i in range(len(patientList)):
            if answers[i] == get_patient_patology(patientList[i]):
                results["patology_answers"][i] = 1
            if ageAnswers[i] == get_patient_age(patientList[i]):
                results["age_answers"][i] = 1
            if genderAnswers[i] == get_patient_gender(patientList[i])[1]:
                results["gender_answers"][i] = 1

        return jsonify({"correct_answers": results["patology_answers"], "correct_ages": results["age_answers"], "correct_genders": results["gender_answers"]}), 200
    except Exception as e:
        print("Error checking answers:", str(e))
        return jsonify({"error":str(e)}), 500

@app.route("/reboot", methods=["GET"])
def reboot():
    global currentIndex, patientList, patientVoice, pediatrics

    try:
        currentIndex = 0
        patientVoice = "Sergio"
        pediatrics = False
        patientList = random.sample(list(symptoms.keys()), len(symptoms))
        return jsonify({"message": "NPCs rebooted"}), 200
    except Exception as e:
        return jsonify({"message": "Could not restart the patient NPCs"}), 500

def amazonPolly(text, voice):
    try:
        resutlt = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            Engine="neural",
            VoiceId=voice
        )

        audio_bytes = resutlt["AudioStream"].read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        return audio_base64
    except Exception as e:
        print("Error synthesizing speech:", str(e))

def get_patient_patology(patient):
    if patient == 0:
        return "Hipertensión"
    elif patient == 1:
        return "Migraña"
    elif patient == 2:
        return "Apendicitis"
    elif patient == 3:
        return "VIH/SIDA"
    elif patient == 4:
        return "COVID-19"
    elif patient == 5:
        return "Bronquiolitis"

def get_patient_name(patient):
    return NPC_Voices[patient]["Voice"]

def get_patient_age(patient):
    """
        return 0: 20-30
        return 1: 30-40
        return 2: 40-50
        return 3: < 20
    """
    if patient == 0:
        return 0
    elif patient == 1:
        return 0
    elif patient == 2:
        return 1
    elif patient == 3:
        return 1
    elif patient == 4:
        return 0
    elif patient == 5:
        return 3

def set_patient_age(age_group):
    if age_group == 0 or age_group == 1 or age_group == 4:
        return "20-30 años"
    elif age_group == 2 or age_group == 3:
        return "30-40 años"
    else:
        return "40-50 años"

def get_patient_gender(patient):
    if patient == 0 or patient == 1 or patient == 3 or patient == 5:
        return "hombre", 0
    else:
        return "mujer", 1

if __name__ == "__main__":
    app.run(debug=True, host=SERVER_IP, port=8080)
