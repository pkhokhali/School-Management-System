import 'package:hive_flutter/hive_flutter.dart';

/// Compile-time default (emulator). Override in app settings or via --dart-define.
const defaultApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000/api/v1',
);

const _hiveKey = 'api_base_url';

String normalizeApiBaseUrl(String raw) {
  var url = raw.trim();
  if (url.isEmpty) return defaultApiBaseUrl;
  url = url.replaceAll(RegExp(r'/+$'), '');
  if (!url.endsWith('/api/v1')) {
    if (url.endsWith('/api')) {
      url = '$url/v1';
    } else {
      url = '$url/api/v1';
    }
  }
  return url;
}

String loadSavedApiBaseUrl() {
  final box = Hive.box('settings');
  final saved = box.get(_hiveKey);
  if (saved is String && saved.isNotEmpty) {
    return normalizeApiBaseUrl(saved);
  }
  return normalizeApiBaseUrl(defaultApiBaseUrl);
}

Future<void> saveApiBaseUrl(String url) async {
  await Hive.box('settings').put(_hiveKey, normalizeApiBaseUrl(url));
}
