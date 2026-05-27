import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../qr_display_screen.dart';
import '../widgets/student_ui.dart';

class StudentHomeTab extends ConsumerWidget {
  const StudentHomeTab({super.key, required this.onNavigate, this.onProfileTap});

  final void Function(int tabIndex) onNavigate;
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
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.mint)),
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

        return RefreshIndicator(
          color: StudentPalette.mint,
          onRefresh: () async {
            ref.invalidate(studentProfileProvider);
            ref.invalidate(studentFeesProvider);
            ref.invalidate(studentMarksProvider);
            ref.invalidate(studentExamsProvider);
            ref.invalidate(studentAnnouncementsProvider);
          },
          child: ListView(
            padding: const EdgeInsets.only(bottom: 16),
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 4, 16, 0),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${studentGreeting()}, ${_firstName(user?.fullName)} 👋',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: StudentPalette.textPrimary,
                            ),
                          ),
                          Text(
                            '$batch · $roll',
                            style: const TextStyle(fontSize: 12, color: StudentPalette.textMuted),
                          ),
                        ],
                      ),
                    ),
                    if (noticeList.isNotEmpty)
                      Container(
                        margin: const EdgeInsets.only(right: 6),
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.red.withValues(alpha: 0.8),
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          '${noticeList.length.clamp(1, 9)}',
                          style: const TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                      ),
                    if (onProfileTap != null)
                      IconButton(
                        onPressed: onProfileTap,
                        icon: CircleAvatar(
                          radius: 18,
                          backgroundColor: StudentPalette.mint.withValues(alpha: 0.85),
                          child: Text(
                            initials(user?.fullName ?? ''),
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              StudentHeroCard(
                stats: [
                  (value: attendPct, label: 'Attend.'),
                  (value: gpa > 0 ? gpa.toStringAsFixed(1) : '—', label: 'GPA'),
                  (value: due > 0 ? 'NPR ${(due / 1000).toStringAsFixed(1)}k' : 'OK', label: 'Due'),
                  (value: nextExam.length > 8 ? nextExam.substring(0, 8) : nextExam, label: 'Exam'),
                ],
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: const StudentSectionTitle('Quick actions'),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: GridView.count(
                  crossAxisCount: 2,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 8,
                  crossAxisSpacing: 8,
                  childAspectRatio: 2.4,
                  children: [
                    StudentQuickAction(
                      icon: Icons.payments_outlined,
                      label: 'Pay Fee',
                      onTap: () => onNavigate(2),
                    ),
                    StudentQuickAction(
                      icon: Icons.qr_code_2,
                      label: 'Show QR',
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => const Scaffold(
                            backgroundColor: StudentPalette.bgDark,
                            body: SafeArea(child: QRDisplayScreen()),
                          ),
                        ),
                      ),
                    ),
                    StudentQuickAction(
                      icon: Icons.bar_chart_outlined,
                      label: 'Results',
                      onTap: () => onNavigate(3),
                    ),
                    StudentQuickAction(
                      icon: Icons.calendar_month_outlined,
                      label: 'Study Hub',
                      onTap: () => onNavigate(4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: const StudentSectionTitle("Today's updates"),
              ),
              if (noticeList.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Text('No new notices', style: TextStyle(color: StudentPalette.textMuted)),
                )
              else
                ...noticeList.take(3).map((a) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: StudentDarkRow(
                      icon: Icons.campaign_outlined,
                      iconBg: StudentPalette.teal.withValues(alpha: 0.35),
                      title: a['title']?.toString() ?? 'Notice',
                      subtitle: (a['body']?.toString() ?? '').length > 60
                          ? '${(a['body'] as String).substring(0, 60)}…'
                          : a['body']?.toString(),
                      trailing: a['is_read'] == false
                          ? const StudentStatusChip('New', color: Color(0xFF67E8F9), bg: Color(0x33028090))
                          : null,
                    ),
                  );
                }),
              if (feeList.any((f) => (double.tryParse('${f['balance']}') ?? 0) > 0))
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                  child: StudentDarkRow(
                    icon: Icons.warning_amber_rounded,
                    iconBg: Colors.red.withValues(alpha: 0.25),
                    title: 'Fee payment due',
                    subtitle: 'NPR ${due.toStringAsFixed(0)} outstanding — tap Fees to pay',
                    onTap: () => onNavigate(2),
                    trailing: const Icon(Icons.chevron_right, color: StudentPalette.textMuted),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}

String _firstName(String? fullName) {
  if (fullName == null || fullName.trim().isEmpty) return 'Student';
  return fullName.trim().split(RegExp(r'\s+')).first;
}
