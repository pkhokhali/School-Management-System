import 'package:dio/dio.dart';

String messageFromDio(DioException e) {
  switch (e.type) {
    case DioExceptionType.connectionError:
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.sendTimeout:
    case DioExceptionType.receiveTimeout:
      return 'Cannot reach the server. Use your PC IP (not 10.0.2.2 on a real phone), '
          'same Wi‑Fi, backend on 0.0.0.0:8000, and allow port 8000 in the firewall.';
    case DioExceptionType.badResponse:
      final data = e.response?.data;
      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }
      final code = e.response?.statusCode;
      if (code == 401) return 'Invalid email or password.';
      if (code == 403) return 'This account cannot use the mobile app.';
      if (code == 400) return 'Bad request. Check the server URL ends with /api/v1';
      return 'Server error (${code ?? 'unknown'}).';
    default:
      return e.message ?? 'Request failed.';
  }
}

String messageFromLoginError(Object e) {
  if (e is DioException) return messageFromDio(e);
  return 'Login failed: $e';
}
