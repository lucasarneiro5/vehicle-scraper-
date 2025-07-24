import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def extrair_dados(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    anuncios = soup.find_all('section', class_='olx-adcard')
    dados = []

    for anuncio in anuncios:
        # Título
        titulo_tag = anuncio.find('h2', class_='olx-adcard__title')
        titulo = titulo_tag.text.strip() if titulo_tag else None

        # Link
        link_tag = anuncio.find('a', class_='olx-adcard__link')
        link = link_tag['href'] if link_tag else None

        # Quilometragem
        km_tag = anuncio.find('div', class_='olx-adcard__detail')
        km = km_tag.text.strip() if km_tag else None

        # Preço
        preco_tag = anuncio.find('h3', class_='olx-adcard__price')
        preco = preco_tag.text.strip() if preco_tag else None

        dados.append({
            'titulo': titulo,
            'km': km,
            'preco': preco,
            'link': link
        })

    return dados


def aceitar_cookies(driver):
    try:
        botao = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "adopt-accept-all-button"))
        )
        botao.click()
    except TimeoutException:
        pass


def navegar_e_coletar():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    url_base = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-ac?o={}"
    pagina = 1
    todos_dados = []

    try:
        while True:
            driver.get(url_base.format(pagina))

            if pagina == 1:
                aceitar_cookies(driver)

            time.sleep(3)

            dados = extrair_dados(driver)
            if not dados:
                break

            todos_dados.extend(dados)

            # Verifica se botão da página seguinte está desabilitado
            try:
                proximo_btn = driver.find_element(By.XPATH, '//a[contains(text(),"Próxima página")]/..')
                if 'olx-core-button--disabled' in proximo_btn.get_attribute('class'):
                    break
            except NoSuchElementException:
                break

            pagina += 1

    finally:
        driver.quit()

    df = pd.DataFrame(todos_dados)
    df.to_csv('carros_olx.csv', index=False)
    print(f"{len(df)} registros salvos em carros_olx.csv")


if __name__ == '__main__':
    navegar_e_coletar()
