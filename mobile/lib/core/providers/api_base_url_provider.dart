import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_base_url.dart';

final apiBaseUrlProvider =
    StateNotifierProvider<ApiBaseUrlNotifier, String>((ref) => ApiBaseUrlNotifier());

class ApiBaseUrlNotifier extends StateNotifier<String> {
  ApiBaseUrlNotifier() : super(loadSavedApiBaseUrl());

  Future<void> setBaseUrl(String raw) async {
    final normalized = normalizeApiBaseUrl(raw);
    await saveApiBaseUrl(normalized);
    state = normalized;
  }
}
