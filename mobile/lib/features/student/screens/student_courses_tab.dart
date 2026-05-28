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
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (list) {
        final examList = exams.valueOrNull ?? [];
        final markList = marks.valueOrNull ?? [];

        var totalPct = 0.0;
        for (final e in list) {
          final cid = e['course'] as int?;
          if (cid != null) totalPct += courseProgressPercent(cid, examList, markList);
        }
        final avg = list.isEmpty ? 0.0 : totalPct / list.length;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            StudentNavyHeader(
              title: 'My Courses',
              subtitle: list.isEmpty
                  ? 'No enrollments'
                  : '${list.length} subject(s) · ${avg.round()}% avg progress',
              chips: [
                _chip('All', true),
                _chip('Active', false),
                _chip('Done', false),
              ],
            ),
            Expanded(
              child: list.isEmpty
                  ? const Center(child: Text('No enrolled courses yet', style: TextStyle(color: StudentPalette.textMuted)))
                  : RefreshIndicator(
                      color: StudentPalette.indigo,
                      onRefresh: () async {
                        ref.invalidate(studentEnrollmentsProvider);
                        ref.invalidate(studentExamsProvider);
                        ref.invalidate(studentMarksProvider);
                      },
                      child: ListView(
                        padding: const EdgeInsets.fromLTRB(14, 12, 14, 24),
                        children: list.map((e) {
                          final cid = e['course'] as int?;
                          final name = e['course_name']?.toString() ?? 'Course';
                          final teacher = e['teacher_name']?.toString() ?? 'Faculty';
                          final pct = cid == null ? 0.0 : courseProgressPercent(cid, examList, markList);
                          final done = pct >= 100;
                          final active = pct > 0 && !done;
                          return StudentCourseRow(
                            icon: Icons.menu_book_outlined,
                            iconBg: _iconBg(pct),
                            iconColor: _barColor(pct),
                            title: name,
                            subtitle: '$teacher · ${pct.round()}% complete',
                            pill: done
                                ? const StudentPill('Done', type: StudentPillType.green)
                                : active
                                    ? const StudentPill('Active', type: StudentPillType.blue)
                                    : const StudentPill('Upcoming', type: StudentPillType.gray),
                            percent: pct,
                            barColor: _barColor(pct),
                          );
                        }).toList(),
                      ),
                    ),
            ),
          ],
        );
      },
    );
  }

  Widget _chip(String label, bool on) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.only(right: 4),
        padding: const EdgeInsets.symmetric(vertical: 5),
        decoration: BoxDecoration(
          color: on ? StudentPalette.indigo : Colors.white.withValues(alpha: 0.07),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            color: on ? Colors.white : Colors.white38,
          ),
        ),
      ),
    );
  }

  Color _iconBg(double pct) {
    if (pct >= 100) return StudentPalette.successBg;
    if (pct >= 50) return StudentPalette.infoBg;
    if (pct > 0) return StudentPalette.warningBg;
    return StudentPalette.grayBg;
  }

  Color _barColor(double pct) {
    if (pct >= 100) return StudentPalette.success;
    if (pct >= 50) return StudentPalette.info;
    if (pct > 0) return const Color(0xFFEA580C);
    return StudentPalette.textMuted;
  }
}
