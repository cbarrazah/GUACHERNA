from flask import Flask, request, render_template_string
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__)

# URL raw del archivo Excel en GitHub (reemplaza con la tuya)
EXCEL_URL = 'https://raw.githubusercontent.com/cbarrazah/GUACHERNA/main/BATALLA44.xlsx'

def cargar_datos():
    try:
        # Descarga el archivo
        response = requests.get(EXCEL_URL)
        response.raise_for_status()  # Verifica errores
        # Lee el Excel en memoria usando Pandas
        df = pd.read_excel(BytesIO(response.content), engine='openpyxl')
        return df
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    error = None
    if request.method == 'POST':
        cedula = request.form.get('cedula').strip()
        if not cedula:
            error = 'La cédula es requerida.'
        else:
            df = cargar_datos()
            if df is not None:
                # Busca la fila (case-insensitive, asumiendo CEDULA es string o numérico)
                matching_row = df[df['CEDULA'].astype(str).str.strip().str.lower() == cedula.lower()]
                if not matching_row.empty:
                    resultado = matching_row.iloc[0].to_dict()  # Convierte a diccionario
                else:
                    error = 'No se encontró ninguna fila coincidente.'
            else:
                error = 'Error al cargar los datos.'

    # HTML simple para el formulario y resultados
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Portal de Consulta por Cédula</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            form { margin-bottom: 20px; }
            ul { list-style-type: none; padding: 0; }
            li { margin-bottom: 10px; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>Portal de Consulta por Cédula</h1>
        <form method="post">
            <label for="cedula">Ingrese Cédula:</label>
            <input type="text" id="cedula" name="cedula" required>
            <button type="submit">Buscar</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        {% if resultado %}
            <h2>Información encontrada:</h2>
            <ul>
                {% for key, value in resultado.items() %}
                    <li><strong>{{ key }}:</strong> {{ value }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    </body>
    </html>
    '''
    return render_template_string(html, resultado=resultado, error=error)

if __name__ == '__main__':
    app.run(debug=True)