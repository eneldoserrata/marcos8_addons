import urllib2
import httplib
import json
import ssl

# have to export the DER certify recived from azul to base64
# openssl x509 -inform der -in MYCERT.cer -out my_cert.crt
# I ended up solving this by concatenating
# the private key you use to generate crs with your converted cert
# cat my_key.key my_cert.crt > certify.pem
CERT = "~/cartone.pem"
CERT1 = "~ROOT-CA-NEW_v2.1cer"
CERT2 = "~/CA-INTER-NEW_v2.1cer"

URL = "https://pruebas.azul.com.do/Webservices/JSON/default.aspx"
HOST = "pruebas.azul.com.do"

tarjetas = {"visa_aprove": "4012000077777777",
            "visa_decline": "4012000088888886",
            "mastercard_aprove": "5424180279791773",
            "mastercard_decline": "5424180279791740",
            "discover_aprove": "6011000991200035",
            "discover_aprove": "6011000990099826"}

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    """Class to allow a certificate to be uploaded
    by the client."""
    def __init__(self, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=10):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        return httplib.HTTPSConnection(host, cert_file=self.cert, timeout=timeout, context=context)



tx_bpd_request = {"Channel": "EC",
                  "Store": "39040200107",
                  "CardNumber": tarjetas["visa_aprove"],
                  "Expiration": "201512",
                  "CVC": "123",
                  "PosInputMode": "E-Commerce",
                  "TrxType": "Sale",
                  "Amount": "650730",
                  "Itbis": "99264",
                  "CurrencyPosCode": "$",
                  "Payments": "1",
                  "Plan": "0",
                  "AcquirerRefData": "1",
                  "RRN": "null",
                  "CustomerServicePhone": "809-111-2222",
                  "OrderNumber": "234",
                  "ECommerceUrl": "cartone.com.do",
                  "CustomOrderId": "ABC123"}


opener = urllib2.build_opener(HTTPSClientAuthHandler(cert=CERT))
urllib2.install_opener(opener)

request = urllib2.Request(URL)
request.add_header("Content-Type", "application/json")
request.add_header("Auth1", "cartone")
request.add_header("Auth2", "cartone")

request.add_data(json.dumps(tx_bpd_request))
request.method = lambda: "POST"

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_default_certs()


response = urllib2.urlopen(request, context=context)
# response = opener.open(request)
print response.read()