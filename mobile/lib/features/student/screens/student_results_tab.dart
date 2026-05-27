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
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.mint)),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (list) {
        if (list.isEmpty) {
          return const Center(
            child: Text(
              'No published results yet',
              style: TextStyle(color: StudentPalette.textMuted),
            ),
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

        return RefreshIndicator(
          color: StudentPalette.mint,
          onRefresh: () async => ref.invalidate(studentMarksProvider),
          child: ListView(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
            children: [
              Row(
                children: [
                  const Expanded(
                    child: Text(
                      'My Results',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600, color: StudentPalette.textPrimary),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF22C55E).withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '$term',
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF4ADE80)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: StudentPalette.teal.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$term · Summary',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        _stat('GPA', gpa > 0 ? gpa.toStringAsFixed(1) : '—'),
                        _stat('Avg', '${avgPct.round()}%'),
                        _stat('Subjects', '${bySubject.length}'),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              const StudentSectionTitle('Subject breakdown'),
              ...bySubject.entries.map((e) {
                final m = e.value;
                final grade = m['grade']?.toString() ?? '—';
                final internal = m['internal_marks'];
                final external = m['external_marks'];
                final total = m['total_marks'];
                return StudentDarkRow(
                  icon: Icons.grade_outlined,
                  iconBg: const Color(0xFF22C55E).withValues(alpha: 0.25),
                  title: e.key,
                  subtitle: 'Internal $internal · Final $external',
                  trailing: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        grade,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: grade == 'F' ? const Color(0xFFF87171) : const Color(0xFF4ADE80),
                        ),
                      ),
                      Text(
                        '$total/100',
                        style: const TextStyle(fontSize: 11, color: StudentPalette.textMuted),
                      ),
                    ],
                  ),
                );
              }),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('PDF download — use admin portal marksheet for now')),
                        );
                      },
                      icon: const Icon(Icons.download, size: 18, color: Color(0xFF4ADE80)),
                      label: const Text('Download PDF', style: TextStyle(color: Color(0xFF4ADE80))),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.share, size: 18, color: Color(0xFF67E8F9)),
                      label: const Text('Share', style: TextStyle(color: Color(0xFF67E8F9))),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _stat(String label, String value) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 11, color: StudentPalette.textMuted)),
          Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: Colors.white)),
        ],
      ),
    );
  }
}
