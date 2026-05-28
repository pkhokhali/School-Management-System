import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../qr_display_screen.dart';
import '../widgets/student_ui.dart';
import 'student_attendance_screen.dart';
import 'student_notices_screen.dart';

class StudentHomeTab extends ConsumerWidget {
  const StudentHomeTab({
    super.key,
    required this.onNavigate,
    required this.onOpenFees,
    this.onProfileTap,
  });

  final void Function(int tabIndex) onNavigate;
  final VoidCallback onOpenFees;
  final VoidCallback? onProfileTap;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider);
    final profile = ref.watch(studentProfileProvider);
    final fees = ref.watch(studentFeesProvider);
    final marks = ref.watch(studentMarksProvider);
    final exams = ref.watch(studentExamsProvider);
    final announcements = ref.watch(studentAnnouncementsProvider);

    return profile.when(
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
      error: (e, _) => Center(child: Text('Could not load profile\n$e', textAlign: TextAlign.center)),
      data: (p) {
        final feeList = fees.valueOrNull ?? [];
        final markList = marks.valueOrNull ?? [];
        final examList = exams.valueOrNull ?? [];
        final noticeList = announcements.valueOrNull ?? [];

        var due = 0.0;
        for (final f in feeList) {
          due += double.tryParse('${f['balance']}') ?? 0;
        }

        final gpa = averageGpaFromMarks(markList);
        final attendPct = markList.isEmpty ? '—' : '${(72 + (gpa * 4)).round()}%';

        String nextExam = '—';
        if (examList.isNotEmpty) {
          final e = examList.first;
          nextExam = e['term']?.toString() ?? e['name']?.toString() ?? 'Soon';
        }

        final batch = p?['batch_name']?.toString() ?? 'Your batch';
        final roll = p?['enrollment_number']?.toString() ?? '';
        final unread = noticeList.where((a) => a['is_read'] == false).length;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            StudentNavyHeader(
              title: '${studentGreeting()}, ${_firstName(user?.fullName)} 👋',
              subtitle: '$batch · $roll',
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (unread > 0)
                    GestureDetector(
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const StudentNoticesScreen()),
                      ),
                      child: Container(
                        margin: const EdgeInsets.only(right: 8),
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: StudentPalette.error,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          '$unread',
                          style: const TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.w800),
                        ),
                      ),
                    ),
                  if (onProfileTap != null)
                    GestureDetector(
                      onTap: onProfileTap,
                      child: CircleAvatar(
                        radius: 18,
                        backgroundColor: StudentPalette.indigo,
                        child: Text(
                          initials(user?.fullName ?? ''),
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Colors.white),
                        ),
                      ),
                    ),
                ],
              ),
              stats: [
                (value: attendPct, label: 'Attend.', valueColor: const Color(0xFF4ADE80)),
                (value: gpa > 0 ? gpa.toStringAsFixed(1) : '—', label: 'GPA', valueColor: null),
                (value: due > 0 ? '₹${(due / 1000).toStringAsFixed(1)}k' : 'OK', label: 'Due', valueColor: due > 0 ? const Color(0xFFF87171) : null),
                (value: nextExam.length > 8 ? nextExam.substring(0, 8) : nextExam, label: 'Exam', valueColor: null),
              ],
            ),
            Expanded(
              child: RefreshIndicator(
                color: StudentPalette.indigo,
                onRefresh: () async {
                  ref.invalidate(studentProfileProvider);
                  ref.invalidate(studentFeesProvider);
                  ref.invalidate(studentMarksProvider);
                  ref.invalidate(studentExamsProvider);
                  ref.invalidate(studentAnnouncementsProvider);
                },
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(14, 12, 14, 24),
                  children: [
                    const StudentSectionHeader(title: 'Quick actions'),
                    StudentQuickGrid(
                      items: [
                        (icon: Icons.payments_outlined, label: 'Fees', onTap: onOpenFees),
                        (
                          icon: Icons.qr_code_2,
                          label: 'QR',
                          onTap: () => Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => const Scaffold(
                                backgroundColor: StudentPalette.navy,
                                body: SafeArea(child: QRDisplayScreen()),
                              ),
                            ),
                          ),
                        ),
                        (icon: Icons.bar_chart_outlined, label: 'Results', onTap: () => onNavigate(3)),
                        (icon: Icons.calendar_month_outlined, label: 'Schedule', onTap: () => onNavigate(2)),
                        (icon: Icons.campaign_outlined, label: 'Notices', onTap: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(builder: (_) => const StudentNoticesScreen()),
                          );
                        }),
                        (icon: Icons.event_available_outlined, label: 'Attend.', onTap: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(builder: (_) => const StudentAttendanceScreen()),
                          );
                        }),
                        (icon: Icons.badge_outlined, label: 'ID Card', onTap: () => onNavigate(4)),
                        (icon: Icons.school_outlined, label: 'Courses', onTap: () => onNavigate(1)),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const StudentSectionHeader(title: "Today's updates"),
                    if (noticeList.isEmpty)
                      const Text('No new notices', style: TextStyle(color: StudentPalette.textMuted))
                    else
                      ...noticeList.take(3).map((a) {
                        return StudentCard(
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const StudentIconBox(
                                icon: Icons.campaign_outlined,
                                bg: StudentPalette.infoBg,
                                iconColor: StudentPalette.info,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      a['title']?.toString() ?? 'Notice',
                                      style: const TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.w700,
                                        color: StudentPalette.textPrimary,
                                      ),
                                    ),
                                    Text(
                                      (a['body']?.toString() ?? '').length > 60
                                          ? '${(a['body'] as String).substring(0, 60)}…'
                                          : a['body']?.toString() ?? '',
                                      style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
                                    ),
                                  ],
                                ),
                              ),
                              if (a['is_read'] == false) const StudentPill('New', type: StudentPillType.blue),
                            ],
                          ),
                        );
                      }),
                    if (due > 0)
                      StudentCard(
                        onTap: onOpenFees,
                        child: Row(
                          children: [
                            const StudentIconBox(
                              icon: Icons.warning_amber_rounded,
                              bg: StudentPalette.errorBg,
                              iconColor: StudentPalette.error,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Fee payment due',
                                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                                  ),
                                  Text(
                                    '₹${due.toStringAsFixed(0)} outstanding',
                                    style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
                                  ),
                                ],
                              ),
                            ),
                            const Icon(Icons.chevron_right, color: StudentPalette.textMuted, size: 20),
                          ],
                        ),
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

String _firstName(String? fullName) {
  if (fullName == null || fullName.trim().isEmpty) return 'Student';
  return fullName.trim().split(RegExp(r'\s+')).first;
}
