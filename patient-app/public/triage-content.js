/**
 * Static triage content for the patient mini web app.
 *
 * In production these strings come from the LanguageAgent (translated on the
 * fly). For an offline/demo-safe build we ship pre-translated content for the
 * most common World-Cup languages. Falls back to English.
 */
window.TRIAGE_CONTENT = {
  en: {
    bcp47: "en-US",
    reassure: "Help is on the way. I'll ask a few quick questions.",
    micHint: "Tap to speak",
    speakAgain: "Hear question again",
    skip: "I can't speak — show pictures",
    painPrompt: "How strong is the pain? Tap a number.",
    bodyPrompt: "Where does it hurt? Tap the area.",
    done: "Thank you. The medical team has your answers. Help is here.",
    questions: [
      "Where does it hurt?",
      "How strong is the pain, from 0 to 10?",
      "Do you have any allergies?",
      "Are you taking any medicine right now?",
      "Do you have diabetes, heart, or other conditions?",
    ],
    body: { head: "Head", chest: "Chest", belly: "Belly", arm: "Arm", leg: "Leg", back: "Back" },
  },
  pt: {
    bcp47: "pt-BR",
    reassure: "A ajuda está a caminho. Vou fazer algumas perguntas rápidas.",
    micHint: "Toque para falar",
    speakAgain: "Ouvir a pergunta de novo",
    skip: "Não consigo falar — mostrar imagens",
    painPrompt: "Qual é a intensidade da dor? Toque num número.",
    bodyPrompt: "Onde dói? Toque na área.",
    done: "Obrigado. A equipe médica tem suas respostas. A ajuda chegou.",
    questions: [
      "Onde está doendo?",
      "Qual é a intensidade da dor, de 0 a 10?",
      "Você tem alguma alergia?",
      "Está tomando algum remédio agora?",
      "Você tem diabetes, problemas no coração ou outras condições?",
    ],
    body: { head: "Cabeça", chest: "Peito", belly: "Barriga", arm: "Braço", leg: "Perna", back: "Costas" },
  },
  es: {
    bcp47: "es-ES",
    reassure: "La ayuda está en camino. Te haré algunas preguntas rápidas.",
    micHint: "Toca para hablar",
    speakAgain: "Escuchar la pregunta otra vez",
    skip: "No puedo hablar — mostrar imágenes",
    painPrompt: "¿Qué tan fuerte es el dolor? Toca un número.",
    bodyPrompt: "¿Dónde te duele? Toca la zona.",
    done: "Gracias. El equipo médico tiene tus respuestas. La ayuda ha llegado.",
    questions: [
      "¿Dónde te duele?",
      "¿Qué tan fuerte es el dolor, del 0 al 10?",
      "¿Tienes alguna alergia?",
      "¿Estás tomando algún medicamento ahora?",
      "¿Tienes diabetes, problemas del corazón u otras condiciones?",
    ],
    body: { head: "Cabeza", chest: "Pecho", belly: "Vientre", arm: "Brazo", leg: "Pierna", back: "Espalda" },
  },
  ar: {
    bcp47: "ar-SA",
    rtl: true,
    reassure: "المساعدة في الطريق. سأطرح بعض الأسئلة السريعة.",
    micHint: "اضغط للتحدث",
    speakAgain: "استمع للسؤال مرة أخرى",
    skip: "لا أستطيع الكلام — أظهر الصور",
    painPrompt: "ما شدة الألم؟ اضغط على رقم.",
    bodyPrompt: "أين يؤلمك؟ اضغط على المكان.",
    done: "شكرًا. الفريق الطبي لديه إجاباتك. المساعدة وصلت.",
    questions: [
      "أين يؤلمك؟",
      "ما شدة الألم من 0 إلى 10؟",
      "هل لديك أي حساسية؟",
      "هل تتناول أي دواء الآن؟",
      "هل لديك سكري أو مشاكل في القلب أو حالات أخرى؟",
    ],
    body: { head: "الرأس", chest: "الصدر", belly: "البطن", arm: "الذراع", leg: "الساق", back: "الظهر" },
  },
  tr: {
    bcp47: "tr-TR",
    reassure: "Yardım geliyor. Birkaç hızlı soru soracağım.",
    micHint: "Konuşmak için dokun",
    speakAgain: "Soruyu tekrar dinle",
    skip: "Konuşamıyorum — resimleri göster",
    painPrompt: "Ağrı ne kadar şiddetli? Bir sayıya dokun.",
    bodyPrompt: "Neresi acıyor? Bölgeye dokun.",
    done: "Teşekkürler. Sağlık ekibi cevaplarını aldı. Yardım geldi.",
    questions: [
      "Neresi acıyor?",
      "Ağrı 0 ile 10 arasında ne kadar şiddetli?",
      "Herhangi bir alerjin var mı?",
      "Şu anda ilaç kullanıyor musun?",
      "Şeker, kalp veya başka bir rahatsızlığın var mı?",
    ],
    body: { head: "Baş", chest: "Göğüs", belly: "Karın", arm: "Kol", leg: "Bacak", back: "Sırt" },
  },
};

window.BODY_EMOJI = {
  head: "🧠",
  chest: "🫀",
  belly: "🩻",
  arm: "💪",
  leg: "🦵",
  back: "🔙",
};
