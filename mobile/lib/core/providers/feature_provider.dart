import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';

final featureFlagsProvider = FutureProvider<Map<String, bool>>((ref) async {
  final dio = ref.read(dioProvider);
  final res = await dio.get('/features/');
  return Map<String, bool>.from(res.data['feature_flags'] ?? {});
});

bool isFeatureEnabled(Map<String, bool>? flags, String key) {
  return flags?[key] ?? false;
}
