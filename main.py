import re

import requests as requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError, ConnectionError


class VesselFinderScraper:
    def get_page(self, url, counter=10, dynamic_verification=True):
        """
        Content retriever
        :param dynamic_verification: try without SSL verify if needed
        :param url: the link whose content is to be returned
        :param counter: how many times of retrying
        :return: content of response
        """
        print(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        verify = True
        for count in range(1, counter + 1):
            try:
                response = requests.get(url, timeout=10, headers=headers, verify=verify)
                return response
            except ConnectionError as cae:
                print("A weird connection error!", count, url, cae)
                continue
            except Exception as e:
                print('Error occurred while getting page content!', count, url, e)
                if dynamic_verification and type(e) == SSLError:
                    verify = False
                continue
        raise TimeoutError

    def get_ship_data(self, imo_no):
        vesselfinder_url = "https://www.vesselfinder.com/vessels/SHIPNAME-IMO-{}-MMSI-0".format(imo_no)
        page = self.get_page(vesselfinder_url)
        soup = BeautifulSoup(page.content, "lxml")
        data = {}

        if not soup.find("div", "error-content"):
            flag_style = soup.find("div", "title-flag-icon")["style"]
            # use django's own urlize function here
            data["Flag URL"] = re.findall(r"(?P<url>https?://[^\s()]+)", flag_style)[0]
            for product in soup.find_all("tr"):
                n3 = product.find("td", "n3")
                v3 = product.find("td", "v3")
                if n3 and v3:
                    if v3.find("i", "nd"):
                        data[n3.text] = "Available to subscribed users"
                    else:
                        data[n3.text] = v3.text
        return data


def get_imo_input():
    imo_no = 0
    while len(str(imo_no)) != 7:
        try:
            imo_no = int(input("IMO: "))
        except ValueError:
            imo_no = 0
    return imo_no


def main():
    vfs = VesselFinderScraper()
    imo_no = get_imo_input()
    ship_data = vfs.get_ship_data(imo_no)

    for key, value in ship_data.items():
        print(f"{key}:", value)


if __name__ == '__main__':
    main()
