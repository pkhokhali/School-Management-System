import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/api_base_url_provider.dart';
import '../storage/secure_storage.dart';

Dio createDio(String baseUrl) {
  final dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 15),
    receiveTimeout: const Duration(seconds: 15),
    headers: {'Content-Type': 'application/json'},
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
            final refreshDio = Dio(BaseOptions(baseUrl: baseUrl));
            final res = await refreshDio.post(
              '/auth/token/refresh/',
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
}

final dioProvider = Provider<Dio>((ref) {
  final baseUrl = ref.watch(apiBaseUrlProvider);
  return createDio(baseUrl);
});
