import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../../core/api/api_client.dart';
import '../../offline/offline_sync.dart';

class AttendanceScanScreen extends ConsumerStatefulWidget {
  const AttendanceScanScreen({super.key});

  @override
  ConsumerState<AttendanceScanScreen> createState() => _AttendanceScanScreenState();
}

class _AttendanceScanScreenState extends ConsumerState<AttendanceScanScreen> {
  List<dynamic> _classes = [];
  int? _sessionId;
  bool _loading = true;
  bool _syncing = false;
  int _pending = 0;
  bool _scanBusy = false;
  final MobileScannerController _scanner = MobileScannerController();

  @override
  void initState() {
    super.initState();
    _refreshPending();
    _loadClasses();
    WidgetsBinding.instance.addPostFrameCallback((_) => _tryAutoSync());
  }

  @override
  void dispose() {
    _scanner.dispose();
    super.dispose();
  }

  void _refreshPending() {
    setState(() => _pending = OfflineSync.pendingCount);
  }

  Future<void> _loadClasses() async {
    setState(() => _loading = true);
    try {
      final today = DateTime.now().toIso8601String().substring(0, 10);
      final res = await ref.read(dioProvider).get(
        '/attendance/sessions/my-classes/',
        queryParameters: {'date': today},
      );
      final list = res.data is List ? res.data as List : (res.data['results'] as List? ?? []);
      setState(() {
        _classes = list;
        if (_sessionId == null && list.isNotEmpty) {
          _sessionId = list.first['id'] as int?;
        }
      });
    } catch (_) {
      final fallback = await ref.read(dioProvider).get(
        '/attendance/sessions/',
        queryParameters: {'date': DateTime.now().toIso8601String().substring(0, 10)},
      );
      final list = fallback.data is List ? fallback.data as List : (fallback.data['results'] as List? ?? []);
      setState(() {
        _classes = list;
        if (_sessionId == null && list.isNotEmpty) {
          _sessionId = list.first['id'] as int?;
        }
      });
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _tryAutoSync() async {
    if (_pending == 0) return;
    await _syncPending(silent: true);
  }

  Future<void> _syncPending({bool silent = false}) async {
    if (_pending == 0) {
      if (!silent && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('No offline scans to sync')));
      }
      return;
    }
    setState(() => _syncing = true);
    try {
      final result = await OfflineSync.syncAll(ref.read(dioProvider));
      _refreshPending();
      if (!mounted) return;
      if (result.synced > 0 || result.failed > 0) {
        final msg = result.failed > 0
            ? 'Synced ${result.synced}, failed ${result.failed}.${result.errors.isNotEmpty ? ' ${result.errors.first}' : ''}'
            : 'Synced ${result.synced} offline scan(s)';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
      }
    } on DioException catch (e) {
      if (!silent && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.response?.data?['detail']?.toString() ?? 'Sync failed')),
        );
      }
    } finally {
      if (mounted) setState(() => _syncing = false);
    }
  }

  Future<({double? lat, double? lng})> _readGps() async {
    try {
      if (!await Geolocator.isLocationServiceEnabled()) return (lat: null, lng: null);
      var perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) perm = await Geolocator.requestPermission();
      if (perm == LocationPermission.denied || perm == LocationPermission.deniedForever) {
        return (lat: null, lng: null);
      }
      final pos = await Geolocator.getCurrentPosition();
      return (lat: pos.latitude, lng: pos.longitude);
    } catch (_) {
      return (lat: null, lng: null);
    }
  }

  Map<String, dynamic>? get _selectedClass {
    if (_sessionId == null) return null;
    for (final c in _classes) {
      if (c['id'] == _sessionId) return Map<String, dynamic>.from(c as Map);
    }
    return null;
  }

  Future<void> _onScan(String code) async {
    if (_sessionId == null || _scanBusy) return;
    setState(() => _scanBusy = true);
    final gps = await _readGps();
    final sel = _selectedClass;
    final body = <String, dynamic>{
      'session_id': _sessionId,
      'payload': code,
      if (gps.lat != null) 'gps_lat': gps.lat,
      if (gps.lng != null) 'gps_lng': gps.lng,
    };
    if (sel != null) {
      body['date'] = sel['date'];
      body['batch'] = sel['batch'];
      body['course'] = sel['course'];
      body['period'] = sel['period'] ?? 1;
    }
    try {
      await ref.read(dioProvider).post('/attendance/qr-mark/', data: body);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Marked present')));
      }
    } on DioException catch (e) {
      if (OfflineSync.shouldQueueOffline(e)) {
        await OfflineSync.queueRecord(
          sessionId: _sessionId!,
          payload: code,
          gpsLat: gps.lat,
          gpsLng: gps.lng,
          date: sel?['date']?.toString(),
          batch: sel?['batch'] as int?,
          course: sel?['course'] as int?,
          period: sel?['period'] as int? ?? 1,
        );
        _refreshPending();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Saved offline — tap Sync when back online')),
          );
        }
      } else if (mounted) {
        final detail = e.response?.data is Map ? e.response?.data['detail'] : null;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(detail?.toString() ?? 'Could not mark attendance')),
        );
      }
    } finally {
      if (mounted) setState(() => _scanBusy = false);
    }
  }

  String _classLabel(dynamic s) {
    if (s['register_label'] != null) return s['register_label'].toString();
    final period = (s['period'] ?? 1) > 1 ? ' · P${s['period']}' : '';
    final shift = s['shift_name'] != null ? ' · ${s['shift_name']}' : '';
    return '${s['batch_name']} · ${s['course_name']}$period$shift';
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
          child: _loading
              ? const LinearProgressIndicator()
              : _classes.isEmpty
                  ? const Text('No classes assigned for today. Contact academic office.')
                  : DropdownButtonFormField<int>(
                      value: _sessionId,
                      decoration: const InputDecoration(
                        labelText: 'Class register (today)',
                        border: OutlineInputBorder(),
                      ),
                      items: _classes
                          .map((s) => DropdownMenuItem<int>(
                                value: s['id'] as int,
                                child: Text(_classLabel(s), overflow: TextOverflow.ellipsis),
                              ))
                          .toList(),
                      onChanged: (v) => setState(() => _sessionId = v),
                    ),
        ),
        if (_pending > 0)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            child: Row(
              children: [
                Expanded(
                  child: Text('$_pending scan(s) waiting to sync', style: Theme.of(context).textTheme.bodySmall),
                ),
                FilledButton.tonal(
                  onPressed: _syncing ? null : () => _syncPending(),
                  child: _syncing
                      ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Sync now'),
                ),
              ],
            ),
          ),
        Expanded(
          child: _sessionId == null
              ? const Center(child: Text('Select your class to start scanning'))
              : MobileScanner(
                  controller: _scanner,
                  onDetect: (capture) async {
                    final barcodes = capture.barcodes;
                    final code = barcodes.isEmpty ? null : barcodes.first.rawValue;
                    if (code == null) return;
                    await _onScan(code);
                  },
                ),
        ),
      ],
    );
  }
}
