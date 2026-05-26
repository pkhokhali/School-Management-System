import 'package:flutter_test/flutter_test.dart';
import 'package:institute_mobile/offline/offline_sync.dart';
import 'package:hive_flutter/hive_flutter.dart';

void main() {
  test('offline queue stores record', () async {
    await Hive.initFlutter();
    await Hive.openBox('offline_attendance');
    await OfflineSync.queueRecord(
      sessionId: 1,
      payload: 'STU:1:abc',
      status: 'present',
    );
    expect(Hive.box('offline_attendance').isNotEmpty, true);
  });
}
