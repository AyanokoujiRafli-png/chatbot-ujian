from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Data soal
soal = [
    {
        "soal": "Apa ibu kota Indonesia?",
        "pilihan": ["Jakarta", "Bandung", "Surabaya", "Medan"],
        "jawaban": "Jakarta"
    },
    {
        "soal": "Siapakah presiden pertama Indonesia?",
        "pilihan": ["Soeharto", "Soekarno", "Habibie", "Gus Dur"],
        "jawaban": "Soekarno"
    },
    {
        "soal": "Berapa hasil 5 + 3 × 2?",
        "pilihan": ["16", "11", "10", "13"],
        "jawaban": "11"
    },
    {
        "soal": "Planet terdekat dengan Matahari adalah?",
        "pilihan": ["Venus", "Mars", "Merkurius", "Bumi"],
        "jawaban": "Merkurius"
    },
    {
        "soal": "Hewan yang bisa hidup di air dan darat disebut?",
        "pilihan": ["Reptil", "Amfibi", "Mamalia", "Ikan"],
        "jawaban": "Amfibi"
    }
]

# Status user sementara (di memori, untuk demo)
user_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_quiz():
    data = request.json
    nama = data.get('nama')
    if not nama:
        return jsonify({"error": "Nama harus diisi"}), 400
    
    # Buat session baru
    session_id = str(random.randint(1000, 9999))
    user_sessions[session_id] = {
        "nama": nama,
        "current_soal": 0,
        "score": 0,
        "soal_list": soal.copy()
    }
    
    soal_pertama = user_sessions[session_id]["soal_list"][0]
    return jsonify({
        "session_id": session_id,
        "soal": soal_pertama["soal"],
        "pilihan": soal_pertama["pilihan"],
        "nomor": 1,
        "total": len(soal)
    })

@app.route('/jawab', methods=['POST'])
def jawab_soal():
    data = request.json
    session_id = data.get('session_id')
    jawaban_user = data.get('jawaban')
    
    if session_id not in user_sessions:
        return jsonify({"error": "Session tidak ditemukan"}), 400
    
    session = user_sessions[session_id]
    current_index = session["current_soal"]
    soal_saat_ini = session["soal_list"][current_index]
    
    # Cek jawaban
    benar = (jawaban_user == soal_saat_ini["jawaban"])
    if benar:
        session["score"] += 1
    
    # Pindah ke soal berikutnya
    session["current_soal"] += 1
    is_selesai = (session["current_soal"] >= len(session["soal_list"]))
    
    if is_selesai:
        nilai = (session["score"] / len(session["soal_list"])) * 100
        return jsonify({
            "selesai": True,
            "benar": benar,
            "score": session["score"],
            "total": len(session["soal_list"]),
            "nilai": nilai,
            "pesan": f"🎉 Selamat {session['nama']}! Kamu mendapat nilai {nilai:.0f}"
        })
    else:
        soal_berikutnya = session["soal_list"][session["current_soal"]]
        return jsonify({
            "selesai": False,
            "benar": benar,
            "soal": soal_berikutnya["soal"],
            "pilihan": soal_berikutnya["pilihan"],
            "nomor": session["current_soal"] + 1,
            "total": len(session["soal_list"]),
            "score_sementara": session["score"]
        })

if __name__ == '__main__':
    app.run(debug=True)
