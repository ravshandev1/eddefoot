import json
import requests
from payme.cards.subscribe_cards import PaymeSubscribeCards

client = PaymeSubscribeCards(
    base_url="https://checkout.test.paycom.uz/api/",
    paycom_id="5e730e8e0b852a417aa49ceb"
)


class PaymeSubscribeReceipts:
    __CACHE_CONTROL = "no-cache"
    __CONTENT_TYPE = "application/json"
    __P2P_DESCRIPTION = "P2P Transaction"

    def __init__(self, base_url: str, id_payme: str, key_payme: str) -> None:
        self.__base_url: str = base_url
        self.__headers: dict = {
            "X-Auth": f"{id_payme}:{key_payme}",
            "Content-Type": self.__CONTENT_TYPE,
            "Cache-Control": self.__CACHE_CONTROL,
        }
        self.__methods: dict = {
            "receipts_get": "receipts.get",
            "receipts_pay": "receipts.pay",
            "receipts_send": "receipts.send",
            "receipts_check": "receipts.check",
            "receipts_cancel": "receipts.cancel",
            "receipts_create": "receipts.create",
            "receipts_create_p2p": "receipts.p2p",
        }

    def __request(self, card_info: dict) -> dict:
        context: dict = {
            "data": card_info,
            "url": self.__base_url,
            "headers": self.__headers,
        }
        return requests.post(**context).json()

    def receipts_create(self, _id: int, amount: float, order_id: int, title: str) -> dict:
        """Creating a payment receipt"""
        context: dict = {
            "id": _id,
            "method": self.__methods.get("receipts_create"),
            "params": {
                "amount": amount,
                "account": {
                    "order_id": order_id,
                },
                "items": [
                    {
                        "title": title,
                        "price": amount,
                        "count": 1,
                        "code": 'something',
                        "vat_percent": 12,
                        "package_code": '123456',
                    }
                ]
            }
        }
        return self.__request(self._parse_to_json(**context))

    def receipts_create_p2p(self, _id: int, token: str, amount: float) -> dict:
        """P2P Transaction"""
        context: dict = {
            "id": _id,
            "method": self.__methods.get("receipts_create_p2p"),
            "params": {
                "token": token,
                "amount": amount,
                "description": self.__P2P_DESCRIPTION
            }
        }
        return self.__request(self._parse_to_json(**context))

    def receipts_pay(self, _id: int, invoice_id: str, token: str, phone: str) -> dict:
        """Pay receipt"""
        context: dict = {
            "id": _id,
            "method": self.__methods.get("receipts_pay"),
            "params": {
                "id": invoice_id,
                "token": token,
                "payer": {
                    "phone": phone,
                }
            }
        }
        return self.__request(self._parse_to_json(**context))

    def receipts_send(self, _id: int, invoice_id: str, phone: str) -> dict:
        """The method is used to send a payment receipt in an SMS message"""
        context: dict = {
            "id": _id,
            "method": self.__methods.get('receipts_send'),
            "params": {
                "id": invoice_id,
                "phone": phone
            }
        }
        return self.__request(self._parse_to_json(**context))

    def receipts_cancel(self, _id: int, invoice_id: str) -> dict:
        """Placing a paid receipt in the cancellation queue"""
        context: dict = {
            "id": _id,
            "method": self.__methods.get('receipts_cancel'),
            "params": {
                "id": invoice_id
            }
        }

        return self.__request(self._parse_to_json(**context))

    def receipts_check(self, _id: int, invoice_id: str) -> dict:
        """Check status receipt"""
        context: dict = {
            "id": _id,
            "method": self.__methods.get('receipts_check'),
            "params": {
                "id": invoice_id
            }
        }

        return self.__request(self._parse_to_json(**context))

    def reciepts_get(self, _id: int, invoice_id: str) -> dict:
        """Checking the status of the receipt"""
        context: dict = {
            "id": _id,
            "method": self.__methods.get('receipts_get'),
            "params": {
                "id": invoice_id
            }
        }

        return self.__request(self._parse_to_json(**context))

    def reciepts_get_all(self, _id: int, count: int, _from: str, to: str, offset: str) -> dict:
        """Full information on receipts for a certain period"""
        context: dict = {
            "id": _id,
            "method": self.__methods.get('receipts_get_all'),
            "params": {
                "count": count,
                "from": _from,
                "to": to,
                "offset": offset
            }
        }
        return self.__request(self._parse_to_json(**context))

    @staticmethod
    def _parse_to_json(**kwargs) -> dict:
        context: dict = {
            "id": kwargs.pop("id"),
            "method": kwargs.pop("method"),
            "params": kwargs.pop("params"),
        }
        return json.dumps(context)


client_receipt = PaymeSubscribeReceipts(
    base_url="https://checkout.test.paycom.uz/api/",
    id_payme="5e730e8e0b852a417aa49ceb",
    key_payme="ZPDODSiTYKuX0jyO7Kl2to4rQbNwG08jbghj"
)
