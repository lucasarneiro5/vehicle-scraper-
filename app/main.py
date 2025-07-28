from dotenv import load_dotenv
import scraper
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

def main():
    scraper.main()

if __name__ == "__main__":
    main()
