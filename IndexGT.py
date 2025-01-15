import sqlite3
from flask import Flask
from fast_html import render, table, tr, th, td, details, summary, div

app = Flask(__name__)

def get_data():
    with sqlite3.connect('IndexGT.db') as conn:
        cursor = conn.cursor()
        query = """
        SELECT COUNTRY, NAME, TOUR_DE_FRANCE AS TOUR, GIRO, VUELTA
        FROM CYCLISTS 
        WHERE END_YEAR > strftime('%Y', 'now')
        ORDER BY COUNTRY, NAME;
        """
        cursor.execute(query)
        results = cursor.fetchall()
    return results

@app.route('/')
def home():
    results = get_data()

    # Initialiser les données par pays
    country_data = {}
    for country, name, tour, giro, vuelta in results:
        if country not in country_data:
            country_data[country] = {
                "count": 0,
                "cyclists": []
            }
        country_data[country]["count"] += 1
        victories = []
        if tour:
            victories.append('Tour')
        if giro:
            victories.append('Giro')
        if vuelta:
            victories.append('Vuelta')
        name_with_tags = f"{name} ({', '.join(victories)})"
        country_data[country]["cyclists"].append(name_with_tags)

    # Créer une liste de lignes avec les données par pays
    rows = []
    for country, data in country_data.items():
        count = data["count"]
        cyclists_list = data["cyclists"]
        dropdown_content = "<br>".join(cyclists_list)
        dropdown = details(render(summary("")) + dropdown_content)
        row_data = [str(country), str(count), dropdown]
        rows.append(row_data)

    # Trier les lignes en fonction du nombre de gagnants (2e colonne)
    rows.sort(key=lambda x: int(x[1]), reverse=True)

    headers = ["Country", "IndexGT", "Riders"]
    
    # Construire les lignes HTML
    header_row = tr([th(header) for header in headers])
    data_rows = [tr([td(cell) for cell in row]) for row in rows]

    # Construire la table HTML
    table_html = render(table([header_row] + data_rows))

    # Lien vers le fichier CSS de PicoCSS
    pico_css_link = '<link rel="stylesheet" href="https://unpkg.com/@picocss/pico@1.*/css/pico.min.css">'

    # Structure HTML complète avec PicoCSS
    content = f"""
    {pico_css_link}
    <div class="container">
        <h1 class="text-center">IndexGT</h1>
        <p class="text-center">The IndexGT corresponds, for each country, to the number of active cyclists from that country who have won at least one stage of the Tour de France, the Giro d’Italia, or the Vuelta a España.</p>
        <div class="table-container">
            {table_html}
        </div>
    </div>
    """

    # Afficher le HTML avec PicoCSS inclus
    return content

if __name__ == '__main__':
    app.run(debug=True)
