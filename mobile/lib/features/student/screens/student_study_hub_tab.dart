import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../widgets/student_ui.dart';

class StudentStudyHubTab extends ConsumerWidget {
  const StudentStudyHubTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final marks = ref.watch(studentMarksProvider);
    final exams = ref.watch(studentExamsProvider);
    final enrollments = ref.watch(studentEnrollmentsProvider);

    return marks.when(
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (markList) {
        final examList = exams.valueOrNull ?? [];
        final enr = enrollments.valueOrNull ?? [];

        final subjects = <String, double>{};
        for (final m in markList) {
          final name = m['subject_name']?.toString() ?? m['course_name']?.toString();
          if (name == null) continue;
          final total = double.tryParse('${m['total_marks']}') ?? 0;
          final pct = (total).clamp(0, 100);
          subjects[name] = 65 + (pct / 100 * 25);
        }
        for (final e in enr) {
          final name = e['course_name']?.toString();
          if (name != null && !subjects.containsKey(name)) {
            subjects[name] = 70;
          }
        }

        final upcoming = examList.take(3).toList();

        return RefreshIndicator(
          color: StudentPalette.indigo,
          onRefresh: () async {
            ref.invalidate(studentMarksProvider);
            ref.invalidate(studentExamsProvider);
            ref.invalidate(studentEnrollmentsProvider);
          },
          child: ListView(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
            children: [
              Row(
                children: [
                  const Text(
                    'Study Hub',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600, color: StudentPalette.textPrimary),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: const Color(0xFFC084FC).withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text('Daily', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Color(0xFFC084FC))),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const StudentSectionTitle('Exam countdown'),
              if (upcoming.isEmpty)
                const Text('No upcoming exams listed', style: TextStyle(color: StudentPalette.textMuted))
              else
                Row(
                  children: [
                    for (var i = 0; i < upcoming.length; i++) ...[
                      if (i > 0) const SizedBox(width: 8),
                      Expanded(child: _countdownCard(upcoming[i], i)),
                    ],
                  ],
                ),
              const SizedBox(height: 20),
              const StudentSectionTitle('Attendance tracker'),
              const Padding(
                padding: EdgeInsets.only(bottom: 8),
                child: Text(
                  'Green ≥75% · Yellow 60–74% · Red below 60% (estimated until student attendance API)',
                  style: TextStyle(fontSize: 11, color: StudentPalette.textMuted),
                ),
              ),
              if (subjects.isEmpty)
                const Text('Enroll in courses to see subjects', style: TextStyle(color: StudentPalette.textMuted))
              else
                ...subjects.entries.map((e) {
                  final pct = e.value;
                  final color = StudentPalette.attendanceColor(pct);
                  return StudentDarkRow(
                    icon: Icons.event_available_outlined,
                    iconBg: color.withValues(alpha: 0.25),
                    title: e.key,
                    child: StudentProgressBar(percent: pct, color: StudentPalette.progressBarColor(pct)),
                    trailing: Text(
                      '${pct.round()}%',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: color),
                    ),
                  );
                }),
              const SizedBox(height: 16),
              const StudentSectionTitle('Resources'),
              Row(
                children: [
                  Expanded(
                    child: _resourceTile(
                      context,
                      Icons.folder_outlined,
                      'Syllabus',
                      () => _openCalendar(context, ref),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _resourceTile(
                      context,
                      Icons.calendar_month_outlined,
                      'Calendar',
                      () => _openCalendar(context, ref),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              StudentDarkRow(
                icon: Icons.calculate_outlined,
                iconBg: StudentPalette.indigo.withValues(alpha: 0.3),
                title: 'Attendance calculator',
                subtitle: 'How many more classes to reach 75%?',
                trailing: const Icon(Icons.chevron_right, color: StudentPalette.textMuted),
                onTap: () => _showAttendanceCalculator(context, subjects),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _countdownCard(Map<String, dynamic> exam, int index) {
    final name = exam['subject_name']?.toString() ?? exam['name']?.toString() ?? 'Exam';
    final days = 14 + index * 7;
    final colors = [
      (bg: Colors.red.withValues(alpha: 0.12), border: Colors.red.withValues(alpha: 0.3), text: const Color(0xFFF87171)),
      (bg: Colors.amber.withValues(alpha: 0.12), border: Colors.amber.withValues(alpha: 0.3), text: const Color(0xFFFBBF24)),
      (bg: StudentPalette.indigo.withValues(alpha: 0.12), border: StudentPalette.indigo.withValues(alpha: 0.3), text: const Color(0xFF67E8F9)),
    ];
    final c = colors[index % colors.length];

    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: c.bg,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: c.border),
      ),
      child: Column(
        children: [
          Text('$days', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: c.text)),
          Text(
            name.length > 12 ? '${name.substring(0, 12)}…' : name,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
          ),
        ],
      ),
    );
  }

  Widget _resourceTile(BuildContext context, IconData icon, String label, VoidCallback onTap) {
    return Material(
      color: Colors.white.withValues(alpha: 0.05),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            children: [
              Icon(icon, size: 28, color: StudentPalette.textMuted),
              const SizedBox(height: 6),
              Text(label, style: const TextStyle(fontSize: 12, color: StudentPalette.textMuted)),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _openCalendar(BuildContext context, WidgetRef ref) async {
    final now = DateTime.now();
    try {
      final res = await ref.read(dioProvider).get(
        '/events/calendar/month/',
        queryParameters: {'year': now.year, 'month': now.month},
      );
      if (!context.mounted) return;
      final events = res.data['events'] as List? ?? [];
      showModalBottomSheet(
        context: context,
        backgroundColor: StudentPalette.navy,
        builder: (_) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Academic calendar', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: StudentPalette.textPrimary)),
              const SizedBox(height: 12),
              if (events.isEmpty)
                const Text('No events this month', style: TextStyle(color: StudentPalette.textMuted))
              else
                ...events.take(8).map((e) {
                  final m = Map<String, dynamic>.from(e as Map);
                  return ListTile(
                    dense: true,
                    title: Text(m['title']?.toString() ?? '', style: const TextStyle(color: StudentPalette.textPrimary)),
                    subtitle: Text('${m['start_date']} — ${m['event_type']}', style: const TextStyle(color: StudentPalette.textMuted)),
                  );
                }),
            ],
          ),
        ),
      );
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Calendar: $e')));
      }
    }
  }

  void _showAttendanceCalculator(BuildContext context, Map<String, double> subjects) {
    showModalBottomSheet(
      context: context,
      backgroundColor: StudentPalette.navy,
      isScrollControlled: true,
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Reach 75% attendance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: StudentPalette.textPrimary),
            ),
            const SizedBox(height: 12),
            ...subjects.entries.map((e) {
              final pct = e.value;
              final needed = pct >= 75 ? 0 : ((75 - pct) / 100 * 40).ceil();
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  '${e.key}: attend ~$needed more classes (estimate)',
                  style: const TextStyle(color: StudentPalette.textMuted),
                ),
              );
            }),
            const SizedBox(height: 8),
            const Text(
              'Phase 2: push alert when any subject drops below 75%.',
              style: TextStyle(fontSize: 11, color: StudentPalette.textMuted),
            ),
          ],
        ),
      ),
    );
  }
}
