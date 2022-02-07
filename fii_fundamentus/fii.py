import requests
from requests.models import Response
from bs4 import BeautifulSoup

class TickerNotFoundError(Exception):
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.message = f'Could not retrieve data for {self.ticker}'
        super().__init__(self.message)

class HTMLPaseError(Exception):
    def __init__(self, title) -> None:
        self.ticker = title
        self.message = f'Error parsing the HTML data of the page: {title}'
        super().__init__(self.message)

def get_html_data(ticker: str) -> Response:
    url = f'https://www.fundamentus.com.br/detalhes.php?papel={ticker}'
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            }

    html = requests.get(url, headers=header)
    if 'Nenhum papel encontrado' in html.text \
            or ticker not in html.text \
            or html.status_code != 200:
        raise TickerNotFoundError(ticker)
    
    return html

def parse_html(soup:BeautifulSoup, label_class:str, label_text:str, value_class:str) -> str:
    span_label = soup.find(class_=label_class, text=label_text)
    if span_label is None:
        raise HTMLPaseError(soup.title.text)
    span_value = span_label.find_next(class_=value_class)
    if span_value is None:
        raise HTMLPaseError(soup.title.text)
    return span_value.text

def get_value_per_share(soup: BeautifulSoup) -> str:
    vps = parse_html(soup, label_class='txt', label_text='VP/Cota', value_class='data w2')
    vps = vps.replace(',', '.')
    return vps

def get_price(soup: BeautifulSoup) -> str:
    price = parse_html(soup, label_class='txt', label_text='Cotação', value_class='data destaque w3')
    price = price.replace(',', '.')
    return price

def get_total_shares(soup: BeautifulSoup) -> str:
    shares = parse_html(soup, label_class='txt', label_text='Nro. Cotas', value_class='data w3')
    shares = shares.replace('.', '')
    return shares

def get_net_worth(soup: BeautifulSoup) -> str:
    net_worth = parse_html(soup, label_class='txt', label_text='Patrim Líquido', value_class='data w1')
    net_worth = net_worth.replace('.', '').replace(',', '')
    return net_worth

def get_fund_name(soup: BeautifulSoup) -> str:
    name = parse_html(soup, label_class='txt', label_text='Nome', value_class='data')
    name = name.upper()
    return name

def get_dividends_12m(soup: BeautifulSoup) -> str:
    dividends = parse_html(soup, label_class='txt', label_text='Dividendo/cota', value_class='data w2')
    dividends = dividends.replace(',', '.')
    return dividends

def get_dividend_yield(soup: BeautifulSoup) -> str:
    dividend_yield = parse_html(soup, label_class='txt', label_text='Div. Yield', value_class='data')
    dividend_yield = dividend_yield.replace(',', '.')
    return dividend_yield

def get_fii_info(ticker: str) -> dict:
    try:
        html = get_html_data(ticker)
        html.status_code
    except TickerNotFoundError as err:
        return {'message': err.message,
                'error': True}

    try:
        soup = BeautifulSoup(html.text, features='html.parser')

        fii_info = {
            'name': get_fund_name(soup),
            'price': get_price(soup),
            'total_shares': get_total_shares(soup),
            'net_worth': get_net_worth(soup),
            'value_per_share': get_value_per_share(soup),
            'dividends_12m': get_dividends_12m(soup),
            'dividend_yield': get_dividend_yield(soup),
        }
        fii_info['PVP'] = round(float(fii_info['price']) / float(fii_info['value_per_share']), 2)
    except HTMLPaseError as err:
        return {'message': err.message,
                'error': True}

    return fii_info

if __name__ == '__main__':
    pass