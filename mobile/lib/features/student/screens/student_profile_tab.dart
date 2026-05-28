import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/providers/theme_provider.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../qr_display_screen.dart';
import '../widgets/student_ui.dart';

class StudentProfileTab extends ConsumerWidget {
  const StudentProfileTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider);
    final dark = ref.watch(darkModeProvider);
    final profile = ref.watch(studentProfileProvider);
    final marks = ref.watch(studentMarksProvider);

    return profile.when(
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (p) {
        final markList = marks.valueOrNull ?? [];
        final gpa = averageGpaFromMarks(markList);
        final name = user?.fullName ?? p?['full_name']?.toString() ?? 'Student';
        final roll = p?['enrollment_number']?.toString() ?? '';
        final batch = p?['batch_name']?.toString() ?? '';

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            StudentNavyHeader(
              title: name,
              subtitle: '$batch · $roll',
              trailing: const StudentPill('Active', type: StudentPillType.green),
            ),
            Expanded(
              child: ListView(
          padding: const EdgeInsets.fromLTRB(14, 12, 14, 24),
          children: [
            StudentCard(
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: StudentPalette.indigo,
                    child: Text(
                      initials(name),
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Colors.white),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: StudentPalette.profileText)),
                        Text('$batch · $roll', style: const TextStyle(fontSize: 12, color: StudentPalette.profileMuted)),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 6,
                          children: [
                            _chip('Active', const Color(0xFFE1F5EE), const Color(0xFF0F6E56)),
                            _chip('Student', const Color(0xFFE6F1FB), const Color(0xFF185FA5)),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            StudentCard(
              child: Row(
                children: [
                  _profileStat('${markList.isEmpty ? "—" : "87%"}', 'Attendance'),
                  _profileStat(gpa > 0 ? gpa.toStringAsFixed(1) : '—', 'GPA'),
                  _profileStat(markList.isNotEmpty ? (markList.first['grade']?.toString() ?? '—') : '—', 'Grade'),
                ],
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'ID CARD & DOCUMENTS',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, letterSpacing: 0.6, color: StudentPalette.profileMuted),
            ),
            const SizedBox(height: 8),
            _docRow(
              Icons.badge_outlined,
              'Digital Student ID',
              'Tap to view or share',
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const Scaffold(body: QRDisplayScreen())),
              ),
            ),
            _docRow(
              Icons.description_outlined,
              'Character Certificate',
              'Request online (Phase 2)',
              onTap: () => _comingSoon(context, 'Certificate requests'),
            ),
            _docRow(
              Icons.article_outlined,
              'Migration Certificate',
              'Apply & track status (Phase 2)',
              onTap: () => _comingSoon(context, 'Certificate requests'),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('Dark mode', style: TextStyle(color: StudentPalette.profileText)),
              subtitle: const Text('Home & tabs use dark theme', style: TextStyle(color: StudentPalette.profileMuted)),
              value: dark,
              activeColor: StudentPalette.indigo,
              onChanged: (_) => ref.read(darkModeProvider.notifier).toggle(),
            ),
            ListTile(
              title: const Text('Server settings', style: TextStyle(color: StudentPalette.profileText)),
              subtitle: Text(user?.email ?? '', style: const TextStyle(color: StudentPalette.profileMuted)),
              trailing: const Icon(Icons.chevron_right, color: StudentPalette.indigo),
              onTap: () => context.push('/profile'),
            ),
            ListTile(
              title: const Text('Logout', style: TextStyle(color: Colors.red)),
              onTap: () async {
                await ref.read(authProvider.notifier).logout();
                if (context.mounted) context.go('/login');
              },
            ),
          ],
        ),
            ),
          ],
        );
      },
    );
  }

  Widget _chip(String t, Color bg, Color fg) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(8)),
      child: Text(t, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: fg)),
    );
  }

  Widget _profileStat(String v, String l) {
    return Expanded(
      child: Column(
        children: [
          Text(v, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: StudentPalette.indigo)),
          Text(l, style: const TextStyle(fontSize: 11, color: StudentPalette.profileMuted)),
        ],
      ),
    );
  }

  Widget _docRow(IconData icon, String title, String sub, {VoidCallback? onTap}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Material(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(10),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              border: Border.all(color: const Color(0xFFE2E8F0)),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                Icon(icon, size: 22, color: StudentPalette.indigo),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: StudentPalette.profileText)),
                      Text(sub, style: const TextStyle(fontSize: 11, color: StudentPalette.profileMuted)),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right, color: StudentPalette.indigo, size: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _comingSoon(BuildContext context, String feature) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$feature — coming in Phase 2')));
  }
}
