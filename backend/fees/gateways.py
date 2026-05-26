"""Payment gateway adapters - mock verify for MVP."""
from abc import ABC, abstractmethod


class PaymentGateway(ABC):
    @abstractmethod
    def initiate(self, amount: float, ref: str) -> dict:
        pass

    @abstractmethod
    def verify(self, transaction_ref: str) -> bool:
        pass


class EsewaGateway(PaymentGateway):
    def initiate(self, amount, ref):
        return {'payment_url': f'https://esewa.com.np/mock?amt={amount}&ref={ref}', 'ref': ref}

    def verify(self, transaction_ref):
        return transaction_ref.startswith('ESW-')


class KhaltiGateway(PaymentGateway):
    def initiate(self, amount, ref):
        return {'payment_url': f'https://khalti.com/mock?amt={amount}&ref={ref}', 'ref': ref}

    def verify(self, transaction_ref):
        return transaction_ref.startswith('KHT-')


class ConnectIPSGateway(PaymentGateway):
    def initiate(self, amount, ref):
        return {'payment_url': f'https://connectips.com/mock?ref={ref}', 'ref': ref}

    def verify(self, transaction_ref):
        return transaction_ref.startswith('CIPS-')


class FonepayGateway(PaymentGateway):
    """Fonepay QR / dynamic merchant integration (mock for dev)."""

    def initiate(self, amount, ref):
        return {
            'payment_url': f'https://fonepay.mock/pay?amount={amount}&merchant_ref={ref}',
            'ref': ref,
            'gateway': 'fonepay',
            'qr_payload': f'FONEPAY|{ref}|{amount}',
        }

    def verify(self, transaction_ref):
        return transaction_ref.upper().startswith('FPY-') or transaction_ref.upper().startswith('FONEPAY-')


GATEWAYS = {
    'esewa': EsewaGateway(),
    'khalti': KhaltiGateway(),
    'connect_ips': ConnectIPSGateway(),
    'fonepay': FonepayGateway(),
}
