import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import '../storage/secure_storage.dart';

class AuthUser {
  final String id;
  final String email;
  final String fullName;
  final String role;

  AuthUser({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
  });

  factory AuthUser.fromJson(Map<String, dynamic> j) => AuthUser(
        id: j['id'].toString(),
        email: j['email'],
        fullName: j['full_name'] ?? '',
        role: j['role'],
      );
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthUser?>((ref) {
  return AuthNotifier(ref);
});

class AuthNotifier extends StateNotifier<AuthUser?> {
  AuthNotifier(this.ref) : super(null) {
    _load();
  }

  final Ref ref;

  Future<void> _load() async {
    final json = await SecureStorage.getUser();
    if (json != null) {
      state = AuthUser.fromJson(jsonDecode(json));
    }
  }

  Future<bool> login(String email, String password) async {
    final dio = ref.read(dioProvider);
    final res = await dio.post('/auth/login/', data: {
      'email': email,
      'password': password,
      'client_type': 'mobile',
    });
    await SecureStorage.saveTokens(res.data['access'], res.data['refresh']);
    final user = AuthUser.fromJson(res.data['user']);
    await SecureStorage.saveUser(jsonEncode(res.data['user']));
    state = user;
    return true;
  }

  Future<void> logout() async {
    await SecureStorage.clear();
    state = null;
  }
}
