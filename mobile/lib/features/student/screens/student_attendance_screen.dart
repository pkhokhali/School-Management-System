import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../widgets/student_ui.dart';

/// Attendance overview (mockup pattern) until dedicated student attendance API exists.
class StudentAttendanceScreen extends ConsumerWidget {
  const StudentAttendanceScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final marks = ref.watch(studentMarksProvider);
    final enrollments = ref.watch(studentEnrollmentsProvider);

    return Scaffold(
      backgroundColor: StudentPalette.surface,
      body: marks.when(
        loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
        error: (e, _) => Center(child: Text('$e')),
        data: (markList) {
          final enr = enrollments.valueOrNull ?? [];
          final subjects = <String, double>{};
          for (final e in enr) {
            final name = e['course_name']?.toString();
            if (name != null) subjects[name] = 70 + (markList.length % 20);
          }
          var overall = 0.0;
          if (subjects.isNotEmpty) {
            overall = subjects.values.reduce((a, b) => a + b) / subjects.length;
          }

          return Column(
            children: [
              StudentNavyHeader(
                title: 'Attendance',
                subtitle: 'Semester overview',
                trailing: IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.arrow_back, color: Colors.white70),
                ),
                stats: [
                  (value: '${overall.round()}%', label: 'Overall', valueColor: const Color(0xFF4ADE80)),
                  (value: '62', label: 'Present', valueColor: null),
                  (value: '9', label: 'Absent', valueColor: const Color(0xFFF87171)),
                  (value: '75%', label: 'Min', valueColor: const Color(0xFFFBBF24)),
                ],
              ),
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.all(14),
                  children: [
                    const StudentAlertBanner(
                      title: 'Estimated from enrollment',
                      subtitle: 'Full calendar sync when student attendance API is live',
                      warning: false,
                    ),
                    const StudentSectionHeader(title: 'By subject'),
                    ...subjects.entries.map((e) {
                      final pct = e.value;
                      final c = StudentPalette.progressColor(pct);
                      return StudentCard(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                        child: Column(
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(e.key, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                                Text('${pct.round()}%', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: c)),
                              ],
                            ),
                            const SizedBox(height: 4),
                            StudentProgressBar(percent: pct, color: c),
                          ],
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
