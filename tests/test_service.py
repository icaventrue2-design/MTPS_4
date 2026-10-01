from unittest.mock import Mock, patch
import pytest
import requests
from src.service import PaymentService


def test_process_payment_success():
    # Arrange
    service = PaymentService()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "tx_id": "txn_123"}

    # Act & Assert
    with patch("src.service.requests.post") as mock_post:
        mock_post.return_value = mock_response
        result = service.process_payment(amount=100.0, card_token="tok_visa_1234")

        # Проверка возвращаемого значения
        assert result == {"success": True, "tx_id": "txn_123"}

        # Проверка количества вызовов
        mock_post.assert_called_once()

        # Проверка передаваемых аргументов (URL, json, headers, timeout)
        mock_post.assert_called_once_with(
            "https://api.payments.example/v1/charge",
            json={
                "amount": 100.0,
                "currency": "RUB",
                "card_token": "tok_visa_1234",
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk_test_123",
            },
            timeout=5,
        )


def test_process_payment_bank_failure():
    # Arrange
    service = PaymentService()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "failure",
        "reason": "insufficient_funds",
    }

    # Act & Assert
    with patch("src.service.requests.post") as mock_post:
        mock_post.return_value = mock_response
        result = service.process_payment(amount=500.0, card_token="tok_visa_5678")

        assert result == {"success": False, "error": "insufficient_funds"}
        mock_post.assert_called_once()


def test_process_payment_timeout():
    # Arrange
    service = PaymentService()

    # Act & Assert
    with patch("src.service.requests.post") as mock_post:
        # Мокируем выброс ошибки таймаута
        mock_post.side_effect = requests.Timeout()

        result = service.process_payment(amount=100.0, card_token="tok_visa_1234")

        assert result == {"success": False, "error": "timeout"}
        mock_post.assert_called_once()


def test_process_payment_connection_error():
    # Arrange
    service = PaymentService()

    # Act & Assert
    with patch("src.service.requests.post") as mock_post:
        # Мокируем сетевую ошибку
        mock_post.side_effect = requests.ConnectionError()

        result = service.process_payment(amount=100.0, card_token="tok_visa_1234")

        assert result == {"success": False, "error": "network_error"}
        mock_post.assert_called_once()