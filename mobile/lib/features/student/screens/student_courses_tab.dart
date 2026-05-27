import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../widgets/student_ui.dart';

class StudentCoursesTab extends ConsumerWidget {
  const StudentCoursesTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final enrollments = ref.watch(studentEnrollmentsProvider);
    final exams = ref.watch(studentExamsProvider);
    final marks = ref.watch(studentMarksProvider);

    return enrollments.when(
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.mint)),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (list) {
        final examList = exams.valueOrNull ?? [];
        final markList = marks.valueOrNull ?? [];

        if (list.isEmpty) {
          return const Center(
            child: Text('No enrolled courses yet', style: TextStyle(color: StudentPalette.textMuted)),
          );
        }

        var totalPct = 0.0;
        for (final e in list) {
          final cid = e['course'] as int?;
          if (cid != null) totalPct += courseProgressPercent(cid, examList, markList);
        }
        final avg = list.isEmpty ? 0 : totalPct / list.length;

        return RefreshIndicator(
          color: StudentPalette.mint,
          onRefresh: () async {
            ref.invalidate(studentEnrollmentsProvider);
            ref.invalidate(studentExamsProvider);
            ref.invalidate(studentMarksProvider);
          },
          child: ListView(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            children: [
              Row(
                children: [
                  const Expanded(
                    child: Text(
                      'My Courses',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600, color: StudentPalette.textPrimary),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: StudentPalette.mint.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${avg.round()}% avg',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF4ADE80)),
                    ),
                  ),
                ],
              ),
              Text(
                '${list.length} program(s) · progress from published exams',
                style: const TextStyle(fontSize: 12, color: StudentPalette.textMuted),
              ),
              const SizedBox(height: 16),
              ...list.map((e) {
                final cid = e['course'] as int?;
                final name = e['course_name']?.toString() ?? 'Course';
                final code = e['course_code']?.toString() ?? '';
                final pct = cid == null ? 0.0 : courseProgressPercent(cid, examList, markList);
                final done = pct >= 100;
                return StudentDarkRow(
                  icon: Icons.school_outlined,
                  iconBg: _courseColor(pct),
                  title: name,
                  subtitle: code.isEmpty ? '${pct.round()}% complete' : '$code · ${pct.round()}% complete',
                  trailing: done
                      ? const StudentStatusChip('✓', color: Color(0xFF4ADE80), bg: Color(0x3322C55E))
                      : pct == 0
                          ? const StudentStatusChip('—', color: Color(0xFFF87171), bg: Color(0x33EF4444))
                          : null,
                  child: StudentProgressBar(percent: pct, color: _barColor(pct)),
                );
              }),
            ],
          ),
        );
      },
    );
  }

  Color _courseColor(double pct) {
    if (pct >= 100) return const Color(0xFF22C55E).withValues(alpha: 0.35);
    if (pct >= 50) return const Color(0xFF3B82F6).withValues(alpha: 0.35);
    if (pct > 0) return const Color(0xFFF0A500).withValues(alpha: 0.35);
    return StudentPalette.teal.withValues(alpha: 0.25);
  }

  Color _barColor(double pct) {
    if (pct >= 100) return const Color(0xFF22C55E);
    if (pct >= 50) return const Color(0xFF3B82F6);
    if (pct > 0) return const Color(0xFFF0A500);
    return StudentPalette.mint;
  }
}
