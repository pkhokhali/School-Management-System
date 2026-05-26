import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/api/api_errors.dart';
import '../../core/api/api_client.dart';
import '../../core/providers/api_base_url_provider.dart';
import '../../core/providers/auth_provider.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _email = TextEditingController(text: 'student1@institute.edu.np');
  final _password = TextEditingController(text: 'student123');
  final _serverUrl = TextEditingController();
  bool _serverUrlInitialized = false;
  bool _loading = false;
  bool _testingServer = false;
  String? _error;
  String? _serverStatus;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _serverUrl.dispose();
    super.dispose();
  }

  Future<void> _applyServerUrl() async {
    await ref.read(apiBaseUrlProvider.notifier).setBaseUrl(_serverUrl.text);
    if (mounted) {
      setState(() {
        _serverUrl.text = ref.read(apiBaseUrlProvider);
        _serverStatus = 'Server URL saved.';
        _error = null;
      });
    }
  }

  Future<void> _testServer() async {
    setState(() {
      _testingServer = true;
      _serverStatus = null;
      _error = null;
    });
    try {
      await ref.read(apiBaseUrlProvider.notifier).setBaseUrl(_serverUrl.text);
      final res = await ref.read(dioProvider).get('/features/');
      if (mounted) {
        setState(() {
          _serverUrl.text = ref.read(apiBaseUrlProvider);
          _serverStatus = 'Server OK (${res.statusCode}). You can log in.';
        });
      }
    } on DioException catch (e) {
      if (mounted) {
        setState(() => _serverStatus = messageFromDio(e));
      }
    } catch (e) {
      if (mounted) setState(() => _serverStatus = e.toString());
    } finally {
      if (mounted) setState(() => _testingServer = false);
    }
  }

  Future<void> _login() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await ref.read(apiBaseUrlProvider.notifier).setBaseUrl(_serverUrl.text);
      await ref.read(authProvider.notifier).login(_email.text.trim(), _password.text);
      if (mounted) context.go('/home');
    } catch (e) {
      if (mounted) {
        setState(() => _error = messageFromLoginError(e));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentUrl = ref.watch(apiBaseUrlProvider);
    if (!_serverUrlInitialized) {
      _serverUrl.text = currentUrl;
      _serverUrlInitialized = true;
    }

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Institute App',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'API: $currentUrl',
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              TextField(
                controller: _email,
                keyboardType: TextInputType.emailAddress,
                autocorrect: false,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _password,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Password',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              ExpansionTile(
                title: const Text('Server settings'),
                subtitle: const Text('Required on a real phone — use your PC IP'),
                children: [
                  TextField(
                    controller: _serverUrl,
                    decoration: const InputDecoration(
                      labelText: 'API base URL',
                      hintText: 'http://192.168.1.10:8000/api/v1',
                      border: OutlineInputBorder(),
                      helperText: 'Phone and PC must be on the same Wi‑Fi',
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: _testingServer ? null : _testServer,
                          child: _testingServer
                              ? const SizedBox(
                                  height: 18,
                                  width: 18,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Text('Test server'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: _applyServerUrl,
                          child: const Text('Save URL'),
                        ),
                      ),
                    ],
                  ),
                  if (_serverStatus != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      _serverStatus!,
                      style: TextStyle(
                        color: _serverStatus!.startsWith('Server OK')
                            ? Colors.green.shade700
                            : Colors.orange.shade800,
                      ),
                    ),
                  ],
                ],
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: const TextStyle(color: Colors.red)),
              ],
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _loading ? null : _login,
                child: _loading
                    ? const SizedBox(
                        height: 22,
                        width: 22,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Login'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
