from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import mysql.connector

# Configura o driver para usar o container Selenium
def configurar_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    try:
        driver = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=options
        )
        return driver
    except WebDriverException as e:
        print("Erro ao conectar com o Selenium:", e)
        exit(1)

def esperar_anuncios(driver, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.sc-1fcmfeb-2'))  # Ajuste o seletor conforme o HTML atual da OLX
        )
        return True
    except TimeoutException:
        print("⏰ Timeout esperando anúncios carregarem.")
        return False

# Aceita cookies no site
def aceitar_cookies(driver):
    try:
        botao = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "adopt-accept-all-button"))
        )
        botao.click()
    except TimeoutException:
        pass

# Extrai dados da página HTML
def extrair_dados(html, estado):
    soup = BeautifulSoup(html, 'html.parser')
    anuncios = soup.find_all('section', class_='olx-adcard')
    dados = []
    for anuncio in anuncios:
        titulo = anuncio.find('h2', class_='olx-adcard__title')
        preco = anuncio.find('h3', class_='olx-adcard__price')
        km_tag = anuncio.find('div', class_='olx-adcard__detail')
        dados.append({
            'titulo': titulo.text.strip() if titulo else None,
            'km': km_tag.text.strip() if km_tag else None,
            'preco': preco.text.strip() if preco else None,
            'estado': estado
        })
    return dados

# Salva os dados no banco MySQL
def salvar_no_mysql(dados):
    try:
        conexao = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "db"),
            user=os.getenv("MYSQL_USER", "root"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            password=os.getenv("MYSQL_PASSWORD", "root"),
            database=os.getenv("MYSQL_DATABASE", "olx_data")
        )
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255),
                km VARCHAR(255),
                preco VARCHAR(255),
                estado VARCHAR(2)
            )
        """)
        for item in dados:
            cursor.execute("""
                INSERT INTO veiculos (titulo, km, preco, estado)
                VALUES (%s, %s, %s, %s)
            """, (item['titulo'], item['km'], item['preco'], item['estado']))
        conexao.commit()
        cursor.close()
        conexao.close()
    except mysql.connector.Error as err:
        print("Erro ao salvar no MySQL:", err)

# Loop principal por estado e paginação
def main():
    estados = [
        "ac", "al", "ap", "am", "ba", "ce", "df", "es", "go", "ma", "mt", "ms", "mg",
        "pa", "pb", "pr", "pe", "pi", "rj", "rn", "rs", "ro", "rr", "sc", "sp", "se", "to"
    ]

    driver = configurar_driver()

    for estado in estados:
        print(f"\n🚗 Coletando dados do estado: {estado.upper()}")
        base_url = f"https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-{estado}?lis=home_body_search_bar_2020"
        driver.get(base_url)

        esperar_anuncios(driver)
        aceitar_cookies(driver)
        time.sleep(2)

        todos_os_dados = []
        pagina = 1
        ultima_pagina_html = ""

        while True:
            print(f"📄 Coletando página {pagina}")
            dados = extrair_dados(driver.page_source, estado)
            if not dados:
                print("⚠️ Nenhum dado encontrado. Encerrando.")
                break

            todos_os_dados.extend(dados)

            proxima_url = f"{base_url}&o={pagina + 1}"
            driver.get(proxima_url)
            time.sleep(3)

            # Detecção de fim da paginação
            nova_pagina_html = driver.page_source
            if nova_pagina_html == ultima_pagina_html:
                print("🔚 Fim da paginação detectado.")
                break

            ultima_pagina_html = nova_pagina_html
            pagina += 1

        df = pd.DataFrame(todos_os_dados)
        print(df.head())
        print(f"🧾 Total de dados do estado {estado.upper()}: {len(df)}")

        salvar_no_mysql(todos_os_dados)
        print(f"💾 {len(todos_os_dados)} registros salvos no banco para {estado.upper()}")

    driver.quit()
