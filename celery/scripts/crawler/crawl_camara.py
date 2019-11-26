import sys
sys.path.append('../')
from crawler.crawl import Crawl  # noqa: E402
import constants  # noqa: E402


class CrawlCamara(Crawl):
    def __init__(self):
        self.api_url = constants.URL_API_CAMARA
        self.web_url = constants.SITE_CAMARA
        Crawl.__init__(self)

    def crawl_apreciacao(self, json_projeto):
        """
        json_projeto:
            dict -> json returned on specific pl request

        Returns
        --------
        string -> Apreciação from specific pl
        """
        try:
            proposicao = str(json_projeto["dados"]["id"])
            soup = self.get_page_content(self.web_url +
                                         "proposicoesWeb/fichadetramitacao" +
                                         f"?idProposicao={proposicao}")
            div_apreciacao = soup.find("div",
                                       {"id": "informacoesDeTramitacao"})
            paragraph_apreciacao = div_apreciacao.find('p')
            paragraph_apreciacao.strong.decompose()
            apreciacao = paragraph_apreciacao.text.strip()
        except AttributeError:
            apreciacao = None
        return apreciacao

    def crawl_apensados(self, json_projeto):
        """
        json_projeto:
            dict -> json returned on specific pl request

        Returns
        --------
        string -> PL's apensados from specific pl
        """
        proposicao = str(json_projeto["dados"]["id"])
        soup = self.get_page_content(self.web_url +
                                     "proposicoesWeb/fichadetramitacao" +
                                     f"?idProposicao={proposicao}")
        try:
            pls_apensados = []
            div_apensada = soup.find("div", {"id": "divResumoApensados"})
            paragraph_apensada = div_apensada.find('p')
            pls_apensados.append(paragraph_apensada.find('strong').text)
        except AttributeError:
            try:
                div_apensada = soup.find("a", {"id": "lnkArvoreDeApensados"})
                new_soup = self.get_page_content(self.web_url +
                                                 "proposicoesWeb/"
                                                 f"{div_apensada.get('href')}")
                uls = new_soup.find("ul", {"class": "linkProposicao"})
                lis = uls.find_all('li')
                for li in lis:
                    lower_li = li.span.text.lower().strip()
                    if lower_li.startswith('pl'):
                        pls_apensados.append(li.span.text)
            except AttributeError:
                return None
        except IndexError:
            return None
        else:
            return pls_apensados[0]
