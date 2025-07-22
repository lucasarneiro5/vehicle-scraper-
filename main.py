# app/main.py
from scraper import scrape_webmotors

def main():
    print("Iniciando raspagem de dados da Webmotors...")
    dados = scrape_webmotors(paginas=3)  # Ajustável
    print(f"Raspagem finalizada com {len(dados)} veículos.")

    # Exemplo: salvar em CSV
    import pandas as pd
    df = pd.DataFrame(dados)
    df.to_csv("webmotors_veiculos.csv", index=False)
    print("Dados salvos em 'webmotors_veiculos.csv'")

if __name__ == "__main__":
    main()
