import 'package:dio/dio.dart';
import 'package:hive_flutter/hive_flutter.dart';

class OfflineSyncResult {
  final int synced;
  final int failed;
  final List<String> errors;

  const OfflineSyncResult({
    required this.synced,
    required this.failed,
    this.errors = const [],
  });
}

class OfflineSync {
  static Box get _box => Hive.box('offline_attendance');

  static int get pendingCount => _box.length;

  static List<Map<String, dynamic>> pendingRecords() {
    return _box.toMap().entries.map((e) {
      final v = Map<String, dynamic>.from(e.value as Map);
      v['client_key'] = e.key.toString();
      return v;
    }).toList();
  }

  static Future<void> queueRecord({
    required int sessionId,
    required String payload,
    String status = 'present',
    double? gpsLat,
    double? gpsLng,
    String? date,
    int? batch,
    int? course,
    int period = 1,
  }) async {
    final key = DateTime.now().millisecondsSinceEpoch.toString();
    await _box.put(key, {
      'session_id': sessionId,
      'payload': payload,
      'status': status,
      'source': 'qr',
      if (gpsLat != null) 'gps_lat': gpsLat,
      if (gpsLng != null) 'gps_lng': gpsLng,
      if (date != null) 'date': date,
      if (batch != null) 'batch': batch,
      if (course != null) 'course': course,
      'period': period,
      'queued_at': DateTime.now().toIso8601String(),
    });
  }

  static Future<void> removeKeys(Iterable<String> keys) async {
    for (final key in keys) {
      await _box.delete(key);
    }
  }

  static Future<OfflineSyncResult> syncAll(Dio dio) async {
    final pending = _box.toMap();
    if (pending.isEmpty) {
      return const OfflineSyncResult(synced: 0, failed: 0);
    }

    final records = <Map<String, dynamic>>[];
    for (final entry in pending.entries) {
      final v = Map<String, dynamic>.from(entry.value as Map);
      records.add({
        'client_key': entry.key.toString(),
        if (v['session_id'] != null) 'session_id': v['session_id'],
        'payload': v['payload'],
        'status': v['status'],
        'source': v['source'],
        if (v['gps_lat'] != null) 'gps_lat': v['gps_lat'],
        if (v['gps_lng'] != null) 'gps_lng': v['gps_lng'],
        if (v['date'] != null) 'date': v['date'],
        if (v['batch'] != null) 'batch': v['batch'],
        if (v['course'] != null) 'course': v['course'],
        if (v['period'] != null) 'period': v['period'],
      });
    }

    final response = await dio.post('/attendance/offline-sync/', data: {'records': records});
    final data = response.data as Map<String, dynamic>;
    final synced = (data['synced'] as List? ?? [])
        .map((e) => Map<String, dynamic>.from(e as Map))
        .toList();
    final failed = (data['failed'] as List? ?? [])
        .map((e) => Map<String, dynamic>.from(e as Map))
        .toList();

    final keysToRemove = synced
        .map((r) => r['client_key']?.toString())
        .whereType<String>()
        .where((k) => k.isNotEmpty);
    await removeKeys(keysToRemove);

    final errors = failed
        .map((r) => r['error']?.toString())
        .whereType<String>()
        .where((e) => e.isNotEmpty)
        .toList();

    return OfflineSyncResult(
      synced: synced.length,
      failed: failed.length,
      errors: errors,
    );
  }

  static bool shouldQueueOffline(DioException error) {
    if (error.type == DioExceptionType.connectionError ||
        error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return true;
    }
    final code = error.response?.statusCode;
    return code == null || code >= 500;
  }
}
