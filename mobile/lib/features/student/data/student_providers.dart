import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';

List<dynamic> _asList(dynamic data) {
  if (data is List) return data;
  if (data is Map && data['results'] is List) return data['results'] as List;
  return [];
}

final studentProfileProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final res = await ref.read(dioProvider).get('/students/', queryParameters: {'page_size': 1});
  final list = _asList(res.data);
  if (list.isEmpty) return null;
  return Map<String, dynamic>.from(list.first as Map);
});

final studentEnrollmentsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final res = await ref.read(dioProvider).get(
    '/enrollment/',
    queryParameters: {'status': 'approved', 'page_size': 50},
  );
  return _asList(res.data).map((e) => Map<String, dynamic>.from(e as Map)).toList();
});

final studentFeesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final res = await ref.read(dioProvider).get('/fees/assignments/', queryParameters: {'page_size': 50});
  return _asList(res.data).map((e) => Map<String, dynamic>.from(e as Map)).toList();
});

final studentMarksProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final res = await ref.read(dioProvider).get('/results/marks/', queryParameters: {'page_size': 200});
  return _asList(res.data).map((e) => Map<String, dynamic>.from(e as Map)).toList();
});

final studentExamsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final res = await ref.read(dioProvider).get('/results/exams/', queryParameters: {'page_size': 100});
  return _asList(res.data).map((e) => Map<String, dynamic>.from(e as Map)).toList();
});

final studentAnnouncementsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final res = await ref.read(dioProvider).get('/announcements/', queryParameters: {'page_size': 20});
  return _asList(res.data).map((e) => Map<String, dynamic>.from(e as Map)).toList();
});

/// Course completion % from published exams vs student marks (until teacher progress API exists).
double courseProgressPercent(int courseId, List<Map<String, dynamic>> exams, List<Map<String, dynamic>> marks) {
  final courseExams = exams.where((e) => e['course'] == courseId).toList();
  if (courseExams.isEmpty) return 0;
  final examIds = courseExams.map((e) => e['id']).toSet();
  final done = marks.where((m) => examIds.contains(m['exam'])).length;
  return (done / courseExams.length * 100).clamp(0, 100);
}

String gradeToGpa(String? grade) {
  switch (grade?.toUpperCase()) {
    case 'A+':
      return '4.0';
    case 'A':
      return '3.7';
    case 'B+':
      return '3.3';
    case 'B':
      return '3.0';
    case 'C':
      return '2.0';
    case 'D':
      return '1.0';
    default:
      return '—';
  }
}

double averageGpaFromMarks(List<Map<String, dynamic>> marks) {
  if (marks.isEmpty) return 0;
  var sum = 0.0;
  var n = 0;
  for (final m in marks) {
    final g = m['grade']?.toString();
    if (g == null || g.isEmpty || g == 'F') continue;
    final v = double.tryParse(gradeToGpa(g));
    if (v != null && v > 0) {
      sum += v;
      n++;
    }
  }
  return n == 0 ? 0 : sum / n;
}
