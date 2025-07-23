# Web Crawler de Anúncios da OLX (Carros por Estado)

Este projeto utiliza **Selenium** e **BeautifulSoup** para acessar a OLX, simular a navegação até a categoria de veículos e coletar informações de anúncios por **todos os estados do Brasil**.

## 🚗 Funcionalidades

- Acessa a página principal da OLX
- Clica automaticamente em "Autos" e depois em "Buscar"
- Percorre os anúncios da categoria "Carros, vans e utilitários" de todos os estados
- Coleta as seguintes informações:
  - Estado
  - Título do anúncio
  - Preço
  - Localização
  - Data do anúncio
  - Quilometragem (KM)
  - Cor
  - URL do anúncio
- Armazena tudo em um `DataFrame` e salva como CSV

## 🧰 Tecnologias utilizadas

- Python 3.10+
- Selenium
- BeautifulSoup4
- Pandas
- Google Chrome (via chromedriver)

## ▶️ Como usar

1. Instale os requisitos:

```bash
pip install selenium beautifulsoup4 pandas
```

2. Certifique-se de ter o `chromedriver` compatível com sua versão do Chrome.

3. Execute o script:

```bash
python olx_crawler.py
```

4. O resultado estará em um arquivo `anuncios_olx_corrigido.csv` na mesma pasta.

## ⚠️ Observações

- A OLX pode bloquear requisições automatizadas. Recomenda-se usar `user-agent` aleatório e delays variáveis para produção.
- Nem todos os estados terão resultados o tempo todo.

## 📁 Estrutura esperada de saída (exemplo)

| Estado | Título                             | Preço      | Localização     | Data   | KM       | Cor      | URL                         |
|--------|-------------------------------------|------------|------------------|--------|----------|----------|-----------------------------|
| SP     | HB20 CONFORT 1.0 FLEX - 2023/2024   | R$ 65.000  | São Paulo - SP   | Hoje   | 20.000 km| Prata    | https://sp.olx.com.br/...   |

---

Desenvolvido com fins educacionais.
