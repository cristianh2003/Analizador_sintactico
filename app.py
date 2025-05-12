from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from analizador import analizar_codigo, AnalizadorSimplificadoCPP  # Asegurarse de importar la clase

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'clave_secreta_segura'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        if file and file.filename.endswith(".cpp"):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
                tokens = analizar_codigo(code)

                # Ejecutar análisis sintáctico
                analizador = AnalizadorSimplificadoCPP(tokens)
                try:
                    analizador.analizar_programa()
                    sintactico_resultado = "¡Análisis sintáctico completado con éxito!"
                except SyntaxError as e:
                    sintactico_resultado = f"Error de sintaxis en la línea {analizador.token_actual[2] if analizador.token_actual else 'desconocida'}: {e}"

            os.remove(filepath)

            # Guardar tokens y resultado sintáctico en sesión
            session['tokens'] = tokens
            session['sintactico_resultado'] = sintactico_resultado
            return redirect(url_for('index'))

    tokens = session.pop('tokens', None)
    sintactico_resultado = session.pop('sintactico_resultado', None)
    return render_template("index.html", tokens=tokens, sintactico_resultado=sintactico_resultado)

if __name__ == "__main__":
    app.run(debug=True)
