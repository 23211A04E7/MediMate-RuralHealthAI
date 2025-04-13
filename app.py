from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from gtts import gTTS
from uuid import uuid4
import os

app = Flask(__name__)
CORS(app)

remedies = {
    "cold": {
        "aliases": ["cold", "జలుబు"],
        "condition": {"en": "Common Cold", "te": "సాధారణ జలుబు"},
        "remedy": {
            "en": "Drink warm water, rest well, and inhale steam twice a day.If symptoms are severe, please visit the nearest hospital.",
            "te": "గోరువెచ్చని నీరు త్రాగండి, విశ్రాంతి తీసుకోండి, రోజుకు రెండు సార్లు ఆవిరి పీల్చండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "fever": {
        "aliases": ["fever", "జ్వరం", "జ్వరము"],
        "condition": {"en": "Fever", "te": "జ్వరం"},
        "remedy": {
            "en": "Stay hydrated, take paracetamol, and rest properly.If symptoms are severe, please visit the nearest hospital.",
            "te": "బాగా నీరు త్రాగండి, ప్యారాసిటమాల్ తీసుకోండి, విశ్రాంతి తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "headache": {
        "aliases": ["headache", "తలనొప్పి"],
        "condition": {"en": "Headache", "te": "తలనొప్పి"},
        "remedy": {
            "en": "Apply a cold compress and rest in a quiet dark room.If symptoms are severe, please visit the nearest hospital.",
            "te": "చల్లటి కంఫ్రెస్ వేసుకోండి, నిశ్శబ్ద గదిలో విశ్రాంతి తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "cough": {
        "aliases": ["cough", "దగ్గు"],
        "condition": {"en": "Cough", "te": "దగ్గు"},
        "remedy": {
            "en": "Drink warm honey-lemon water and avoid cold foods.If symptoms are severe, please visit the nearest hospital.",
            "te": "గోరువెచ్చని తేనె-నిమ్మరసం నీరు త్రాగండి మరియు చల్లని ఆహారాన్ని నివారించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "sore throat": {
        "aliases": ["sore throat", "గొంతు నొప్పి"],
        "condition": {"en": "Sore Throat", "te": "గొంతు నొప్పి"},
        "remedy": {
            "en": "Gargle with salt water and drink warm fluids.If symptoms are severe, please visit the nearest hospital.",
            "te": "ఉప్పు నీటితో గొంతు కడుగుకోవడం మరియు గోరువెచ్చని ద్రవాలను త్రాగడం మంచిది.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "stomach ache": {
        "aliases": ["stomach ache", "పేగు నొప్పి", "కడుపు నొప్పి"],
        "condition": {"en": "Stomach Ache", "te": "కడుపు నొప్పి"},
        "remedy": {
            "en": "Avoid spicy food, drink warm water and rest.If symptoms are severe, please visit the nearest hospital.",
            "te": "కారం తక్కువ ఆహారం తీసుకోండి, గోరువెచ్చని నీరు త్రాగండి మరియు విశ్రాంతి తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "diarrhea": {
        "aliases": ["diarrhea", "వికారం"],
        "condition": {"en": "Diarrhea", "te": "వికారం"},
        "remedy": {
            "en": "Stay hydrated with ORS and eat light food.If symptoms are severe, please visit the nearest hospital.",
            "te": "ORS త్రాగండి మరియు తేలికపాటి ఆహారం తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "vomiting": {
        "aliases": ["vomiting", "వాంతులు"],
        "condition": {"en": "Vomiting", "te": "వాంతులు"},
        "remedy": {
            "en": "Sip water slowly and avoid solid foods for a while.If symptoms are severe, please visit the nearest hospital.",
            "te": "నెమ్మదిగా నీరు త్రాగండి మరియు కొంతకాలం ఘన ఆహారాన్ని నివారించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "body pain": {
        "aliases": ["body pain", "శరీర నొప్పులు"],
        "condition": {"en": "Body Pain", "te": "శరీర నొప్పులు"},
        "remedy": {
            "en": "Take a warm bath, use a pain reliever if necessary.If symptoms are severe, please visit the nearest hospital.",
            "te": "గోరువెచ్చని నీటితో స్నానం చేయండి, అవసరమైతే నొప్పి నివారణ మందులు తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "acidity": {
        "aliases": ["acidity", "ఆమ్లత"],
        "condition": {"en": "Acidity", "te": "ఆమ్లత"},
        "remedy": {
            "en": "Avoid spicy food, eat small meals, and drink cold milk.If symptoms are severe, please visit the nearest hospital.",
            "te": "కారం తక్కువ ఆహారం తీసుకోండి, చిన్న భోజనాలు చేయండి, చల్లని పాల త్రాగండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
        "constipation": {
        "aliases": ["constipation", "మలబద్ధకం"],
        "condition": {"en": "Constipation", "te": "మలబద్ధకం"},
        "remedy": {
            "en": "Eat fiber-rich foods like fruits and drink plenty of water.If symptoms are severe, please visit the nearest hospital.",
            "te": "ఫైబర్ ఎక్కువగా ఉండే పండ్లు తినండి, తగినంత నీరు త్రాగండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "indigestion": {
        "aliases": ["indigestion", "అజీర్ణం"],
        "condition": {"en": "Indigestion", "te": "అజీర్ణం"},
        "remedy": {
            "en": "Avoid oily foods and eat light meals. Ginger tea helps.If symptoms are severe, please visit the nearest hospital.",
            "te": "నూనె ఫుడ్ తక్కువగా తీసుకోండి, తేలికపాటి ఆహారం తినండి. అల్లం టీ ఉపశమనంగా పనిచేస్తుంది.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "gas": {
        "aliases": ["gas", "వాయువు"],
        "condition": {"en": "Gas Trouble", "te": "వాయువు"},
        "remedy": {
            "en": "Avoid carbonated drinks and spicy food. Take a walk after meals.If symptoms are severe, please visit the nearest hospital.",
            "te": "కార్బొనేట్ పానీయాలు, మసాలా ఆహారం నివారించండి. భోజనం తరువాత నడవండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "toothache": {
        "aliases": ["toothache", "పళ్ల నొప్పి"],
        "condition": {"en": "Toothache", "te": "పళ్ల నొప్పి"},
        "remedy": {
            "en": "Apply clove oil on the affected tooth and consult a dentist.If symptoms are severe, please visit the nearest hospital.",
            "te": "పలుకు లవంగం నూనె పెట్టండి మరియు దంతవైద్యుడిని సంప్రదించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "eye pain": {
        "aliases": ["eye pain", "కన్ను నొప్పి"],
        "condition": {"en": "Eye Pain", "te": "కన్ను నొప్పి"},
        "remedy": {
            "en": "Splash eyes with cold water and rest them. Avoid screens.If symptoms are severe, please visit the nearest hospital.",
            "te": "చల్లటి నీటితో కళ్ళు కడగండి మరియు విశ్రాంతి ఇవ్వండి. మొబైల్ లేదా ల్యాప్‌టాప్ చూడడం తగ్గించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "ear pain": {
        "aliases": ["ear pain", "చెవి నొప్పి"],
        "condition": {"en": "Ear Pain", "te": "చెవి నొప్పి"},
        "remedy": {
            "en": "Warm olive oil drops may help. Seek medical advice if severe.",
            "te": "గోరువెచ్చని ఆలివ్ ఆయిల్ చుక్కలు వేయండి. ఎక్కువ అయితే డాక్టర్ ని సంప్రదించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "back pain": {
        "aliases": ["back pain", "వెనుక నొప్పి"],
        "condition": {"en": "Back Pain", "te": "వెనుక నొప్పి"},
        "remedy": {
            "en": "Apply a warm compress and do gentle stretching exercises.If symptoms are severe, please visit the nearest hospital.",
            "te": "గోరువెచ్చని కంఫ్రెస్ వాడండి, మెల్లగా స్ట్రెచింగ్ చేయండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "neck pain": {
        "aliases": ["neck pain", "గొంతు నొప్పి"],
        "condition": {"en": "Neck Pain", "te": "గొంతు నొప్పి"},
        "remedy": {
            "en": "Use a warm cloth and practice light neck exercises.If symptoms are severe, please visit the nearest hospital.",
            "te": "వెచ్చని గుడ్డ వాడండి మరియు మెత్తగా నెక్ వ్యాయామాలు చేయండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "dizziness": {
        "aliases": ["dizziness", "తలకిక్కిపోవడం"],
        "condition": {"en": "Dizziness", "te": "తలకిక్కిపోవడం"},
        "remedy": {
            "en": "Sit or lie down immediately, drink some water, and rest.If symptoms are severe, please visit the nearest hospital.",
            "te": "వెంటనే కూర్చోవడం లేదా పడుకోవడం, నీరు త్రాగడం మరియు విశ్రాంతి అవసరం.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "burn": {
        "aliases": ["burn", "గాయం", "కాలి పోవడం"],
        "condition": {"en": "Burn", "te": "గాయం"},
        "remedy": {
            "en": "Apply cold water to the area, avoid applying ice directly.If symptoms are severe, please visit the nearest hospital.",
            "te": "గాయానికి చల్లటి నీరు వేసుకోండి, ఐస్ నేరుగా పెట్టొద్దు.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
        "vomiting": {
        "aliases": ["vomiting", "ఉలికిపాటు", "ఒక్కింతలు"],
        "condition": {"en": "Vomiting", "te": "ఒక్కింతలు"},
        "remedy": {
            "en": "Drink ORS or lemon water and rest. Avoid solid food temporarily.If symptoms are severe, please visit the nearest hospital.",
            "te": "ORS లేదా నిమ్మ నీరు త్రాగండి. కొంతకాలం ఘన ఆహారం తినడం నివారించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "diarrhea": {
        "aliases": ["diarrhea", "వికారం", "దస్తులు"],
        "condition": {"en": "Diarrhea", "te": "దస్తులు"},
        "remedy": {
            "en": "Stay hydrated with ORS and avoid spicy foods.If symptoms are severe, please visit the nearest hospital.",
            "te": "ORS త్రాగుతూ ఉండండి, కారమైన ఆహారం తినకండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "acidity": {
        "aliases": ["acidity", "మాడిసికట్టు", "ఆమ్లత"],
        "condition": {"en": "Acidity", "te": "ఆమ్లత"},
        "remedy": {
            "en": "Drink cold milk or buttermilk and avoid oily foods.If symptoms are severe, please visit the nearest hospital.",
            "te": "చల్లటి పాలు లేదా మజ్జిగ త్రాగండి, నూనె గల ఆహారం నివారించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "sore throat": {
        "aliases": ["sore throat", "గొంతు నొప్పి", "గొంతు మంట"],
        "condition": {"en": "Sore Throat", "te": "గొంతు నొప్పి"},
        "remedy": {
            "en": "Gargle with warm salt water and drink warm fluids.If symptoms are severe, please visit the nearest hospital.",
            "te": "ఉప్పు వేసిన గోరువెచ్చని నీటితో గార్గిల్ చేయండి, వెచ్చని పదార్థాలు త్రాగండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "cough": {
        "aliases": ["cough", "దగ్గు"],
        "condition": {"en": "Cough", "te": "దగ్గు"},
        "remedy": {
            "en": "Drink warm honey water and avoid cold items.If symptoms are severe, please visit the nearest hospital.",
            "te": "తేనె కలిపిన గోరువెచ్చని నీరు త్రాగండి, చల్లటి పదార్థాలు తీసుకోకండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "muscle pain": {
        "aliases": ["muscle pain", "కండరాల నొప్పి"],
        "condition": {"en": "Muscle Pain", "te": "కండరాల నొప్పి"},
        "remedy": {
            "en": "Use warm compress and do gentle stretching.If symptoms are severe, please visit the nearest hospital.",
            "te": "వెచ్చని కంఫ్రెస్ వాడండి, మెల్లగా స్ట్రెచింగ్ చేయండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "joint pain": {
        "aliases": ["joint pain", "సంధి నొప్పి"],
        "condition": {"en": "Joint Pain", "te": "సంధి నొప్పి"},
        "remedy": {
            "en": "Use turmeric in warm milk, take rest, and consult doctor if needed.",
            "te": "వెచ్చని పాలలో పసుపు కలిపి త్రాగండి, విశ్రాంతి తీసుకోండి, అవసరమైతే వైద్యుడిని సంప్రదించండి."
        }
    },
    "menstrual cramps": {
        "aliases": ["menstrual cramps", "ఋతుస్రావ నొప్పులు", "పీరియడ్స్ నొప్పి"],
        "condition": {"en": "Menstrual Cramps", "te": "ఋతుస్రావ నొప్పులు"},
        "remedy": {
            "en": "Apply heating pad and drink warm herbal tea.If symptoms are severe, please visit the nearest hospital.",
            "te": "వెచ్చని బ్యాగ్ వాడండి మరియు హెర్బల్ టీ త్రాగండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "allergy": {
        "aliases": ["allergy", "అలెర్జీ"],
        "condition": {"en": "Allergy", "te": "అలెర్జీ"},
        "remedy": {
            "en": "Avoid allergens and take antihistamines if required.If symptoms are severe, please visit the nearest hospital.",
            "te": "అలెర్జీ కలిగించే పదార్థాలను నివారించండి, అవసరమైతే యాంటీహిస్టామిన్ తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "nose bleed": {
        "aliases": ["nose bleed", "ముక్కు రక్తస్రావం"],
        "condition": {"en": "Nose Bleed", "te": "ముక్కు రక్తస్రావం"},
        "remedy": {
            "en": "Sit upright, pinch nose, and apply cold compress.If symptoms are severe, please visit the nearest hospital.",
            "te": "నిలువుగా కూర్చోండి, ముక్కు ఒత్తండి, చల్లటి కంఫ్రెస్ వాడండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
        "back pain": {
        "aliases": ["back pain", "తిన్నెనొప్పి", "వెనుక నొప్పి"],
        "condition": {"en": "Back Pain", "te": "తిన్నెనొప్పి"},
        "remedy": {
            "en": "Apply warm compress, avoid heavy lifting, and do gentle stretching.If symptoms are severe, please visit the nearest hospital.",
            "te": "వెచ్చని కంఫ్రెస్ వాడండి, బరువు సామాను ఎత్తడం నివారించండి, మెల్లగా వ్యాయామం చేయండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "constipation": {
        "aliases": ["constipation", "కబ్జా", "మలబద్ధకం"],
        "condition": {"en": "Constipation", "te": "మలబద్ధకం"},
        "remedy": {
            "en": "Eat fiber-rich food, drink more water, and stay physically active.If symptoms are severe, please visit the nearest hospital.",
            "te": "ఫైబర్ ఎక్కువగా ఉన్న ఆహారం తినండి, నీరు ఎక్కువగా త్రాగండి, శారీరకంగా చురుకుగా ఉండండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "eye irritation": {
        "aliases": ["eye irritation", "కళ్ల రాపడం", "కళ్ల మంట"],
        "condition": {"en": "Eye Irritation", "te": "కళ్ల మంట"},
        "remedy": {
            "en": "Wash eyes with clean water and avoid rubbing.If symptoms are severe, please visit the nearest hospital.",
            "te": "కళ్లను శుభ్రమైన నీటితో కడగండి, రాయడం నివారించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "toothache": {
        "aliases": ["toothache", "పన్ను నొప్పి"],
        "condition": {"en": "Toothache", "te": "పన్ను నొప్పి"},
        "remedy": {
            "en": "Rinse with salt water and apply clove oil on the tooth.If symptoms are severe, please visit the nearest hospital.",
            "te": "ఉప్పు నీటితో తడిమి, లవంగ నూనెను పన్నుపైన వాడండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "burns": {
        "aliases": ["burn", "కాలిన గాయం", "కాలిన చోటు"],
        "condition": {"en": "Minor Burns", "te": "కాలిన గాయం"},
        "remedy": {
            "en": "Hold under cool water for 10 minutes and apply aloe vera.If symptoms are severe, please visit the nearest hospital.",
            "te": "10 నిమిషాలు చల్లటి నీటిలో ఉంచండి, ఆపై అలోవెరా రాయండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "nausea": {
        "aliases": ["nausea", "వాంతి అనిపించడం"],
        "condition": {"en": "Nausea", "te": "వాంతి అనిపించడం"},
        "remedy": {
            "en": "Sip ginger tea or lemon water and lie down in a ventilated area.If symptoms are severe, please visit the nearest hospital.",
            "te": "అల్లం టీ లేదా నిమ్మ నీరు త్రాగండి, గాలి వెలుపల ఉన్న చోట విశ్రాంతి తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "insomnia": {
        "aliases": ["insomnia", "నిద్రలేమి"],
        "condition": {"en": "Insomnia", "te": "నిద్రలేమి"},
        "remedy": {
            "en": "Avoid screens before sleep, drink warm milk, and follow a sleep routine.If symptoms are severe, please visit the nearest hospital.",
            "te": "నిద్రకి ముందు ఫోన్/టీవీ చూడకండి, వెచ్చని పాలు త్రాగండి, నిద్రపోయే సమయాన్ని పాటించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "ear pain": {
        "aliases": ["ear pain", "చెవి నొప్పి"],
        "condition": {"en": "Ear Pain", "te": "చెవి నొప్పి"},
        "remedy": {
            "en": "Use warm compress and avoid inserting objects into the ear.If symptoms are severe, please visit the nearest hospital.",
            "te": "వెచ్చని కంఫ్రెస్ వాడండి, చెవిలో వస్తువులు పెట్టకండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "dry cough": {
        "aliases": ["dry cough", "ఎండు దగ్గు"],
        "condition": {"en": "Dry Cough", "te": "ఎండు దగ్గు"},
        "remedy": {
            "en": "Use honey with warm water and avoid cold drinks.If symptoms are severe, please visit the nearest hospital.",
            "te": "తేనెను గోరువెచ్చని నీటిలో కలిపి త్రాగండి, చల్లటి పానీయాలు నివారించండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "heat stroke": {
        "aliases": ["heat stroke", "ఉష్ణాఘాతం", "వడదెబ్బ"],
        "condition": {"en": "Heat Stroke", "te": "వడదెబ్బ"},
        "remedy": {
            "en": "Move to a cool place, drink plenty of fluids, and rest.If symptoms are severe, please visit the nearest hospital.",
            "te": "చల్లటి ప్రదేశానికి వెళ్లండి, ఎక్కువగా ద్రవాలు త్రాగండి, విశ్రాంతి తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
        "gastritis": {
        "aliases": ["gastritis", "అజీర్ణం", "గ్యాస్"],
        "condition": {"en": "Gastritis", "te": "అజీర్ణం"},
        "remedy": {
            "en": "Eat light meals, avoid spicy food, and drink cold milk.If symptoms are severe, please visit the nearest hospital.",
            "te": "తేలికపాటి ఆహారం తీసుకోండి, మసాలా తినకండి, చల్లటి పాలు త్రాగండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "skin rash": {
        "aliases": ["rash", "చర్మ దద్దుర్లు", "చర్మం రాపడం"],
        "condition": {"en": "Skin Rash", "te": "చర్మ దద్దుర్లు"},
        "remedy": {
            "en": "Apply calamine lotion and avoid scratching.If symptoms are severe, please visit the nearest hospital.",
            "te": "కాలమైన్ లోషన్ వాడండి, పొక్కను తుడవకండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "indigestion": {
        "aliases": ["indigestion", "జీర్ణక్రమ సమస్య"],
        "condition": {"en": "Indigestion", "te": "జీర్ణక్రమ సమస్య"},
        "remedy": {
            "en": "Drink warm water with lemon and avoid overeating.If symptoms are severe, please visit the nearest hospital.",
            "te": "నిమ్మకాయ కలిపిన గోరువెచ్చని నీరు త్రాగండి, అతిగా తినకండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "menstrual cramps": {
        "aliases": ["menstrual cramps", "పీరియడ్ నొప్పులు", "కాలుష్య నొప్పులు"],
        "condition": {"en": "Menstrual Cramps", "te": "పీరియడ్ నొప్పులు"},
        "remedy": {
            "en": "Use heating pad and drink warm herbal teas.If symptoms are severe, please visit the nearest hospital.",
            "te": "వెచ్చటి వాటర్ బ్యాగ్ వాడండి, గోరువెచ్చటి టీ త్రాగండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "vomiting": {
        "aliases": ["vomiting", "వాంతులు"],
        "condition": {"en": "Vomiting", "te": "వాంతులు"},
        "remedy": {
            "en": "Drink ORS or ginger tea and rest.If symptoms are severe, please visit the nearest hospital.",
            "te": "ORS లేదా అల్లం టీ త్రాగండి, విశ్రాంతి తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "urinary infection": {
        "aliases": ["urinary infection", "మూత్రపింజల సంక్రమణ"],
        "condition": {"en": "Urinary Tract Infection", "te": "మూత్రపింజల సంక్రమణ"},
        "remedy": {
            "en": "Drink plenty of water and consult a doctor for antibiotics.",
            "te": "ఎక్కువ నీరు త్రాగండి, యాంటిబయోటిక్ కోసం వైద్యుడిని సంప్రదించండి."
        }
    },
    "acidity": {
        "aliases": ["acidity", "ఆమ్లత", "జలుబు"],
        "condition": {"en": "Acidity", "te": "ఆమ్లత"},
        "remedy": {
            "en": "Avoid spicy food, eat on time, and take antacids.If symptoms are severe, please visit the nearest hospital.",
            "te": "మసాలా ఆహారం నివారించండి, సమయానికి తినండి, యాంటాసిడ్స్ తీసుకోండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "leg cramps": {
        "aliases": ["leg cramps", "కాళ్ళ నొప్పి", "కాళ్ళ పట్టికలు"],
        "condition": {"en": "Leg Cramps", "te": "కాళ్ళ పట్టికలు"},
        "remedy": {
            "en": "Stretch your legs and drink plenty of fluids.If symptoms are severe, please visit the nearest hospital.",
            "te": "కాళ్ళను స్ట్రెచ్ చేయండి, ఎక్కువగా నీరు త్రాగండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "dizziness": {
        "aliases": ["dizziness", "తల తిరగడం", "తల చక్కర్లు"],
        "condition": {"en": "Dizziness", "te": "తల తిరగడం"},
        "remedy": {
            "en": "Sit or lie down immediately and drink water slowly.If symptoms are severe, please visit the nearest hospital.",
            "te": "అందుబాటులో ఉన్న చోట కూర్చోండి లేదా పడుకోండి, నీటిని నెమ్మదిగా త్రాగండి.లక్షణాలు తీవ్రమై ఉంటే, దయచేసి సమీపంలోని ఆసుపత్రికి వెళ్లండి."
        }
    },
    "ear wax": {
        "aliases": ["ear wax", "చెవి మైలికలు", "చెవి మేలు"],
        "condition": {"en": "Ear Wax Blockage", "te": "చెవి మేలు"},
        "remedy": {
            "en": "Use ear drops or consult a doctor for cleaning.",
            "te": "చెవి డ్రాప్స్ వాడండి లేదా వైద్యుడిని సంప్రదించండి."
        }
    }
}
nearby_clinics = [
    {
        "name": "Government Area Hospital",
        "address": "Main Road, Narsapur, Medak",
        "contact": "08457-222XXX"
    },
    {
        "name": "Sri Sai Clinic",
        "address": "Opp. Bus Stand, Narsapur, Medak",
        "contact": "9849XXXXXX"
    },
    {
        "name": "Laxmi Nursing Home",
        "address": "Shivaji Nagar, Narsapur",
        "contact": "9989XXXXXX"
    }
]


def detect_language(text):
    for char in text:
        if '\u0C00' <= char <= '\u0C7F':
            return 'te'
    return 'en'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_symptom():
    data = request.get_json()
    user_input = data.get("symptom", "").lower()
    lang = detect_language(user_input)

    for value in remedies.values():
        if any(alias in user_input for alias in value["aliases"]):
            return jsonify({
                "condition": value["condition"][lang],
                "remedy": value["remedy"][lang],
                "clinics": nearby_clinics
            })

    fallback_condition = {
        "en": "Unknown",
        "te": "తెలియని లక్షణం"
    }

    fallback_remedy = {
        "en": "Please consult a doctor in Narsapur for further evaluation.",
        "te": "దయచేసి నర్సాపూర్ లోని వైద్యుడిని సంప్రదించండి."
    }

    return jsonify({
        "condition": fallback_condition[lang],
        "remedy": fallback_remedy[lang],
        "clinics": nearby_clinics
    })

@app.route('/speak', methods=['POST'])
def speak_text():
    data = request.get_json()
    text = data.get("text", "")
    lang = detect_language(text)

    filename = f"static/audio_{uuid4().hex}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    return jsonify({"audio_url": f"/{filename}"})

if __name__ == '__main__':
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)                                
