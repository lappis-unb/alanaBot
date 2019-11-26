import sys
sys.path.append('../')
from crawler.crawl import Crawl  # noqa: E402
import constants  # noqa: E402


class CrawlSenado(Crawl):
    def __init__(self):
        self.api_url = constants.URL_API_SENADO
        self.web_url = constants.URL_WEB_SENADO
        Crawl.__init__(self)

    def crawl_tramitacao(self, proposicao_id):
        """
        Returns Tramitação from specific pl

        Args
        -----------
        proposicao_id:
            dict -> json returned on specific pl request

        Returns
        --------
        string -> Tramitação from specific pl
        """
        try:
            soup = self.get_page_content(constants.URL_WEB_SENADO +
                                         "web/atividade/materias/-/materia/" +
                                         f"{proposicao_id}")
            page_content = soup.find("div",
                                     {"id": "conteudoProjeto"})
            tramitacao = page_content.find("div",
                                           {"id": "tramitacao"})
            div_tramitacao = tramitacao.find_all(
                "div",
                {"data-local": "COMISSOES"})[0]

            tramitacao_dls = div_tramitacao.find_all("dd")
            tramitacao_dts = div_tramitacao.find_all("dt")

            text_tramitacao_dls = [tramitacao_dl.text for tramitacao_dl in
                                   tramitacao_dls]
            text_tramitacao_dts = [tramitacao_dt.text for tramitacao_dt in
                                   tramitacao_dts]

            tramitacao_data = dict(zip(text_tramitacao_dts,
                                       text_tramitacao_dls))
            tramitacao = tramitacao_data['Ação:']
        except AttributeError:
            tramitacao = None
        return tramitacao
