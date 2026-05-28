import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../widgets/student_ui.dart';

class StudentResultsTab extends ConsumerWidget {
  const StudentResultsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final marks = ref.watch(studentMarksProvider);

    return marks.when(
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (list) {
        if (list.isEmpty) {
          return const Column(
            children: [
              StudentNavyHeader(title: 'Results', subtitle: 'Published marks'),
              Expanded(
                child: Center(
                  child: Text('No published results yet', style: TextStyle(color: StudentPalette.textMuted)),
                ),
              ),
            ],
          );
        }

        final gpa = averageGpaFromMarks(list);
        var totalMarks = 0.0;
        var count = 0;
        for (final m in list) {
          final t = double.tryParse('${m['total_marks']}') ?? 0;
          if (t > 0) {
            totalMarks += t;
            count++;
          }
        }
        final avgPct = count > 0 ? (totalMarks / count) : 0.0;
        final term = list.first['term']?.toString() ?? 'Latest';

        final bySubject = <String, Map<String, dynamic>>{};
        for (final m in list) {
          final key = m['subject_name']?.toString() ?? m['exam_name']?.toString() ?? 'Subject';
          bySubject[key] = m;
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            StudentNavyHeader(
              title: 'Results',
              subtitle: '$term · Summary',
              stats: [
                (value: gpa > 0 ? gpa.toStringAsFixed(1) : '—', label: 'GPA', valueColor: null),
                (value: '${avgPct.round()}%', label: 'Avg', valueColor: const Color(0xFF4ADE80)),
                (value: '${bySubject.length}', label: 'Subjects', valueColor: null),
              ],
            ),
            Expanded(
              child: RefreshIndicator(
                color: StudentPalette.indigo,
                onRefresh: () async => ref.invalidate(studentMarksProvider),
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(14, 12, 14, 24),
                  children: [
                    const StudentSectionHeader(title: 'Subject breakdown'),
                    ...bySubject.entries.map((e) {
                      final m = e.value;
                      final grade = m['grade']?.toString() ?? '—';
                      return StudentCard(
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(e.key, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                                  Text(
                                    'Internal ${m['internal_marks']} · Final ${m['external_marks']}',
                                    style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
                                  ),
                                ],
                              ),
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(
                                  grade,
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w800,
                                    color: grade == 'F' ? StudentPalette.error : StudentPalette.success,
                                  ),
                                ),
                                Text(
                                  '${m['total_marks']}/100',
                                  style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
                                ),
                              ],
                            ),
                          ],
                        ),
                      );
                    }),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('PDF download — use admin portal marksheet')),
                              );
                            },
                            icon: const Icon(Icons.download, size: 18, color: StudentPalette.indigo),
                            label: const Text('Download PDF', style: TextStyle(color: StudentPalette.indigo)),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
