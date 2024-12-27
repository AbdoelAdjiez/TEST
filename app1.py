from flask import Flask, render_template, request, redirect, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Konfigurasi Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_NAME = "TEST"

# Autentikasi Google Sheets
if not os.path.exists(CREDENTIALS_FILE):
    raise FileNotFoundError(f"File '{CREDENTIALS_FILE}' tidak ditemukan. Pastikan file tersebut ada di direktori yang benar.")

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
client = gspread.authorize(credentials)
sheet = client.open(SPREADSHEET_NAME).sheet1


@app.route("/")
def index():
    return redirect("/pencarian")


@app.route("/pencarian", methods=["GET", "POST"])
def pencarian():
    search_results = None
    if request.method == "POST":
        search_query = request.form["search"].strip().lower()
        try:
            all_rows = sheet.get_all_records()
            search_results = [row for row in all_rows if search_query in str(row.get('AWB', '')).lower()]
            if not search_results:
                flash("Data tidak ditemukan.", "warning")
        except Exception as e:
            flash(f"Terjadi kesalahan saat mengambil data: {str(e)}", "danger")

    return render_template("test.html", page="pencarian", search_results=search_results)


@app.route("/input", methods=["GET", "POST"])
def input_data():
    if request.method == "POST":
        # Ambil data dari form
        tanggal = request.form.get("tanggal", "").strip()
        awb = request.form.get("awb", "").strip()
        ryder = request.form.get("ryder", "").strip()
        renmark = request.form.get("renmark", "").strip()
        reason = request.form.get("reason", "").strip()
        hasil_trace = request.form.get("hasil_trace", "").strip()
        ss = request.form.get("ss", "").strip()

        # Validasi data kosong
        if not (tanggal and awb and ryder and renmark and reason and hasil_trace and ss):
            flash("Semua kolom harus diisi!", "warning")
            return redirect("/input")

        try:
            # Tulis data ke Google Sheets
            sheet.append_row([tanggal, awb, ryder, renmark, reason, hasil_trace, ss])
            flash("Data berhasil disimpan!", "success")
        except Exception as e:
            flash(f"Terjadi kesalahan: {str(e)}", "danger")

    return render_template("test.html", page="input")

@app.route("/database")
def database():
    try:
        all_rows = sheet.get_all_records()
        print(f"All rows in database: {all_rows}")
    except Exception as e:
        flash(f"Terjadi kesalahan saat mengambil data: {str(e)}", "danger")
        all_rows = []

    return render_template("test.html", page="database", database=all_rows)


if __name__ == "__main__":
    app.run(debug=True)
