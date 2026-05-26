import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../storage/secure_storage.dart';

const baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000/api/v1',
);

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 15),
    receiveTimeout: const Duration(seconds: 15),
  ));

  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) async {
      final token = await SecureStorage.getAccessToken();
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
      handler.next(options);
    },
    onError: (error, handler) async {
      if (error.response?.statusCode == 401) {
        final refresh = await SecureStorage.getRefreshToken();
        if (refresh != null) {
          try {
            final res = await Dio().post(
              '$baseUrl/auth/token/refresh/',
              data: {'refresh': refresh},
            );
            await SecureStorage.saveTokens(
              res.data['access'],
              refresh,
            );
            error.requestOptions.headers['Authorization'] =
                'Bearer ${res.data['access']}';
            final clone = await dio.fetch(error.requestOptions);
            return handler.resolve(clone);
          } catch (_) {
            await SecureStorage.clear();
          }
        }
      }
      handler.next(error);
    },
  ));

  return dio;
});
